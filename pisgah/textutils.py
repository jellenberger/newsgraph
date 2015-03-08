import unicodedata
import dateutil.parser

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



## String simplification and normalization functions ##

def normspace(s):
    s = s.translate(space_transtable).strip()
    return s

def asciichars(s):
    s = unicodedata.normalize('NFKD', s) # normalize to combining chars
    s = s.translate(commonpunc_transtable) # punctuation to ascii
    s = s.encode('ascii', 'ignore').decode('ascii') # ascii only
    return s

def normdatestring(s):
    s = dateutil.parser.parse(s).isoformat()
    return s
