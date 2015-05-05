import sys
import re
import string
import unicodedata
import dateutil.parser
from html import unescape



## Constants ##

# for base encoding
BASE_LIST = string.digits + string.ascii_letters
BASE_DICT = dict((c, i) for i, c in enumerate(BASE_LIST))



## Translation Tables ##

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

punc_ords = {i for i in range(sys.maxunicode)}
punc_ords.update(map(ord, string.punctuation))

rmpunc_transtable = dict.fromkeys(punc_ords)


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
    multspacereg = re.compile(r' +')
    s = re.sub(multspacereg, ' ', s)
    return s


# removes all punctuation from string s
def rmpunc(s):
    s = s.translate(rmpunc_transtable)
    return s


# remove url from string
def rmurls(s):
    urlreg = re.compile(r'(([\w-]+://?|www[.])[^\s()<>]+)')
    s = re.sub(urlreg, '', s)
    return s


# encode to base62 (or other base) string
def baseencode(inputnum, base=BASE_LIST):
    baselen = len(base)
    outstr = ''
    while inputnum != 0:
        outstr = base[inputnum % baselen] + outstr
        inputnum //= baselen
    return outstr


# decode base62 (or other base) string to int
def basedecode(s, reverse_base=BASE_DICT):
    length = len(reverse_base)
    outputnum = 0
    for i, c in enumerate(s[::-1]):
        outputnum += (length ** i) * reverse_base[c]
    return outputnum
