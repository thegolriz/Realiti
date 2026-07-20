import os
import re

import boto3
from better_profanity import profanity
from botocore.config import Config


def moderation_check(s3_object):
    if not s3_object:
        return True
    s3_bucket = os.getenv("S3_BUCKET")
    s3_region = os.getenv("S3_REGION")
    s3_client = boto3.client(
        "s3",
        region_name=s3_region,
        config=Config(signature_version="s3v4"),
    )

    session = boto3.Session()
    client = session.client("rekognition", region_name=s3_region)
    response = client.detect_moderation_labels(
        Image={"S3Object": {"Bucket": s3_bucket, "Name": s3_object}}
    )
    print("Detected labels for " + s3_object)
    for label in response["ModerationLabels"]:
        print(label["Name"] + " : " + str(label["Confidence"]))
        if label["Confidence"] > 70:
            s3_client.delete_object(Bucket=s3_bucket, Key=s3_object)
            return False
        # elif label['Confidence'] > 40 and label['Confidence'] < 70:
        #     return human_review
        print(label["ParentName"])

    return True


LEET_MAP = {
    "@": "a",
    "4": "a",
    "3": "e",
    "1": "i",
    "!": "i",
    "|": "i",
    "0": "o",
    "5": "s",
    "$": "s",
    "7": "t",
    "+": "t",
    "8": "b",
    "6": "g",
    "9": "g",
    "2": "z",
}


def normalize(text):
    leet_trans = str.maketrans(LEET_MAP)
    if text:
        text = text.translate(leet_trans)
    return text


REASON_PROFANITY = "profanity"
REASON_LEETSPEAK = "leetspeak"
REASON_SPACING = "spacing"
REASON_PROMPT_INJECTION = "prompt_injection"

# Patterns that indicate an attempt to manipulate the downstream Claude call
# (claude_text_check) rather than genuine post content. Matched against both
# the raw and leetspeak-normalized text, case-insensitively.
_OVERRIDE_VERBS = r"(?:ignore|disregard|forget)"
_OVERRIDE_SCOPE = (
    r"(?:all\s+|any\s+)?(?:the\s+)?(?:previous|prior|above|preceding|earlier)"
)
_OVERRIDE_TARGET = r"(?:instructions?|prompts?|rules?|context|messages?)"

PROMPT_INJECTION_PATTERNS = [re.compile(p, re.IGNORECASE) for p in (
    # Instruction override / context wipe
    _OVERRIDE_VERBS + r"\s+" + _OVERRIDE_SCOPE + r"\s+" + _OVERRIDE_TARGET,
    r"(?:ignore|disregard)\s+everything\s+(?:above|before|prior)",
    r"new\s+instructions?\b",
    r"override\s+(?:your|the|all)\s+"
    r"(?:instructions?|rules?|guidelines?|restrictions?)",
    r"bypass\s+(?:your|the|all)\s+(?:instructions?|rules?|guidelines?|"
    r"restrictions?|filters?|moderation)",
    r"from\s+now\s+on\s*,?\s+(?:you|ignore|act|respond)",
    # Role / persona hijack
    r"you\s*(?:are|'re)\s+now\s+(?:a|an|in)\b",
    r"act\s+as\s+(?:if\s+you\s+(?:are|were)|a|an)\b",
    r"pretend\s+(?:you\s*(?:are|'re)|to\s+be)\b",
    r"roleplay\s+as\b",
    r"simulate\s+(?:a|an|being)\b",
    r"\bdan\s+mode\b",
    r"do\s+anything\s+now\b",
    r"developer\s+mode\b",
    r"\bjailbreak(?:s|ing|ed)?\b",
    r"(?:no|without\s+any)\s+(?:restrictions?|filters?|limitations?|"
    r"censorship|rules?)\s*(?:apply|now|attached)?",
    # System prompt exfiltration
    r"reveal\s+(?:your|the)\s+(?:system\s+)?prompt",
    r"(?:print|repeat|output|show)\s+(?:your|the)\s+(?:system\s+)?"
    r"(?:prompt|instructions?)",
    r"what\s+(?:are|were)\s+your\s+(?:initial\s+|original\s+)?instructions?",
    # Conversation / role delimiter injection
    r"^\s*(?:system|assistant|human|user)\s*:",
    r"<\|?\s*(?:im_start|im_end|system|endoftext)\s*\|?>",
    r"\[/?(?:inst|system)\]",
    r"###\s*(?:system|instruction)",
    # Trying to coerce a specific moderation outcome
    r"(?:mark|flag|label|approve)\s+this\s+(?:post\s+)?as\s+"
    r"(?:safe|approved|clean|appropriate)",
    r"this\s+(?:post\s+)?(?:is\s+)?(?:not|isn't|isn’t)\s+"
    r"(?:inappropriate|against\s+(?:the\s+)?guidelines)",
    r"(?:always|you\s+must)\s+respond\s+with",
    r"your\s+(?:next\s+)?response\s+must\s+(?:be|say)",
    r"respond\s+only\s+with\s+['\"]",
)]


def _contains_prompt_injection(text):
    return any(pattern.search(text) for pattern in PROMPT_INJECTION_PATTERNS)


# Common English words (length >= 4), derived from a frequency-ranked word
# list (first20hours/google-10000-english, MIT licensed). Used to catch
# leetspeak that disguises an ordinary word ("h3llo", "d0nt") rather than
# profanity, while a price ("$450k") or unit number ("4B") normalizes to
# gibberish and won't match a real word here.
_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
with open(os.path.join(_DATA_DIR, "common_words.txt"), encoding="utf-8") as f:
    COMMON_WORDS = frozenset(line.strip() for line in f if line.strip())

# Tokens may include letters/digits/underscore plus the non-word leetspeak
# symbols, so a word like "h3llo" or "$450k" is captured as one token.
_TOKEN_PATTERN = re.compile(r"[\w@!|$+]+")

_URL_PATTERNS = [re.compile(p, re.IGNORECASE) for p in (
    r"https?://",
    r"www\.[a-z0-9-]+\.[a-z]{2,}",
    r"\b[a-z0-9-]{2,63}\.(?:com|net|org|io|co|biz|info|gov|edu|me|ly|xyz)\b",
)]


def _contains_disguised_word(text):
    for token in _TOKEN_PATTERN.findall(text):
        normalized_token = normalize(token).lower()
        if (
            token.lower() != normalized_token
            and len(normalized_token) >= 4
            and normalized_token.isalpha()
            and normalized_token in COMMON_WORDS
        ):
            return True
    return False


def _contains_disguised_url(normalized):
    return any(pattern.search(normalized) for pattern in _URL_PATTERNS)


def _classify(text):
    if not text:
        return None
    normalized = normalize(text)
    if re.search(r"([a-zA-Z]\s){3,}", normalized):
        return REASON_SPACING
    if _contains_prompt_injection(text) or _contains_prompt_injection(normalized):
        return REASON_PROMPT_INJECTION
    if profanity.contains_profanity(text) or profanity.contains_profanity(normalized):
        # Leetspeak (text relies on substituted characters) is an evasion
        # attempt rather than plainly profane content.
        if text != normalized:
            return REASON_LEETSPEAK
        return REASON_PROFANITY
    # Leetspeak that disguises a non-profane word or a link, rather than
    # profanity, is still an evasion attempt per our content guidelines.
    if text != normalized and (
        _contains_disguised_word(text) or _contains_disguised_url(normalized)
    ):
        return REASON_LEETSPEAK
    return None


def regex_check(title, description):
    """Classify title and description independently.

    Returns a (title_reason, description_reason) tuple so callers can
    surface a distinct, field-specific message for each violation found.

    This is the cheap first screen. Anything it lets through is handed to
    the Claude layer (claudeModeration.run_claude_checks) by the caller.
    """
    title_reason = _classify(title)
    description_reason = _classify(description)
    return title_reason, description_reason
