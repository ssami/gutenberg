# coding: utf-8

# Validations to be done:
# 1. Is the text in English?  (WIP - need to learn more RDF)
# 2. Is publish date present? (no publish date: inferring from birth/death)
# 3. Is publish date > 0
#
# Data prep:
# 1. Divide dates into buckets: 10, 50, 100 years
# 2. Download data and store in files for each bucket


import rdflib
import re
import codecs
import os
import math


def _create_map(file_path, file_num):
    g = rdflib.Graph()
    g.parse(file_path, 'rdf')
    #     # grab language
    #     lang_pred = rdflib.URIRef('http://purl.org/dc/terms/language')
    #     print(lang_pred)
    #     lang_obj = [i for i in g.objects(None, lang_pred)]
    #     print(lang_obj)
    #     lang = lang_obj[0] if len(lang_obj) > 0 else None
    #     print(lang)
    #     if (not lang or str(lang) is not 'en'):
    #         return None, None
    # estimate publish date from author's birth/death
    ## grab birth date
    birth_pred = rdflib.URIRef('http://www.gutenberg.org/2009/pgterms/birthdate')
    birth_obj = [i for i in g.objects(None, birth_pred)]
    birth = birth_obj[0] if len(birth_obj) > 0 else None
    # @ grab death date
    death_pred = rdflib.URIRef('http://www.gutenberg.org/2009/pgterms/deathdate')
    death_obj = [i for i in g.objects(None, death_pred)]
    death = death_obj[0] if (len(death_obj) > 0 and birth is not None) else None
    estimated_publish = None
    ## estimate publish date
    if death and birth:
        estimated_publish = str((int(death) + int(birth)) / 2)
    # grab uri for text
    format_pred = rdflib.URIRef('http://purl.org/dc/terms/hasFormat')
    subj = rdflib.URIRef('http://www.gutenberg.org/ebooks/{}'.format(file_num))
    fmt_link = g.objects(subj, format_pred)
    for i in fmt_link:
        if 'txt' in i:  # grab the first text url
            return (str(i), estimated_publish)


def _download_raw_text(url, output_path, max_content=50000, block_size=1024):
    import requests
    stream = requests.get(url, stream=True)
    with open(output_path, 'wb') as fh:
        count = 0
        for block in stream.iter_content(block_size):
            fh.write(block)
            count += block_size
            if count > max_content:
                break


def download_raw_text(url_map, total_size):
    print("Downloading raw text of size {0}".format(total_size))
    train_map = {}
    count = 0
    for idx, data in url_map.items():
        if data:
            url, publish = data
            if publish:
                count += 1
                dl_path = idx + '.txt'
                _download_raw_text(url, dl_path)
                train_map[idx] = (dl_path, publish)
    print("Total valid data = " + str(count))
    print("% valid of original data = " + str(count / total_size))
    return train_map


def _clean_up(text):
    text = text.replace('\r', ' ').replace('\n', ' ')
    return text


def _blob_text(file_path, read_start_line=80, byte_num=500):
    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)
    with(codecs.open(file_path, 'r', encoding='utf-8')) as fh:
        #         if len(list(fh)) < (read_start_line * 2):
        #             return None
        line = None
        count = 0
        while count < read_start_line:
            try:
                fh.readline()
            except:
                # got tired of handling utf-8 issues
                return None
            count += 1
        try:
            data = fh.read(byte_num)
        except:
            # got tired of handling utf-8 issues
            return None
        return _clean_up(data)


def _get_pub_label(pub_date, start_year=1500, end_year=2020, gap_years=20):
    """
    given the start year, the end year, the gap_years
    and the publish date, get the label
    """
    if pub_date < start_year or pub_date > end_year:
        print("publish date {0} is not between {1} and {2}"
              .format(pub_date, start_year, end_year))
        return None
    label = math.floor((pub_date - start_year) / gap_years)
    return label


def format_data(output_file, data_map):
    print("Formatting data for {0}".format(output_file))
    wr = codecs.open(output_file, 'w', encoding='utf-8')
    count = 0
    for idx, fle_dat in data_map.items():
        path, publish = fle_dat
        text = _blob_text(path)
        if text:
            pub_label = _get_pub_label(float(publish))
            if pub_label:
                labeled_line = '__label__' + str(pub_label) + ',' + text + '\n'
                wr.write(labeled_line)
                count += 1
    print("Actual data sample size: " + str(count))
    wr.close()


# Create training and testing data


# define train and test
import random, os

INPUT_TRAIN_SIZE = 300
INPUT_TEST_SIZE = 100
path_prefix = '/Users/ssami/Documents/Personal/cache/epub'
all_texts = os.listdir(path_prefix)
random.shuffle(all_texts)
sample_input_train = all_texts[:INPUT_TRAIN_SIZE]
sample_input_test = all_texts[INPUT_TRAIN_SIZE + 1:INPUT_TRAIN_SIZE + 1 + INPUT_TEST_SIZE]


def build_data(path_prefix,
               sample_input_list,
               size=INPUT_TRAIN_SIZE):
    """

    """
    file_map = {}
    for i in sample_input_list:
        file_path = os.path.join(path_prefix, i, 'pg' + i + '.rdf')
        file_map[i] = _create_map(file_path, i)
    text_map = download_raw_text(file_map, size)  # raw map of publish date to text
    return text_map


# build random training data
train_map = build_data(path_prefix, sample_input_train)

format_data('train.txt', train_map)

# build random testing data
test_map = build_data(path_prefix, sample_input_test, INPUT_TEST_SIZE)

format_data('test.txt', test_map)

