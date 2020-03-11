import re


def remove_french(text, fr_designation_end_list):
    compound = re.findall(r'[^/]+(?://[^/]*)*', text)
    if len(compound) == 2:
        fr_list_text = [x.lower() for x in compound[1].split(" ") if x]
        if any(item in fr_designation_end_list for item in fr_list_text):
            compound.pop()
            text = ' '.join(map(str, compound))
    return text


def remove_stop_words(original_name, stop_words):
    stop_words_rgx = '|'.join(stop_words)
    regex = re.compile(r'\b({})\b'.format(stop_words_rgx))
    found_stop_words = regex.findall(original_name.lower())

    for word in found_stop_words:
        original_name = original_name.replace(word, "")

    return re.sub(' +', ' ', original_name)