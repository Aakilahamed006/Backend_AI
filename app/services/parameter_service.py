import re


def extract_parameters(question: str):

    matches = re.search(r"\[(.*?)\]", question)

    if not matches:
        return {}

    raw_text = matches.group(1)

    pairs = raw_text.split(",")

    data = {}

    for pair in pairs:

        key, value = pair.split("=")

        data[key.strip()] = value.strip()

    return data