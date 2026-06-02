import json
import re
import os

DICT_PATH = os.path.join(os.path.dirname(__file__), "dictionary.json")


def load_dictionary(path=None):
    path = path or DICT_PATH
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def apply_dictionary(text, dictionary):
    if not dictionary:
        return text
    for word, replacement in dictionary.items():
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        def replacer(match):
            original = match.group()
            if original[0].isupper():
                return replacement[0].upper() + replacement[1:]
            return replacement
        text = pattern.sub(replacer, text)
    return text


def fix_punctuation(text):
    text = re.sub(r"\s{2,}", " ", text)
    sentences = re.split(r"([.!?]\s*)", text)
    result = []
    for i, part in enumerate(sentences):
        if i == 0 or (i > 0 and re.match(r"[.!?]\s*", sentences[i - 1])):
            part = part.lstrip()
            if part:
                part = part[0].upper() + part[1:]
        result.append(part)
    return "".join(result).strip()


def postprocess(text, dictionary=None):
    if dictionary is None:
        dictionary = load_dictionary()
    text = text.strip()
    if not text:
        return text
    text = fix_punctuation(text)
    text = apply_dictionary(text, dictionary)
    return text
