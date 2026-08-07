"""Unit tests for the Claude moderation layer (claudeModeration)."""

from types import SimpleNamespace
from unittest import mock

import pytest

from website.api import claudeModeration as cm
from website.api.claudeModeration import (
    DECISION_ALLOW,
    DECISION_BLOCK,
    DECISION_REVIEW,
    Verdict,
    run_claude_checks,
)


def allow():
    return Verdict(DECISION_ALLOW, "")


def block(r="nope"):
    return Verdict(DECISION_BLOCK, r)


def review(r="hmmm"):
    return Verdict(DECISION_REVIEW, r)


@pytest.fixture
def stub_checks(monkeypatch):
    """Swap the four Claude checks for canned verdicts and record run order.
    Returns (set_verdicts, calls); default every check to ALLOW."""
    calls = []

    def make(name, verdict):
        def fake(*args, **kwargs):
            calls.append(name)
            return verdict

        return fake

    def set_verdicts(title=None, description=None, media=None, match=None):
        monkeypatch.setattr(cm, "check_title", make("title", title or allow()))
        monkeypatch.setattr(
            cm, "check_description", make("description", description or allow())
        )
        monkeypatch.setattr(cm, "check_media", make("media", media or allow()))
        monkeypatch.setattr(
            cm, "check_media_matches_description", make("match", match or allow())
        )

    return set_verdicts, calls


def test_all_allow_returns_none(stub_checks):
    set_verdicts, calls = stub_checks
    set_verdicts()  # all ALLOW
    assert run_claude_checks("t", "d", "k.png") is None
    assert calls == ["title", "description", "media", "match"]


def test_block_short_circuits(stub_checks):
    set_verdicts, calls = stub_checks
    set_verdicts(title=block("bad title"))
    v = run_claude_checks("t", "d", "k.png")
    assert v.decision == DECISION_BLOCK and v.reason == "bad title"
    assert calls == ["title"]  # nothing after title ran


def test_block_outranks_earlier_review(stub_checks):
    set_verdicts, calls = stub_checks
    set_verdicts(title=review(), media=block("bad media"))
    v = run_claude_checks("t", "d", "k.png")
    assert v.decision == DECISION_BLOCK and v.reason == "bad media"
    assert calls == ["title", "description", "media"]  # match never ran


def test_first_review_returned_when_no_block(stub_checks):
    set_verdicts, calls = stub_checks
    set_verdicts(description=review("hold it"))
    v = run_claude_checks("t", "d", "k.png")
    assert v.decision == DECISION_REVIEW and v.reason == "hold it"
    assert calls == ["title", "description", "media", "match"]


CHECK_IDS = ["title", "description", "media", "match"]

# (check, non-empty args) — reaches _verdict. Media checks need _media_block
# stubbed (see stub_media_block) since they hit S3 before _verdict.
NONEMPTY_CASES = [
    (cm.check_title, ("Title",)),
    (cm.check_description, ("Desc",)),
    (cm.check_media, ("photo.png",)),
    (cm.check_media_matches_description, ("photo.png", "Desc")),
]

# (check, args with a required field empty) — trips the guard before _verdict.
EMPTY_CASES = [
    (cm.check_title, ("",)),
    (cm.check_description, ("",)),
    (cm.check_media, ("",)),
    (cm.check_media_matches_description, ("", "Desc")),
]


@pytest.fixture
def stub_media_block(monkeypatch):
    # Keep the media checks off S3 so they reach _verdict like the text checks.
    monkeypatch.setattr(cm, "_media_block", lambda *a, **k: {"stub": "block"})


@pytest.mark.parametrize("check, args", EMPTY_CASES, ids=CHECK_IDS)
def test_guard_skips_verdict(monkeypatch, check, args):
    spy = mock.Mock()
    monkeypatch.setattr(cm, "_verdict", spy)
    result = check(*args)
    spy.assert_not_called()
    assert result == cm._OK


@pytest.mark.parametrize("check, args", NONEMPTY_CASES, ids=CHECK_IDS)
def test_nonempty_reaches_verdict(monkeypatch, stub_media_block, check, args):
    spy = mock.Mock()
    monkeypatch.setattr(cm, "_verdict", spy)
    check(*args)
    spy.assert_called_once()


@pytest.mark.parametrize("check, args", NONEMPTY_CASES, ids=CHECK_IDS)
def test_check_fails_open(monkeypatch, stub_media_block, check, args):
    spy = mock.Mock(side_effect=Exception("boom"))
    monkeypatch.setattr(cm, "_verdict", spy)
    result = check(*args)
    spy.assert_called_once()
    assert result == cm._OK


# --- _verdict parsing: mock the API response, not _verdict itself ---


def _text_block(text):
    return SimpleNamespace(type="text", text=text)


def _stub_response(monkeypatch, *blocks):
    """Make _client.messages.create return a fake response with these blocks."""
    resp = SimpleNamespace(content=list(blocks))
    fake_client = SimpleNamespace(
        messages=SimpleNamespace(create=lambda **kwargs: resp)
    )
    monkeypatch.setattr(cm, "_client", fake_client)


def test_verdict_parses_decision_and_reason(monkeypatch):
    # A non-text block first proves _verdict skips past it to find the text.
    _stub_response(
        monkeypatch,
        SimpleNamespace(type="tool_use"),
        _text_block('{"decision": "block", "reason": "nope"}'),
    )
    assert cm._verdict("system", "content") == Verdict(DECISION_BLOCK, "nope")


def test_verdict_defaults_missing_reason(monkeypatch):
    _stub_response(monkeypatch, _text_block('{"decision": "allow"}'))
    assert cm._verdict("system", "content") == Verdict(DECISION_ALLOW, "")


def test_verdict_no_text_block_raises(monkeypatch):
    _stub_response(monkeypatch, SimpleNamespace(type="tool_use"))
    with pytest.raises(ValueError):
        cm._verdict("system", "content")
