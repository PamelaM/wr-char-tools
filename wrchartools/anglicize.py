# 
# anglicize -- convert strings to just plain ascii
# Rev 0.1
#

import string, unicodedata, makeutf8

UNICODE_SPECIAL_CHARS = {0x2018:u"'",
                         0x2019:u"'",
                         0x201a:u"'",
                         
                         0x201C:u'"',
                         0x201D:u'"',
                         0x201E:u'"',
                         
                         0x2013:u'-',
                         0x2014:u'-',
                         0x2028:u' ',
                         }                             

def anglicize(text, raiseExceptions=False, charsets=[], encode_errors='ignore'):    
    """turns text into an ASCII string with a decent try to make latin-1 characters become simple ascii"""

    if not text:
        return text
    temp = makeutf8.makeUTF8(text, charsets=charsets) # make it a utf8 string
    if not isinstance(temp, unicode):
        temp = unicode(temp, 'utf-8')        # make it unicode
        
    # Do the translation BEFORE the noralize/encode makes them blanks
    if encode_errors!='xmlcharrefreplace':
        temp = temp.translate(UNICODE_SPECIAL_CHARS) # fix the cp1252 characters
        temp = temp.replace('\u2026' ,"...") # handle the elipsis, since it's a 1 char -> 3 chars
    
    fixed = unicodedata.normalize('NFKD', temp).encode('ASCII', encode_errors) # do the official normalize
    return fixed
 