import sys
import re
import random
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
    return s.lower().strip()


def get_postags(phrase):
    taggedlist = nltk.pos_tag(nltk.word_tokenize(phrase))
    return [t[1] for t in taggedlist]


def read_ns_headlinedata():
    fname = 'data/newsspace200.xml'
    doc = iterparse(fname)
    headlines = []
    for event, elem in doc:
        if elem.tag == 'title':
            headline = elem.text
            if headline is not None:
                headline = clean_ns_headline(headline)
                postags = get_postags(headline)
                posngrams = ngrams(postags, 4)
                print(list(posngrams), '\n')



def main():
    read_ns_headlinedata()



if __name__ == "__main__":
    sys.exit(main())


# Notes
'''
english_vocab = set(w.lower() for w in nltk.corpus.words.words())
text_vocab = set(w.lower() for w in text if w.lower().isalpha())
unusual = text_vocab.difference(english_vocab) 
'''
