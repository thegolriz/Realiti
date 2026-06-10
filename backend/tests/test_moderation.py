from website.api.moderationRoute import moderation_check, normalize, regex_check

# --- normalize ---


def test_normalize_leet_substitutions():
    assert normalize("h3ll0") == "hello"


def test_normalize_all_mapped_chars():
    assert normalize("@413!|0$5+86927") == "aaieiiosstbggzt"


def test_normalize_mixed_case_unchanged():
    result = normalize("Hello World")
    assert result == "Hello World"


def test_normalize_empty_string():
    assert normalize("") == ""


def test_normalize_none_returns_none():
    assert normalize(None) is None


# --- regex_check ---


def test_regex_check_clean_with_title():
    assert regex_check("Nice photo", "A great sunset") is True


def test_regex_check_clean_no_title():
    assert regex_check(None, "A great sunset") is True


def test_regex_check_profanity_in_title():
    assert regex_check("shit post", "clean description") is False


def test_regex_check_profanity_in_description():
    assert regex_check("clean title", "this is shit") is False


def test_regex_check_profanity_no_title():
    assert regex_check(None, "this is shit") is False


def test_regex_check_leet_profanity_in_title():
    # "5h1t" normalizes to "shit"
    assert regex_check("5h1t post", "clean description") is False


def test_regex_check_leet_profanity_in_description():
    assert regex_check("clean title", "5h1t content") is False


def test_regex_check_spaced_letters_in_title():
    assert regex_check("a b c d", "clean description") is False


def test_regex_check_spaced_letters_in_description():
    assert regex_check("clean title", "s p a m content") is False


def test_regex_check_spaced_letters_no_title():
    assert regex_check(None, "s p a m") is False


def test_regex_check_two_spaced_letters_allowed():
    # pattern requires 3+ consecutive "letter space" — two should pass
    assert regex_check("a b clean", "normal description") is True


# --- moderation_check early return ---


def test_moderation_check_none_returns_true():
    assert moderation_check(None) is True


def test_moderation_check_empty_string_returns_true():
    assert moderation_check("") is True
