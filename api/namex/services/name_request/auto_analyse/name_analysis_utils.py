import itertools
import re
import collections
from sqlalchemy import create_engine
from toolz import unique

from namex.services.name_request.auto_analyse import DataFrameFields


# TODO: Fix caps and stuff...
def data_frame_to_list(df):
    df_dist = df.loc[df.word_classification == DataFrameFields.DISTINCTIVE.value]
    df_desc = df.loc[df.word_classification == DataFrameFields.DESCRIPTIVE.value]
    df_none = df.loc[df.word_classification == DataFrameFields.UNCLASSIFIED.value]

    list_dist = list(df_dist.word)
    list_desc = list(df_desc.word)
    list_none = list(df_none.word)

    return list_dist, list_desc, list_none


def get_dataframe_list(df, field):
    return df[field].str.split(',').tolist()


def get_flat_list(lst):
    subs_list = [item for sublist in lst for item in sublist]
    return [x.strip() for x in subs_list]
    # return subs_list


# TODO: What is going on here? Why the change?
'''
def remove_french(text, fr_designation_end_list):
    compound = re.findall(r'[^/]+(?://[^/]*)*', text)
    if len(compound) == 2:
        fr_list_text = [x.lower() for x in compound[1].split(" ") if x]
        if any(item in fr_designation_end_list for item in fr_list_text):
            compound.pop()
            text = ' '.join(map(str, compound))
    return text
'''


def remove_french(text):
    text = re.sub(r'/([A-Za-z]+(?:[^[A-Za-z]\n]+[A-Za-z]+)+[^[A-Za-z]\n]*$)?',
                  ' ',
                  text,
                  0,
                  re.IGNORECASE)
    return text


def remove_stop_words(original_name, stop_words):
    stop_words_rgx = '|'.join(stop_words)
    regex = re.compile(r'\b({})\b'.format(stop_words_rgx))
    found_stop_words = regex.findall(original_name.lower())

    for word in found_stop_words:
        original_name = original_name.replace(word, "")

    return re.sub(' +', ' ', original_name)


def list_distinctive_descriptive_same(name_list):
    queue = collections.deque(name_list)
    dist_list = []
    desc_list = []

    while 1 < len(queue):
        queue.pop()
        dist_list.append(list(queue))
    dist_list.reverse()

    for dist in dist_list:
        desc_list.append([i for i in name_list if i not in dist])

    return dist_list, desc_list


def validate_distinctive_descriptive_lists(list_name, list_dist, list_desc):
    current_category = None
    list_dist_tmp = []
    list_desc_tmp = []
    list_incorrect_classification = []
    for idx, token_name, has_more in lookahead(list_name):
        if idx == 0:
            current_category = None
        if ((token_name in list_dist and token_name in list_desc) or (
                token_name not in list_dist and token_name not in list_desc)) and has_more and (
                current_category is None):
            list_dist_tmp.extend([token_name])
            current_category = DataFrameFields.DISTINCTIVE.value
        elif ((token_name in list_dist and token_name in list_desc) or (
                token_name not in list_dist and token_name not in list_desc)) and has_more and (
                current_category == DataFrameFields.DISTINCTIVE.value):
            list_dist_tmp.extend([token_name])
            list_desc_tmp.extend([token_name])
            current_category = DataFrameFields.DISTINCTIVE.value
        elif ((token_name in list_dist and token_name in list_desc) or (
                token_name not in list_dist and token_name not in list_desc)) and has_more and (
                current_category is None or current_category == DataFrameFields.DESCRIPTIVE.value):
            list_desc_tmp.extend([token_name])
            current_category = DataFrameFields.DESCRIPTIVE.value
        elif token_name in list_dist and token_name not in list_desc and (
                current_category is None or current_category == DataFrameFields.DISTINCTIVE.value) and has_more:
            current_category = DataFrameFields.DISTINCTIVE.value
            list_dist_tmp.extend([token_name])
        elif token_name in list_desc and (
                current_category == DataFrameFields.DISTINCTIVE.value or current_category == DataFrameFields.DESCRIPTIVE.value):
            current_category = DataFrameFields.DESCRIPTIVE.value
            list_desc_tmp.extend([token_name])
        else:
            list_incorrect_classification.append({token_name: idx})
            # break

    return list_dist_tmp, list_desc_tmp, list_incorrect_classification


def list_distinctive_descriptive(name_list, dist_list, desc_list):
    queue_dist = collections.deque(dist_list)

    if dist_list == name_list:
        queue_dist.pop()

    dist_list_all = []
    desc_list_all = []

    dist_list_all.append(list(queue_dist))

    # TODO: Arturo why the change?
    '''
    while len(queue_dist) > 1:
        queue_dist.pop()
        dist_list_all.append(list(queue_dist))

    dist = map(list, unique(map(tuple, dist_list_all)))
    dist_list_all = list(dist)
    dist_list_all.reverse()
    '''

    for dist in dist_list_all:
        desc_list_all.append([i for i in name_list if i not in dist])

    # TODO: Arturo why the change?
    '''
    flatten_desc = [item for sublist in desc_list_all for item in sublist]
    flatten_desc = list(set(flatten_desc))
    if flatten_desc.sort() != desc_list.sort():
        raise Exception('Invalid generated descriptive list.')
    '''
    return dist_list_all, desc_list_all


def lookahead(iterable):
    """Pass through all values from the given iterable, augmented by the
    information if there are more values to come after the current one
    (True), or if it is the last value (False).
    """
    # Get an iterator and pull the first value.
    it = iter(iterable)
    last = next(it)
    # Run the iterator to exhaustion (starting from the second value).
    idx = 0
    for idx, val in enumerate(it):
        # Report the *previous* value (more to come).
        yield idx, last, True
        last = val
    # Report the last value.
    yield idx + 1, last, False
