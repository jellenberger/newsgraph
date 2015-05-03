import sys
import re
import random
import pickle
import gzip
import csv
import codecs
from collections import Counter
import nltk
from nltk.util import ngrams

#from xml.etree.ElementTree import iterparse
#from html import unescape
import textutils as tu



def clean_headline(s):
    s = re.sub(r'SERVICE ALERT ?-', '', s)
    s = tu.asciichars(s)
    s = s.replace('...', '')
    # TODO need same dash treatment as tweet processer?
    return s.lower().strip()


def get_phrasetags(phrase):
    taggedphrase = nltk.pos_tag(nltk.word_tokenize(phrase))
    phrasetags = [token[1] for token in taggedphrase]
    return phrasetags

def calc_ngramcounts(wordlists, n):
    ngramcounts = Counter() 
    for wordlist in wordlists:
        for ngram in ngrams(wordlist, n):
            ngramcounts[ngram] += 1
    return ngramcounts


def read_headlines():
    fname = 'data/headlines.csv.gz'
    with gzip.open(fname, 'r') as f:
        rdr = csv.reader(codecs.iterdecode(f, 'latin-1'))
        for line in rdr:
            if line:
                yield line


def main():
    n = 4
    verbtags = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
    print('Reading headlines.')
    headline_reader = read_headlines()
    for _ in range(100):
        phrase = next(headline_reader)[1]
        tags = get_phrasetags(phrase)
        phraseverbs = [tag for tag in tags if tag in verbtags]
        if phraseverbs and len(tags) >= 8:
            print(phrase)


if __name__ == "__main__":
    sys.exit(main())


# Notes
'''
english_vocab = set(w.lower() for w in nltk.corpus.words.words())
text_vocab = set(w.lower() for w in text if w.lower().isalpha())
unusual = text_vocab.difference(english_vocab) 
'''
