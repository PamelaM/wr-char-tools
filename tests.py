# vim: set fileencoding=utf-8 :
import itertools
import unittest
from wrchartools import makeutf8, anglicize, stdwrapper, printrows

CP1252_STR = "\x80\x80\x80\x80"
UTF8_STR = "\xe2\x82\xac\xe2\x82\xac\xe2\x82\xac\xe2\x82\xac"
UNICODE_STR = unicode(CP1252_STR, "cp1252")

# FORMAT : test_value, utf8-expected, anglicize-expected, charsets, encode_errors
TEST_VALUES = [("","", "",[], 'ignore'),
         (None, None, None,[], 'ignore'),
         ("ascii-foo","ascii-foo", "ascii-foo",[], 'ignore'),
         ("ascii-BAR","ascii-BAR","ascii-BAR",[], 'ignore'),
         ("ascii-'1234567890-`~!@#$%^&*()_+","ascii-'1234567890-`~!@#$%^&*()_+","ascii-'1234567890-`~!@#$%^&*()_+",[], 'ignore'),
         (u"ascii-foo","ascii-foo","ascii-foo",[], 'ignore'),
         (u"ascii-BAR","ascii-BAR","ascii-BAR",[], 'ignore'),
         (u"ascii-'1234567890-`~!@#$%^&*()_+","ascii-'1234567890-`~!@#$%^&*()_+","ascii-'1234567890-`~!@#$%^&*()_+",[], 'ignore'),
         ("utf8-äöü","utf8-\xc3\xa4\xc3\xb6\xc3\xbc","utf8-aou",[], 'ignore'),
         (u"utf8-äöü","utf8-\xc3\xa4\xc3\xb6\xc3\xbc","utf8-aou",[], 'ignore'),
         ("cp1252-1000\x80", "cp1252-1000\xe2\x82\xac","cp1252-1000",[], 'ignore'),
         ("junk-aaa\x8e","junk-aaaŽ", "junk-aaaZ",[], 'ignore'),
         ("junk-aaa\x8f","junk-aaaè", "junk-aaae",[], 'ignore'),
         ("junk-aaa\x8d","junk-aaaç", "junk-aaac",[], 'ignore'),
         ("junk-aaa\x81","junk-aaaÅ", "junk-aaaA",[], 'ignore'),
         ("""SQ: \xe2\x80\x99, DQ: \xe2\x80\x9c, DQ: \xe2\x80\x9d, DASH: \xe2\x80\x94, SPC: \xe2\x80\xa8, OTHR: \xe2\x80\xa7""",
          """SQ: \xe2\x80\x99, DQ: \xe2\x80\x9c, DQ: \xe2\x80\x9d, DASH: \xe2\x80\x94, SPC: \xe2\x80\xa8, OTHR: \xe2\x80\xa7""" ,
          """SQ: ', DQ: ", DQ: ", DASH: -, SPC:  , OTHR: """ ,[], 'ignore'),
         ("Qu\x8er\x8e", "Qu\xc5\xbdr\xc5\xbd", "QuZrZ",[], 'ignore'),
         ("Qu\x8er\x8e", "Qu\xc3\xa9r\xc3\xa9", "Quere",['mac_roman', 'cp1252'], 'ignore'),
         ("ακολουθήστεA", "ακολουθήστεA", "A",[], 'ignore'),
         # cp1252 character mappings
         ('\x80', '\xe2\x82\xac', "",[], 'ignore'), 
         ('\x82', '\xe2\x80\x9a', "'",[], 'ignore'), 
         ('\x83', '\xc6\x92', '', [], 'ignore'),
         ('\x84', '\xe2\x80\x9e', '"', [], 'ignore'),
         ('\x85', '\xe2\x80\xa6', "...",[], 'ignore'), 
         ('\x86', '\xe2\x80\xa0', '', [], 'ignore'),
         ('\x87', '\xe2\x80\xa1', '', [], 'ignore'),
         ('\x88', '\xcb\x86', '', [], 'ignore'),
         ('\x89', '\xe2\x80\xb0', '', [], 'ignore'),
         ('\x8a', '\xc5\xa0', 'S', [], 'ignore'),
         ('\x8b', '\xe2\x80\xb9', '', [], 'ignore'),
         ('\x91', '\xe2\x80\x98', "'",[], 'ignore'), 
         ('\x92', '\xe2\x80\x99', "'",[], 'ignore'), 
         ('\x93', '\xe2\x80\x9c', '"', [], 'ignore'),
         ('\x94', '\xe2\x80\x9d', '"', [], 'ignore'),
         ('\x96', '\xe2\x80\x93', '-', [], 'ignore'),
         ('\x97', '\xe2\x80\x94', '-', [], 'ignore'),
         ('\x99', '\xe2\x84\xa2', 'TM', [], 'ignore'),

         ('\x80', '\xe2\x82\xac', "&#8364;",[], 'xmlcharrefreplace'), 
         ('\x82', '\xe2\x80\x9a', "&#8218;",[], 'xmlcharrefreplace'), 
         ('\x83', '\xc6\x92', '&#402;', [], 'xmlcharrefreplace'),
         ('\x84', '\xe2\x80\x9e', '&#8222;', [], 'xmlcharrefreplace'),
         ]

    
class makeutf8TestCase(unittest.TestCase):
    def test_make_tuple(self):
        _mt = makeutf8.makeTupleUTF8
        self.assertEqual(_mt(("utf8-äöü1", "utf8-äöü2")), ('utf8-\xc3\xa4\xc3\xb6\xc3\xbc1', 'utf8-\xc3\xa4\xc3\xb6\xc3\xbc2'))
    
    def test_makeUTF8(self):
        for val, uexpected, aexpected, charsets, encode_errors in TEST_VALUES:
            got =  makeutf8.makeUTF8(val, charsets, encode_errors)
            self.assertTrue(got==uexpected, "Input     %r\nGot:      %r\nExpected: %r" % (val, got, uexpected))
            
    def test_anglicize(self):
        for val, uexpected, aexpected, charsets, encode_errors in TEST_VALUES:
            got =  anglicize.anglicize(val, charsets=charsets, encode_errors=encode_errors)
            self.assertTrue(got==aexpected, "Input     %r\nGot:      %r\nExpected: %r" % (val, got, aexpected))

    def test_make_unicode(self):
        for val, u8expected, aexpected, charsets, encode_errors in TEST_VALUES:
            got =  makeutf8.make_unicode(val, charsets)
            try:
                uexpected = unicode(u8expected)
                umode = "plain"
            except:
                uexpected = unicode(u8expected, 'utf-8')
                umode = "utf-8"
            self.assertTrue(got==uexpected, "Input     %r\nGot:      %r\nExpected: unicode(%r)" % (val, got, uexpected))
            
    def test_makeItemUTF8(self):
        TEST_DICTS = [({},{}),
                      ({"U":'\x81', 
                        "W":"\x96", 
                        "N":1, 
                        "S":"A", 
                        "L":["A",1,'\x81',"\x96", ["A",1,'\x81',"\x96"], {"A":"a","N":1,'\x81':"U","\x96":"W",}], 
                        "D":{"A":"a","N":1,'\x81':"U","\x96":"W","L":["A",1,'\x81',"\x96"]}},
                       {"U":'Å', 
                        "W":"\xe2\x80\x93", 
                        "N":1, 
                        "S":"A", 
                        "L":["A",1,'Å',"\xe2\x80\x93", ["A",1,'Å',"\xe2\x80\x93"], {"A":"a","N":1,'Å':"U","\xe2\x80\x93":"W",}], 
                        "D":{"A":"a","N":1,'Å':"U","\xe2\x80\x93":"W","L":["A",1,'Å',"\xe2\x80\x93"]}}, 
                       ),
                      ]
        self._test_makeitem(makeutf8.makeItemUTF8, TEST_DICTS)
                
    def test_make_unicode_item(self):
        def _t(input, expected):
            got = makeutf8.make_unicode_item(input)
            self.assertTrue(got==expected, "Input     %r\nGot:      %r\nExpected: %r" % (input, got, expected))
            
        _t({}, {})
        _t({"U":"U"},  {u"U":u"U"})
        _t({"U":1},  {u"U":1})
        _t(1,  1)
        _t(("A","B", ["FOO", 8]),   (u"A",u"B", [u"FOO", 8]))
        _t({u"U":"U"},  {u"U":u"U"})
        _t({u"U":CP1252_STR},  {u"U":UNICODE_STR})

    def _test_makeitem(self, func, dicts):
        for input, expected in dicts:
            got = makeutf8.makeItemUTF8(input)
            if got!=expected:
                for k in got.keys():
                    print "%-5s %s:\n  %s\n  %s" % (k, (expected.get(k, "N/A")==got[k]), expected.get(k, "N/A"), got[k])
                for k in expected.keys():
                    if not k in got:
                        print "%-5s False :\n  %s\n  %s" % (k, expected[k], "N/A")
                self.assertEqual(got, expected)



class StdWrapperTestCase(unittest.TestCase):
    

    def testStdWrapper(self):
        # Wrap Output = True/False
        # Input Text = None, "", "INPUT TEXT"
        # InputFile = None, "", "testStdWrapperInputText"
        # combine_stdout_and_stdder = True/False
        # progress_strings = None or list of strings
        
        wrapOutput = [True, False]
        inputText = [None, '', "INPUT TEXT"]
        inputFile = [None, "", "tests/testStdWrapperInputFile.txt"]
        combine_stdout_and_stderr = [True, False]
        passthru = [True, False]
        progress_strings = []#None, [], [''], ['single',],['singlenr\n',],['multi\nnr\n',],['singlenr\n','single1','single2',"multi1\nsingle2"]]
        for wo, intext, infile, css, pt, ps in itertools.product(wrapOutput, inputText, inputFile, combine_stdout_and_stderr, passthru, progress_strings):
            try:
                self.one_run(wo, intext, infile, css, pt, ps)
            except Exception, e:
                print "ONE RUN INFO:"
                print "wrapOutput   :", wo
                print "inputText    :", intext
                print "inputFile    :", infile
                print "Combine      :", css
                print "Passthru     :", pt
                print "Prog Strs    :", ps
                raise
            
        
    def one_run(self, wrapOutput, inputText, inputFileName, 
                combine_stdout_and_stderr,  passthru=False,
                progress_strings=None):

        if progress_strings:
            print "THERE ARE PROGRESS STRINGS"
        exception_expected = inputText and inputFileName
        if inputFileName:
            inputFile = open(inputFileName)
        else:
            inputFile = None
            
        # YES, we're playing games with testing with it's own behaviour, but I think it's okay...
        outer_stw = stdwrapper.StdWrapper()
        was_exception = False
        try:
            try:
               stw = stdwrapper.StdWrapper(wrapOutput, inputText, inputFile, combine_stdout_and_stderr, passthru=passthru, progress_interval=0.01)
               self.failIf(exception_expected, "Expected an exception here")
            except ValueError:
                if exception_expected:
                    return
                raise
                
            try:
                print "NORMAL STDOUT"
                sys.stderr.write("NORMAL STDERR\n")
                if inputFile and not inputText:
                    self.failIfEqual(sys.stdin.fileno(),0)
                else:
                    self.assertEqual(sys.stdin.fileno(),0)
                    
                self.assertEqual(sys.stdout.fileno(),1)
                if wrapOutput and combine_stdout_and_stderr:
                    self.assertEqual(sys.stderr.fileno(),1)
                else:
                    self.assertEqual(sys.stderr.fileno(),2)

                if inputText or inputFile:
                    input = sys.stdin.readline()
                    print "INPUT:", input
                
                if progress_strings!=None:
                    for s in progress_strings[:-1]:
                        self.assertTrue(stw.isprogresstime())
                        stw.progress(s)
                        self.failIf(stw.isprogresstime())
                        stw.next_progress_time = 0.0
                    for s in progress_strings[-1:]:
                        stw.progress(s)
                    
            finally:
                inner_sout, inner_serr = stw.done()
        except Exception, e:
            was_exception = True
            raise
            
        finally:
            outer_sout, outer_serr = outer_stw.done()
            if 1 or was_exception:
                print "-----"
                print "INNER SOUT : ", repr(inner_sout)
                print "INNER SERR : ", repr(inner_serr)
                print "OUTER SOUT : ", repr(outer_sout)
                print "OUTER SERR : ", repr(outer_serr)
            
        
        if wrapOutput and passthru:       
            # Both inner_sout and outer_sout should have everything
            self.check_output(None, None, inner_sout, inner_serr, inputText, inputFileName, combine_stdout_and_stderr, progress_strings)
            if combine_stdout_and_stderr:
                # The inner test combined everyting to sout, so outer_serr never got anything...                
                self.failIf(outer_serr)
                # ... but check_output assumes that sout==serr, so make it so
                outer_serr = outer_sout
            self.check_output(None, None, outer_sout, outer_serr, inputText, inputFileName, combine_stdout_and_stderr, progress_strings)
        elif wrapOutput and not passthru:
            # outer_ should be empty
            self.check_output(outer_sout, outer_serr, inner_sout, inner_serr, inputText, inputFileName, combine_stdout_and_stderr, progress_strings)
        else:
            # Not wrapping, so a) passthru is ignored, and b) inner_ should be empty
            self.check_output(inner_sout, inner_serr, outer_sout, outer_serr, inputText, inputFileName, False, progress_strings)

    def check_output(self, empty_sout, empty_serr, sout, serr, inputText, inputFileName, combine_stdout_and_stderr, progress_strings):                    
        self.failIf(empty_sout)
        self.failIf(empty_serr)
        
        self.assertIn("NORMAL STDOUT\n", sout)
        self.assertIn("NORMAL STDERR\n", serr)

        if combine_stdout_and_stderr:
            self.assertEqual(sout, serr)
            self.assertIn("NORMAL STDOUT\nNORMAL STDERR\n", sout)
        else:
            self.failIfEqual(sout, serr)
        

        if not inputText and inputFileName:
            inputText = open(inputFileName).read()
        
        if inputText:
            self.assertIn("INPUT: %s\n" % inputText, sout)
        else:
            self.assertNotIn("INPUT:", sout)
        
            
        if progress_strings!=None:
            for s in progress_strings:
                self.assertIn(s, serr)                

class PrintrowsTestCase(unittest.TestCase):
    
    def test_emptyrows(self):
        sout = printrows.sprint_rows_as_text([])
        self.failIf(sout, sout)

    def _check_col_widths(self, sout):
        lines = sout.split("\n")
        for line in lines:
            if line[0]=="=":
                cols = [len(x) for x in line.split()]
                return cols
        return None

    def _check_line(self, cols, line):
        words = line.split()
        self.assertEqual(len(words), len(cols))
        wlens = [len(w) for w in words]
        pairs =  map(None, wlens, cols)
        bad_pairs = [(w, c) for w, c in pairs if w>c]
        self.failIf(bad_pairs, "%s Cols too long %s\n%s" % (len(bad_pairs), bad_pairs, line))
                
    def test_spaces(self):
        rows = []
        rows.append(["Campaign ID", "Campaign Name", "Bulkmail ID", "Bulkmail Name"])
        rows.append([180,"PartnersDec172012NewsletterBase",13,"BulkSPDec172012NewsletterFreeAccred"])
        
        sout = printrows.sprint_rows_as_text(rows)
        self.assertTrue(sout, sout)
        cols = self._check_col_widths(sout)
        self.assertTrue(cols, cols)
        for line in sout.strip().split("\n")[2:]:
            self._check_line(cols, line)
            
        
    def test_multiline_fields(self):
        header = ("A\nAA\nAAA", "B", "C", "D", "EEEE\nE\nEE")
        rows = [header,]+[("a", "b", "c", "d", "e"),]
        sout = printrows.sprint_rows_as_text(rows)
        before, after = sout.split("=",1)
        before_lines = before.strip().split("\n")
        self.assertTrue(len(before_lines)==3, repr(before_lines))
        self.assertIn("EEEE", before_lines[0])
        self.assertIn("AAA", before_lines[2])
        self.assertIn("EE", before_lines[2])
        for c in "BCD":
            self.assertIn(c, before_lines[0])
            self.assertNotIn(c, before_lines[1])
            self.assertNotIn(c, before_lines[2])
        
        after_lines = after.split("=")[-1].strip().split("\n")
        self.assertTrue(len(after_lines)==1, repr(after_lines))
        
        
    def test_bunch_not_all_tuples(self):
        header = ("A","B","C","D", "E")
        num_cols = len(header)
        NUM_ROWS = 10
        rows = [header]
        types = [int, str, unicode, float]
        tidx = 0
        for i in range(NUM_ROWS):
            row = []
            for n in range(1,num_cols+1):
                v = (i+1)*n
                t = types[tidx]
                tidx += 1
                if tidx>=len(types):
                    tidx = 0
                if t in (unicode, str):
                    v = t(v)*v
                else:
                    v = t(v)
                row.append(v)
            rows.append(row)
        sout = printrows.sprint_rows_as_text(rows)        
        out_rows = [r.split() for r in sout.strip().split("\n")]
        self.assertTrue(len(out_rows)==(NUM_ROWS+2), "Got %s rows, expected %s\n%s" % (len(out_rows), NUM_ROWS+2, sout))
        for idx, row in enumerate(out_rows):
            self.assertTrue(len(row)==num_cols, "Row #%s got %s cols, expected %s\n%s" % (idx, len(row), num_cols, sout))
            
    def test_one_header(self):
        sout = printrows.sprint_rows_as_text([("A", "B", "C")])        
        self.assertTrue(sout, sout)
        rows = sout.split("\n")
        self.assertTrue(len(rows)==3, "len: %s\n%s" % (len(rows), sout))
        self.assertTrue(rows[1].strip()[0]=="=", sout)
        self.assertTrue(rows[0].split()[0]=="A", sout)
        self.assertTrue(rows[0].split()[1]=="B", sout)
        self.assertTrue(rows[0].split()[2]=="C", sout)
        self.failIf(rows[2].strip(), sout)
        
    def test_one_not_header(self):
        sout = printrows.sprint_rows_as_text([("A", "B", "C")], first_is_header=False)        
        self.assertTrue(sout, sout)
        rows = sout.split("\n")
        self.assertTrue(len(rows)==2, "len: %s\n%s" % (len(rows), sout))
        self.failIf(rows[1].strip(), sout)
        self.assertTrue(rows[0].split()[0]=="A", sout)
        self.assertTrue(rows[0].split()[1]=="B", sout)
        self.assertTrue(rows[0].split()[2]=="C", sout)

    def test_width(self):
        EXPECTED_LEN = 2+3+4+(2*2)
        EXPECTED_ROWS = 3
        sout = printrows.sprint_rows_as_text([("A", "B", "C"),
                                               (22, "QQQ", "QQQQ")], 
                                              first_is_header=False)        
        self.assertTrue(sout, sout)
        rows = sout.split("\n")
        self.assertTrue(len(rows)==EXPECTED_ROWS, "len: %s\n%s" % (len(rows), sout))
        self.failIf(rows[EXPECTED_ROWS-1].strip(), sout)
        for idx in range(EXPECTED_ROWS-1):
            self.assertTrue(len(rows[idx])==EXPECTED_LEN, "%s: Expected: %s, Got: %s\n%s" % (idx, EXPECTED_LEN, len(rows[idx]), repr(sout)))

    def test_unicode(self):
         rows = [["A", "B", "C", "D", "E", "F"],
                 ['Account', 'Business_Classification_Cleansed__c', u'Business Classification \u2013 Cleansed', 'string(13)', '', '']]
         sout = printrows.sprint_rows_as_text(rows)
         self.assertEqual(len(sout.split("\n")), 4)
         self.assertIn(u'Business Classification \u2013 Cleansed', sout)
         
                                     
if __name__ == '__main__':
    # When this module is executed from the command-line, run all its tests
    unittest.main()