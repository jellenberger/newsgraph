import sys
import re
import sqlite3
import pickle
import gzip
import csv
import codecs
from collections import Counter
import nltk
from nltk.util import ngrams
import config
import textutils as tu


def clean_headline(s):
    intro_words_re = ('cricket|tennis|soccer|golf|football|basketball|baseball|'
        'nba|nhl|column|fxnews|analysis|forex|preview|newsmaker|us stocks|'
        'stocks news|feature|technicals|before the bell|interview|finews|'
        'stocks news europe|stocks news us|rpt|fund view|us credit|treasuries|'
        'brief|global markets|corrected|fed focus|refile|factbox|nations|'
        'fxoutlook|open|export summary|badminton|precious|nfl|next up|'
        'advisory|research alert|rallying|stocks news mideast|budget view|'
        'stocks news uk|global mkts|chronology|european swaps|highlights|'
        'mmnews|stocks news asia|olympics|rugby')
    s = tu.asciichars(s)
    s = s.replace('...', '')
    s = s.replace('--', '-')
    s = s.replace('_', '')
    s = re.sub(r'(update|wrapup|instant view|wrap) ?\d* ?[-:] ?', '', s)
    s = re.sub(r' ?(' + intro_words_re + ') ?-', '', s)
    return s.lower().strip()


def isjunk(s):
    if (
            'daily earnings hits' in s or
            'this is a test' in s or
            'please ignore' in s or
            'reuters world news' in s or
            'reuters sports features schedule' in s or
            'quote of the day' in s or
            'factors to watch' in s or
            'margin intex for' in s or
            'block deal' in s or
            'service alert' in s or
            'take a look' in s or
            'hot stocks' in s or
            'press digest' in s or
            'sealed bids:' in s or
            'scoreboard' in s or
            'economic diary' in s or
            'earnings diary' in s or
            'sports diary' in s or
            'speed guide' in s or
            re.search(r'(text|table|guide) ?\d* ?[-:] ?', s) or
            re.search(r'<(\w+|\d+)?(\.\w+)?>', s) # stock id in brackets
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


def process_and_save_headlines():
    conn = sqlite3.connect(config.dbfile)
    linecount = 0
    cleancount = 0
    headlines = []
    english_words = set(w.lower() for w in nltk.corpus.words.words())
    reader = headline_reader()
    with conn:
        c = conn.cursor()
        c.execute('DELETE FROM headline_corpus')
        for line in reader:
            linecount += 1
            phrase = clean_headline(line[1].lower())
            wordset = set(phrase.split())
            numwords = len(wordset)
            #if True:
            if ((len(wordset & english_words) > (numwords * 0.75)) and not 
                isjunk(phrase) and
                numwords > 3):
                headlines.append((phrase,))
                cleancount += 1
            # for every 100k lines processed, insert cleaned headlines into db
            if linecount % 100000 == 0:
                c.executemany('INSERT INTO headline_corpus(headline) VALUES (?)', headlines)
                headlines = []
    conn.close()


def get_headlines():
    conn = sqlite3.connect(config.dbfile)
    with conn:
        cur = conn.cursor()
        cur.execute('SELECT headline from headline_corpus')
        headlines = cur.fetchall()
    conn.close()
    return headlines


def make_ngram_model(headlines, n):
    ngramcounter = Counter()
    for headline in headlines:
        tagged_headline = nltk.pos_tag(nltk.word_tokenize(headline[0]))
        headline_tags = [token[1] for token in tagged_headline]
        tag_ngrams = list(ngrams(headline_tags, n))
        ngramcounter.update(tag_ngrams)
    return ngramcounter


def main():
	#process_and_save_headlines()
    print('Reading headlines')
    headlines = get_headlines()
    print(str(len(headlines)) + ' headlines retrieved')
    for n in range(3, 6):
        print('Calculating ' + str(n) + '-grams')
        ngramcounter = make_ngram_model(headlines, n)
        fname = '../data/' + str(n) + 'grammodel.pickle'
        with open(fname, 'wb') as f:
            pickle.dump(ngramcounter, f)


if __name__ == "__main__":
    sys.exit(main())


# Notes
'''
english_vocab = set(w.lower() for w in nltk.corpus.words.words())
text_vocab = set(w.lower() for w in text if w.lower().isalpha())
unusual = text_vocab.difference(english_vocab)
''.join(set(string.punctuation) - {"'", '"', "!", ".", "?"}
verbtags = {'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'}    
'''
