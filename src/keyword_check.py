"""
keyword_check.py

WHAT THIS FILE DOES:
Takes a piece of text (a transcript) and checks if it contains
any distress-related words - in English AND Hindi (written in
Roman/English letters, since that's how most Indians text/speak
when using English keyboards - e.g. "bachao" not "बचाओ").

Returns True/False, plus WHICH words matched (so we can show/explain
our decision later - this is the "explainability" judges care about).
"""

# Distress keyword list - English
ENGLISH_KEYWORDS = [
    "help", "help me", "stop", "stop it", "please stop", "let go",
    "leave me", "leave me alone", "someone help", "call police",
    "don't touch me", "get away", "no", "please no", "save me",
]

# Distress keyword list - Hindi (written in Roman letters, as people
# commonly type/say them, since a phone's speech-to-text will output
# Hindi words this way when spoken in Hinglish)
HINDI_KEYWORDS = [
    "bachao",       # save me / help
    "madad",        # help
    "madad karo",   # help me
    "chodo",        # let go
    "chhodo",       # let go (alt spelling)
    "hato",         # get away
    "police bulao", # call the police
    "koi hai",      # is anyone there
    "roko",         # stop
    "mat karo",     # don't do it
]

ALL_KEYWORDS = ENGLISH_KEYWORDS + HINDI_KEYWORDS


def check_keywords(text):
    """
    Takes a transcript (string), returns:
      - found: True/False whether any distress keyword was found
      - matched_words: list of which keywords matched (for explainability)
    """
    text_lower = text.lower().strip()
    matched_words = []

    for keyword in ALL_KEYWORDS:
        if keyword in text_lower:
            matched_words.append(keyword)

    found = len(matched_words) > 0
    return found, matched_words


if __name__ == "__main__":
    # Quick manual test with example sentences (since our real dataset
    # doesn't contain any distress words - see explanation above)
    test_sentences = [
        "kids are talking by the door",          # normal (from our dataset)
        "please help me someone stop",           # distress example
        "hey what time is it",                   # normal
        "bachao madad karo please",              # distress example (Hindi)
        "dogs are sitting by the door",          # normal (from our dataset)
        "chodo mujhe hato",                      # distress example (Hindi)
    ]

    print("--- Testing keyword_check.py with example sentences ---\n")
    for sentence in test_sentences:
        found, matched = check_keywords(sentence)
        status = "DISTRESS WORDS FOUND" if found else "no distress words"
        print(f"'{sentence}'")
        print(f"   -> {status}   (matched: {matched})\n")
