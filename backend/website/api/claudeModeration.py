import base64
import json
import os
from typing import NamedTuple, Optional

import anthropic
import boto3
from botocore.config import Config

# Three possible outcomes per check. Anything that isn't ALLOW keeps the post
# from publishing. REVIEW is the "Claude is unsure" case: too risky to publish,
# not clear enough to hard-block, so it will be routed to the admin dashboard
# for a human decision once that exists.
DECISION_ALLOW = "allow"
DECISION_BLOCK = "block"
DECISION_REVIEW = "needs_review"


class Verdict(NamedTuple):
    decision: str  # one of DECISION_ALLOW / DECISION_BLOCK / DECISION_REVIEW
    # Model-generated explanation of the decision. TODO: decide whether to
    # surface this to the user (on a block) or keep it for the dashboard (on a
    # review), the way postRoutes.MODERATION_MESSAGES maps the regex reasons.
    reason: str


_OK = Verdict(decision=DECISION_ALLOW, reason="")

# One client for the whole module. Do not construct anthropic.Anthropic()
# per call.
_client = anthropic.Anthropic()
_MODEL = "claude-haiku-4-5"

# Structured verdict so responses are always parseable, never free text.
# The enum forces the model into exactly one of the three decisions.
_VERDICT_SCHEMA = {
    "type": "object",
    "properties": {
        "decision": {
            "type": "string",
            "enum": [DECISION_ALLOW, DECISION_BLOCK, DECISION_REVIEW],
        },
        "reason": {"type": "string"},
    },
    "required": ["decision", "reason"],
    "additionalProperties": False,
}

# Map file extension -> (kind, mime). Images and PDFs use different Claude
# content-block types, so the kind decides how _media_block builds the block.
_MEDIA_TYPES = {
    ".png": ("image", "image/png"),
    ".jpg": ("image", "image/jpeg"),
    ".jpeg": ("image", "image/jpeg"),
    ".gif": ("image", "image/gif"),
    ".webp": ("image", "image/webp"),
    ".pdf": ("document", "application/pdf"),
}


# --- system prompts -------------------------------------------------------
# Prompt text lives as .md files in ./prompts so moderation policy can be
# edited as prose without touching this module. Loaded once at import; a
# missing or misnamed file raises here (loud, on purpose) rather than failing
# open per-check. Each prompt must explain the three decisions so the model
# picks the right one: "block" for a clear violation, "allow" when it is
# clearly fine, and "needs_review" when it genuinely cannot tell. Steer
# borderline-but-likely-ok content to "allow" and reserve "needs_review" for
# real uncertainty, or the review queue will fill with false positives.

_PROMPT_DIR = os.path.join(os.path.dirname(__file__), "prompts")


def _load_prompt(name):
    with open(os.path.join(_PROMPT_DIR, name), encoding="utf-8") as f:
        return f.read()


_TITLE_SYSTEM = _load_prompt("title.md")
_DESCRIPTION_SYSTEM = _load_prompt("description.md")
_MEDIA_SYSTEM = _load_prompt("media.md")
_MEDIA_MATCH_SYSTEM = _load_prompt("media_match.md")


# --- shared plumbing ------------------------------------------------------


def _verdict(system, content):
    """Single call site for the API. Returns a Verdict.

    `content` is whatever goes in the user message: a plain string for the
    text checks, or a list of content blocks for the multimodal checks.
    """
    resp = _client.messages.create(
        model=_MODEL,
        max_tokens=1000,
        system=system,
        messages=[{"role": "user", "content": content}],
        output_config={
            "format": {"type": "json_schema", "schema": _VERDICT_SCHEMA}
        },
    )
    # With output_config the model returns the JSON verdict in a text block.
    text = next(
        (b.text for b in resp.content if b.type == "text"), None
    )
    if text is None:
        raise ValueError("no text block in Claude moderation response")
    data = json.loads(text)
    return Verdict(decision=data["decision"], reason=data.get("reason", ""))


def _media_kind(s3_object):
    """Return (kind, mime) for an S3 key, or (None, None) if unsupported."""
    _, ext = os.path.splitext(s3_object.lower())
    return _MEDIA_TYPES.get(ext, (None, None))


def _fetch_s3_bytes(s3_object):
    """Download the object so its bytes can be sent to Claude. Rekognition
    reads straight from S3, but the Anthropic API needs the actual data."""
    s3_client = boto3.client(
        "s3",
        region_name=os.getenv("S3_REGION"),
        config=Config(signature_version="s3v4"),
    )
    obj = s3_client.get_object(
        Bucket=os.getenv("S3_BUCKET"), Key=s3_object
    )
    return obj["Body"].read()


def _media_block(s3_object):
    """Build the image or document content block for a stored object.

    Returns None if the object type isn't one we send to Claude.
    """
    kind, mime = _media_kind(s3_object)
    if kind is None:
        return None
    data_b64 = base64.standard_b64encode(_fetch_s3_bytes(s3_object)).decode()
    source = {"type": "base64", "media_type": mime, "data": data_b64}
    if kind == "image":
        return {"type": "image", "source": source}
    return {"type": "document", "source": source}


# --- public checks --------------------------------------------------------
# Called from postRoutes.post_api after the regex and Rekognition screens.


def check_title(title):
    if not title:
        return _OK
    try:
        content = f"<title>\n{title}\n</title>"
        return _verdict(_TITLE_SYSTEM, content)
    except Exception as exc:  # noqa: BLE001 - fail open, never block a post
        print(f"check_title failed: {exc}")
        return _OK


def check_description(description):
    if not description:
        return _OK
    try:
        content = f"<description>\n{description}\n</description>"
        return _verdict(_DESCRIPTION_SYSTEM, content)
    except Exception as exc:  # noqa: BLE001 - fail open, never block a post
        print(f"check_description failed: {exc}")
        return _OK


def check_media(s3_object):
    if not s3_object:
        return _OK
    try:
        block = _media_block(s3_object)
        if block is None:
            return _OK
        content = [
            block,
            {
                "type": "text",
                "text": "Classify the attached media per your instructions.",
            },
        ]
        return _verdict(_MEDIA_SYSTEM, content)
    except Exception as exc:  # noqa: BLE001 - fail open, never block a post
        print(f"check_media failed: {exc}")
        return _OK


def check_media_matches_description(s3_object, description):
    """The cross-check: is the media actually consistent with the
    description, or is one of them nonsense relative to the other."""
    if not s3_object or not description:
        return _OK
    try:
        block = _media_block(s3_object)
        if block is None:
            return _OK
        content = [
            block,
            {
                "type": "text",
                "text": (
                    "Decide whether the attached media supports this "
                    f"description:\n<description>\n{description}\n</description>"
                ),
            },
        ]
        return _verdict(_MEDIA_MATCH_SYSTEM, content)
    except Exception as exc:  # noqa: BLE001 - fail open, never block a post
        print(f"check_media_matches_description failed: {exc}")
        return _OK


def run_claude_checks(title, description, s3_object) -> Optional[Verdict]:
    """Run the Claude layer in order and return a single Verdict, or None if
    every check allows the post.

    Order: text (title, description) -> media -> media-vs-description.
    Assumes the regex and Rekognition screens have already passed.

    A BLOCK is terminal and returned immediately. A REVIEW is remembered but
    does not stop the run, because a later check could still be a hard BLOCK,
    which outranks it. If nothing blocks, the first REVIEW (if any) is
    returned.
    """
    # Wrapped in lambdas so a BLOCK short-circuits the remaining API calls
    # instead of running all four up front.
    checks = (
        lambda: check_title(title),
        lambda: check_description(description),
        lambda: check_media(s3_object),
        lambda: check_media_matches_description(s3_object, description),
    )
    review = None
    for check in checks:
        verdict = check()
        if verdict.decision == DECISION_BLOCK:
            return verdict
        if verdict.decision == DECISION_REVIEW and review is None:
            review = verdict
    return review
