import sys
import re
import string
import unicodedata
import dateutil.parser
from html import unescape



## Translation tables ##

# whitespace to spaces
space_transtable = {
    ord('\t'): ' ',
    ord('\f'): ' ',
    ord('\n'): ' ',
    ord('\r'): None
}

# quotes and dashes to ascii
commonpunc_transtable = {
    ord('\u2018'): "'",
    ord('\u2019'): "'",
    ord('\u201C'): '"',
    ord('\u201D'): '"',
    ord('\u2010'): '-',
    ord('\u2011'): '-',
    ord('\u2012'): '-',
    ord('\u2013'): '-',
    ord('\u2014'): '-',
}

rmpunc_transtable = dict.fromkeys(i for i in range(sys.maxunicode)
                                  if unicodedata.category(chr(i)).startswith('P'))
rmpunc_transtable.update(dict.fromkeys(map(ord, string.punctuation)))


## String simplification and normalization functions ##

# convert all whitespace characters in a string to spaces
def normspace(s):
    s = s.translate(space_transtable).strip()
    return s


# remove all characters in a string that don't have ascii equivalents
# (after performing some very basic translations) 
def asciichars(s):
    s = unicodedata.normalize('NFKD', s) # normalize to combining chars
    s = s.translate(commonpunc_transtable) # some punctuation to ascii analog 
    s = s.encode('ascii', 'ignore').decode('ascii') # ascii only
    return s


# attempt to parse a string representing a date and convert 
# it to an iso 8601 format string
def normdatestring(s):
    s = dateutil.parser.parse(s).isoformat()
    return s


# attempt to parse a string representing a date and return
# a datetime value
def stringtodate(s):
    return dateutil.parser.parse(s)


# reduces all sequences of space chars with a single space char
def singlespaces(s):
    s = re.sub(' +', ' ', s)
    return s


# removes all punctuation from string s
def rmpunc(s):
    s = s.translate(rmpunc_transtable)
    return s


# replaces space-like punctuation with a space
def puncspace(s):
    s = s.replace('-', ' ')
    s = s.replace('_', ' ')
    return s


# remove url from string
def rmurls(s):
    s = re.sub('(([\w-]+://?|www[.])[^\s()<>]+)', '', s)
    return s
