import sys
import re
import random
import pickle
from collections import Counter
import nltk
from nltk.util import ngrams

from xml.etree.ElementTree import iterparse
from html import unescape
import textutils as tu



def clean_ns_headline(s):
    s = re.sub(r'(<!--.*?-->|<[^>]*>)', '', s)
    s = re.sub(r' #(\d+);', r'&#\1;', s)
    s = s.replace(' nbsp;', '&nbsp;')
    s = s.replace(' quot;', '&quot;')
    s = s.replace(' amp;', '&amp;')
    s = unescape(s)
    s = s.replace('\\', '')
    s = tu.asciichars(s)
    s = s.replace('...', '')
    # TODO need same dash treatment as tweet processer?
    return s.lower().strip()


def get_phrasetags(phrases):
    phrasetags = []
    for phrase in phrases:
        taggedphrase = nltk.pos_tag(nltk.word_tokenize(phrase))
        tags = tuple(t[1] for t in taggedphrase)
        phrasetags.append(tags)
    return phrasetags


def calc_ngramcounts(wordlists, n):
    ngramcounts = Counter() 
    for wordlist in wordlists:
        for ngram in ngrams(wordlist, n):
            ngramcounts[ngram] += 1
    return ngramcounts


def read_headlines():
    fname = 'data/newsspace200.xml'
    doc = iterparse(fname)
    headlines = []
    for event, elem in doc:
        if elem.tag == 'title':
            headline = elem.text
            if headline is not None:
                headline = clean_ns_headline(headline)
                headlines.append(headline)
    return headlines


def main():
    print('Reading headlines.')
    headlines = read_headlines()[:5]
    print(len(headlines), 'headlines read.')
    print('Tagging headlines.')
    headlinetags = get_phrasetags(headlines)
    print(len(headlinetags), 'headlines tagged.')
    print('Counting n-grams')
    ngramcounts = calc_ngramcounts(headlinetags, 3)
    #from pprint import pprint
    #pprint(ngramcounts)
    print('Counted', len(ngramcounts), 'unique n-grams.')
    print(ngramcounts, type(ngramcounts), len(ngramcounts))
    with open('data/posmodel.pickle', 'wb') as f:
        pickle.dump(ngramcounts, f)


if __name__ == "__main__":
    sys.exit(main())


# Notes
'''
english_vocab = set(w.lower() for w in nltk.corpus.words.words())
text_vocab = set(w.lower() for w in text if w.lower().isalpha())
unusual = text_vocab.difference(english_vocab) 
'''
