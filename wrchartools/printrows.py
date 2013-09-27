import sys
import codecs
import locale
import stdwrapper
import anglicize

def sprint_rows_as_text(*args, **kwargs):
    stw = stdwrapper.StdWrapper()
    try:
        _print_rows_as_text(*args, **kwargs)
    finally:
        sout, serr = stw.done()
    return sout

def print_rows_as_text(*args, **kwargs):
    # Convert to preferred encoding to prevent UnicodeDecode errors when printing to stdout
    saved_sout = sys.stdout
    try:
        sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
        _print_rows_as_text(*args, **kwargs)
    finally:
        sys.stdout = saved_sout
        
def _wrap_row(in_row):
    out_rows = [[],]
    
    for idx, e in enumerate(in_row):
        if isinstance(e, basestring) and "\n" in e:
            pieces = e.split("\n")
            out_rows[0].append(pieces[0])
            # Add any needed extra out_rows
            while len(out_rows)<len(pieces):
                out_rows.append(["" for ignored in in_row])
            for pidx, p in enumerate(pieces[1:]):
                out_rows[pidx+1][idx] = p                    
        else:
            out_rows[0].append(e)
    return out_rows
        
def _wrap_rows(in_rows):
    out_rows = []
    for row in in_rows:
        out_rows.extend(_wrap_row(row))
    return out_rows


def _calc_col_lens(rows, col_lens):
    if not rows:
        return col_lens
    
    def _str(f):
        try:
            return str(f)
        except:
            return anglicize.anglicize(f)
        
    if not col_lens:        
        col_lens = [len(_str(f)) for f in rows[0]]
        
    for row in rows:
        row_lens = [len(_str(f)) for f in row]
        col_lens = [max(f, r) for f, r in map(None, col_lens, row_lens)]

    return col_lens

def _print_row_as_text(row, fmt):
    try:
        out = fmt % tuple(row)
        print out.rstrip()
    except:
        print "FMT: %r" % fmt
        print "ROW: %r" % row
        raise
        
def _print_rows_as_text(rows, first_is_header=True, col_lens=None, formats=None):
    if not rows:
        return
    
    if first_is_header:
        header_rows = _wrap_rows(rows[:1])
        body_rows = _wrap_rows(rows[1:])        
    else:
        header_rows = []
        body_rows = _wrap_rows(rows)

    if not col_lens:
        col_lens = _calc_col_lens(header_rows, [])
        col_lens = _calc_col_lens(body_rows, col_lens)

    if not formats:
        formats = [u"%%-%ss" for f in col_lens]
        
    fmt = u"  ".join([f % l for l, f in map(None, col_lens, formats)])
    if header_rows:
        for row in header_rows:
            _print_row_as_text(row, fmt)
        _print_row_as_text([u"="*f for f in col_lens], fmt)

    for row in body_rows:
        _print_row_as_text(row, fmt)
    #print fmt
    
        