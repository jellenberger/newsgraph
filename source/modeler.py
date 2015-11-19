import sys
import re
import pickle
import gzip
import csv
import codecs
from collections import Counter
import nltk
from nltk.util import ngrams
import textutils as tu



def clean_headline(s):
    # strippunc is result of ''.join(set(string.punctuation) - {"'", '"', "!", ".", "?"})
    strippunc = '#)(+*-,/=<>@[]\\_^`{}|~'
    s = tu.asciichars(s)
    s = s.replace('...', '')
    s = re.sub(r'[-:] ?[\w]+( [\w]+){0,2}$', '', s)
    s = re.sub(r'(update|wrapup) ?\d* ?[-:] ?', '', s) # possible duplicates?
    s = re.sub(r' ?(cricket|tennis|soccer|golf|football|basketball|baseball) ?-', '', s)
    s = re.sub(r' +', ' ', s)
    s = s.lower().strip(strippunc + ' ') 
    return s


def isjunk(s):
    if (
            re.search(r'^[\w]+( [\w]+){0,2} ?[-:]', s) or # 1-3 words plus - or : at beginning
            re.search(r'^\([\w]+( [\w]+){0,2} ?\)', s) or # 1-3 word parenthetical at beginning
            re.search(r'<(\w+)?(\.\w+)?>', s) or # stock id in tag
            re.search(r'\([\w]+;[\w]+\)', s) or # stock id in parens
            re.search(r'-+ ?reuters', s) or # dashes and reuters at beginning
            re.search(r'^ *[\*-]+', s) or # multiple asterisks or dashes at beginning
            'daily earnings hits' in s or
            'this is a test' in s or
            'please ignore' in s or
            'reuters world news' in s or
            'reuters sports features schedule' in s or
            'quote of the day' in s or
            'factors to watch' in s or
            'margin intex for' in s
    ):
        return True

    else:
        return False


def headline_reader():
    fname = '../data/headlines.csv.gz'
    with gzip.open(fname, 'r') as f:
        rdr = csv.reader(codecs.iterdecode(f, 'latin-1'))
        for line in rdr:
            if line:
                yield line


def save_counter(counterobj, fname):
    with open(fname, 'wb') as f:
        pickle.dump(counterobj, f)


def main():
    linecount = 0
    taggedcount = 0
    n = 4
    english_words = set(w.lower() for w in nltk.corpus.words.words())
    verbtags = {'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'}
    ngramcounter = Counter()
    reader = headline_reader()
    print('Begin processing')
    for line in reader:
        linecount += 1
        phrase = clean_headline(line[1].lower())
        taggedphrase = nltk.pos_tag(nltk.word_tokenize(phrase))
        tags = [token[1] for token in taggedphrase]
        wordset = {token[0] for token in taggedphrase if token[0].isalpha()}
        hasverb = any([tag in verbtags for tag in tags])
        unknownwords = wordset - english_words
        if (
                hasverb and 
                len(tags) >= 8 and 
                not isjunk(phrase) and
                len(unknownwords) < (len(wordset) / 2)
        ):
            tagngrams = list(ngrams(tags, n))
            ngramcounter.update(tagngrams)
            taggedcount += 1
        if linecount % 10000 == 0:
            print(linecount, 'lines processed;', taggedcount, "lines' POS added to model")
    print('Done.')
    print(linecount, 'lines processed;', taggedcount, "lines' POS added to model")
    print(len(ngramcounter), 'unique ' + str(n) + '-grams')
    print(ngramcounter.most_common(5))
    save_counter(ngramcounter, '../data/' + str(n) + 'grammodel.pickle')


if __name__ == "__main__":
    sys.exit(main())


# Notes
'''
english_vocab = set(w.lower() for w in nltk.corpus.words.words())
text_vocab = set(w.lower() for w in text if w.lower().isalpha())
unusual = text_vocab.difference(english_vocab) 
''.join(set(string.punctuation) - {"'", '"', "!", ".", "?"}
'''
