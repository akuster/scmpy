import os
import sys
#import re
import subprocess

class CmdError(RuntimeError):
    def __init__(self, command):
        self.command = command

    def __str__(self):
        if not isinstance(self.command, basestring):
            cmd = subprocess.list2cmdline(self.command)
        else:
            cmd = self.command

        return "Execution of '%s' failed" % cmd


class NotFoundError(CmdError):
    def __str__(self):
        return CmdError.__str__(self) + ": command not found"

class ExecutionError(CmdError):
    def __init__(self, command, exitcode, stdout = None, stderr = None):
        CmdError.__init__(self, command)
        self.exitcode = exitcode
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self):
        message = ""
        if self.stderr:
            message += self.stderr
        if self.stdout:
            message += self.stdout
        if message:
            message = ":\n" + message

        return (CmdError.__str__(self) +
            " with exit code %s" % self.exitcode + message)

class Popen(subprocess.Popen):
    '''
        sets up some defaults.
    '''
    defaults = {
        "bufsize" : 1024,
        "shell": True,
        "close_fds": True,
        "stdin" : subprocess.PIPE,
        "stdout" :subprocess.PIPE,
        "stderr": subprocess.PIPE,
    }

    def __init__(self, *args, **kwargs):
        options = dict(self.defaults)
        options.update(kwargs)
        subprocess.Popen.__init__(self, *args, **options)

def OsCmd(cmd, **kwargs):
    '''
        retruns a tuple of ret, fout and ferr
    '''
    defaults = {
        'expect': 0
    }
    options = dict(defaults)
    options.update(kwargs)

    log = options.get('log')
    dryrun = options.get('dryrun')
    debug = options.get('debug')
    echo = options.get('echo')
    expect = options.get('expect')

    if debug:
        print "OsCmd(%s %s)" % (cmd, options)

    del options['expect']

    if log:
        del options['log']

    if echo:
        del options['echo']
        print cmd

    if debug is not None or debug >=0:
        del options['debug']

    if dryrun:
        del options['dryrun']

    try:
        p = Popen(cmd, **options)
    except KeyboardInterrupt:
        sys.exit(0)
    except OSError, e:
        if e.errno == 2:
            raise NotFoundError(cmd)
        elif e.errno == 128:
           raise ExecutionError(cmd)
        else:
            raise
    try:
        fout, ferr = p.communicate()
    except KeyboardInterrupt:
        sys.exit(0)

    if p.returncode != 0 and p.returncode != expect:
        raise ExecutionError(cmd, p.returncode, fout, ferr)

    if echo and fout is not None:
        print fout.strip('\n')

    return fout

