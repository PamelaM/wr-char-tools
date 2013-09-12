# coding=utf-8
import types
try:
    import chardet
except ImportError:
    chardet = None

#   UTF-8 will also catch ascii, 
#   cp1252 will also catch latin-1, 
#   mac_roman is it's own thing
#   850 is msdos-latin

DEFAULT_CHARSETS = ['utf-8', 'cp1252', 'mac_roman', '850']
def _str_2_unicode(data, charsets, encode_errors):
    if not charsets:
        charsets = DEFAULT_CHARSETS
        
    for e in charsets:
        try:
            return unicode(data, e)
        except UnicodeDecodeError:
            pass
    
    if chardet:
        cd = chardet.detect(data)
        # -- If confidence is 75%+, try using it
        if cd['confidence']>0.75:
            try:
                return unicode(data, cd['encoding'])
            except UnicodeDecodeError:
                pass
    
    # -- Got here, raise the utf-8 error...
    return unciode(data, 'utf-8')
    
def make_unicode(data, charsets=None, encode_errors=None):
    # If it's not already a str, we can safely unicode-ify it
    if not isinstance(data, str):
        return unicode(data)
    else:
        return _str_2_unicode(data, charsets, encode_errors)

    
def makeUTF8(data, charsets=None, encode_errors='ignore'):
    if not isinstance(data, basestring):
        # Don't covert non-basestring data
        return data
    
    if isinstance(data, str):
        data = _str_2_unicode(data, charsets, encode_errors)        
    return data.encode("utf-8", encode_errors)    

def _make_item(func, i):
    if isinstance(i, dict):
        return _make_dict(func, i)
    elif isinstance(i, basestring):
        return func(i)
    elif isinstance(i, tuple):
        return _make_tuple(func, i)
    elif isinstance(i, list):
        return _make_list(func, i)
    else:
        return i

def _make_dict(func, d):
    return dict([(_make_item(func, k), _make_item(func, v)) for k,v in d.items()])

def _make_tuple(func, t):
    return tuple(_make_list(func, t))

def _make_list(func, l):
    return [_make_item(func, i) for i in l]

# Helpers to convert strings in common python objects into either utf-8 or unicode
def makeItemUTF8(i):
    return _make_item(makeUTF8, i)

def makeDictUTF8(d):
    return _make_dict(makeUTF8, d) 

def makeTupleUTF8(t):
    return _make_tuple(makeUTF8, t)

def makeListUTF8(l):
    return _make_list(makeUTF8, t)

def make_unicode_item(i):
    return _make_item(make_unicode, i)

def make_unicode_dict(d):
    return _make_dict(make_unicode, d) 

def make_unicode_tuple(t):
    return _make_tuple(make_unicode, t)

def make_unicode_list(l):
    return _make_list(make_unicode, t)
