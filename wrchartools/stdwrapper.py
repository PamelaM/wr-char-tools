import time
import sys
import StringIO
import makeutf8

class StdFile(StringIO.StringIO):
    """A cStringIO sub-class that provides a fileno so things that check the fileno
       of stdin/out/err don't get cranky
    """
    
    def __init__(self, fileno, *args, **kwargs):
        self._fileno = fileno
        self._passthru = None
        StringIO.StringIO.__init__(self, *args, **kwargs)
    
    def fileno(self):
        return self._fileno

    def enable_passthru(self, pf):
        self._passthru = pf
    
    def write(self, s):
        if self._passthru:
            self._passthru.write(s)
        if "\b" in s:
            while "\b\b" in s:
                s = s.replace("\b\b", "\b")
            s = s.replace("\b", "\n")
        StringIO.StringIO.write(self, s)

class StdFileUnicode(StdFile):
    def write(self, s):
        return StdFile.write(self, makeutf8.make_unicode(s))

DEFAULT_PROGRESS_INTERVAL = 1.0 # seconds        
class StdWrapper:
    """
        Example:
        
        import stdwrapper
        
        stw = stdwrapper.StdWrapper()
        try:
            do_something()
        finally:
            sout, serr = stw.done()
        
        print sout
        print serr
        
    """
    wrapDepth = 0
    def __init__(self, wrapOutput=True, inputText=None, 
                 inputFile=None, combine_stdout_and_stderr=False, passthru=False,
                 progress_interval=DEFAULT_PROGRESS_INTERVAL,
                 passthru_stderr=False,
                 unicode_out=False):
        """
        wrapOutput    - If False, then stdout and stderr are not affected
        inputText     - If has a value, then stdin is replaced with a StdFile containing that text
        inputFile     - If has a value, then stdin in replaced with that file, opened [ignored if inputText is set]
        combine_stdout_and_stderr - If True, then only one file is StdFile is used.  This can cause programs that check for fileno 2 to get confused
        passthru      - If True, then not only capture the output, but also write it to the original file location (good for debugging)
        """
        StdWrapper.wrapDepth += 1

        self.passthru = passthru
        self.passthru_stderr = passthru_stderr
        self.wrapOutput = wrapOutput
        self.progress_interval = progress_interval

        if unicode_out:
            _stdFileClass = StdFileUnicode
        else:
            _stdFileClass = StdFile
                    
        #print "StdWrapper.__init__ - depth:", wrapDepth
        self.tmpstdout = _stdFileClass(1)
        if combine_stdout_and_stderr:
            self.tmpstderr = self.tmpstdout
        else:
            self.tmpstderr = _stdFileClass(2)      

        self.oldstdout = sys.stdout
        self.oldstderr = sys.stderr
        
        if wrapOutput:
            sys.stdout = self.tmpstdout
            sys.stderr = self.tmpstderr
            if passthru:
                self.tmpstdout.enable_passthru(self.oldstdout)
            if not combine_stdout_and_stderr and (passthru or passthru_stderr):
                self.tmpstderr.enable_passthru(self.oldstderr)
                    

        self.oldstdin = sys.stdin
        if inputText:
            if inputFile:
                raise ValueError, "Only one of inputText and inputFile can be used"
            self.tmpstdin = StdFile(0, inputText)
            sys.stdin = self.tmpstdin
        elif inputFile:
            self.tmpstdin = None
            sys.stdin = inputFile            
        else:
            self.tmpstdin = None

        self.progress_line_buffer = ""
        self.next_progress_time = 0.0
        self.live_progress = self.passthru or self.wrapOutput
    
    def get(self):
        # Get the current values w/o disturbing things
        out = self.tmpstdout.getvalue()
        err = self.tmpstderr.getvalue()
        return out, err
    
    def done(self):
        sys.stdout = self.oldstdout
        sys.stderr = self.oldstderr
        sys.stdin = self.oldstdin
        
        #print "StdWrapper.done - depth:", wrapDepth
        StdWrapper.wrapDepth -= 1
        out = self.tmpstdout.getvalue()
        err = self.tmpstderr.getvalue()
        return out,err
    
    def isprogresstime(self):
        return time.time()>self.next_progress_time
    
    def _write_live_progress_line(self, line, lf):        
        pb_len = len(self.progress_line_buffer)
        if pb_len:
            # Determine how much of progress_line_buffer is the same as the line to print
            idx = 0
            for b, c in map(None, self.progress_line_buffer, line):
                if b!=c:
                    break
                idx += 1
            assert(pb_len>=idx)
            num_back = pb_len - idx
            
            self.oldstderr.write("\b" * num_back)
            self.oldstderr.write(line[idx:])
        else:
            self.oldstderr.write(line)
            
        if lf:
            self.oldstderr.write("\n")
            self.progress_line_buffer = ""
        else:
            self.progress_line_buffer = line
            
    def _write_progress_line(self, line, lf):        
        if self.live_progress:
            self._write_live_progress_line(line, lf)
        if self.wrapOutput:
            sys.stderr.write("%s\n" % line)

    def progress(self, msg):
        lines = msg.split("\n")
        for line in lines[:-1]:
            self.__write_progress_line(line, True)
        for line in lines[-1:]:
            self._write_progress_line(line, False)        
        self.next_progress_time = time.time()+self.progress_interval
