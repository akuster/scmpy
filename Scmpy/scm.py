"""
The SCM module contains a common interface to
some of the other scm programs such as cvs and git
"""
import os
import sys
import re
import ConfigParser

from scmdb import ScmCfgDB
import process

class Scm(ScmCfgDB):

    def __init__(self, scmRef=None, ref=None, ver=None, type=None):
        self.scmRef = scmRef
        self.ref = ref
        self.ver = ver
        self.type = type
        self.noise = 0
        self.debug = 0
        self.trace = 0
        self.db = {}
        if self.debug:
            print "Scm: init(%s, %s, %s, %s) " % (scmRef, ref, ver, type)
        ScmCfgDB.__init__(self,self.db)
        if ref and ver and type:
            self.scmRef = self.findScmRef()
            scm  = self.GetScm(self.scmRef)
#
# topObranch
#
    def topObranch(self):
        """
        This returns the top of branch name for a given repository
        as defined by the refrenece, version and catagory
        """
        tagname = None
        if not self.scmRef or not self.ver or not self.type:
            raise KeyError, "topObranch: Params need value"

        if self.debug:
            print "topObranch(%s, %s, %s, %s)" % \
            (self.scmRef, self.type, self.ref, self.ver)
        try:
            tagname = \
            self.db[self.scmRef][self.ref][self.ver][self.type]['misc'][1]
        except KeyError:
            raise KeyError, "Raw topObranch error"
        except:
            raise

        if self.debug:
            print "topObranch: %s" % tagname

        return tagname

#
# branch
#
    def branch(self):
        """
        This returns the branch name for a given repository
        as defined by the refrenece, version and catagory
        """
        if not self.scmRef or not self.ver or not self.type:
            raise KeyError, "branch: Params can't be empty"

        if self.debug:
            print "branch(%s, %s, %s, %s)" % \
            (self.scmRef, self.type, self.ref, self.ver)
        try:
            branch = self.db[self.scmRef][self.ref][self.ver][self.type]['branch']
        except KeyError:
            raise KeyError, "Raw branch error"
        except:
            raise
        else:
            if self.debug:
                print "Branch: %s" % branch
            return branch

#
# path
#
    def path(self):
        """
        This returns the path for a given repository
        as defined by the refrenece, version and catagory
        """
        if not self.scmRef or not self.ver or \
        not self.ref or not self.type:
            raise KeyError, "path: Params can't be empty"

        if self.debug:
            print "path(%s, %s, %s, %s)" % \
            (self.scmRef, self.ref, self.ver, self.type)

        try:
            loc = self.db[self.scmRef][self.ref][self.ver][self.type]['location']
            try:
                root = self.GetRoot(self.scmRef)
                loc = ("%s/%s" % (root, loc))
            except KeyError:
                pass
        except KeyError:
            raise

        if self.debug:
            print "loc: %s" % loc
        return loc

# cmdCreate
#
    def cmdCreate(self, alias, branch, module, path, \
    prefix, bugnumber, user):
        """ create the command line based on params passed
            We will try to load a module based on scmRef
            if that fails, default to the base scm like cvs
            or git module.
        """

        if self.noise:
            print "cmdCreate(%s, %s, %s, %s, %s, %s, %s)" % \
        (alias, branch, module, path, prefix, bugnumber, user)

        modDir = os.path.dirname(__file__)
        sys.path.insert(0, modDir)

        scm  = self.GetScm(self.scmRef)
        command = self.aliasToCmdName(scm, alias)
        dest = self._CreateDest(self.ref, branch, module, prefix, bugnumber)

        try:
            mod = __import__(self.scmRef)
        except ImportError:
            mod = __import__(scm)

        if self.noise:
            print "mod.cmdCreate(%s, %s, %s, %s, %s, %s, %s)" % \
        (scm, command, dest, branch, module, path, user)

        return (mod.cmdCreate(scm, command, dest, branch, module, path, user))

    def cmd(self, options, command , commandOptionsAndArguments):
        if self.debug:
            print "cmd( %s, %s, %s )" % (options, \
        command , commandOptionsAndArguments)
        command = ('%s %s %s' % \
        (options, command , commandOptionsAndArguments))
        if not self.debug:
            try:
                fout = process.OsCmd(command, stdout=sys.stdout.fileno(), stderr=sys.stderr.fileno(), echo=True)
            except process.CmdError:
                raise
        else:
            print command

    def login(self, branch, path, userid):
        """
        This logins into given repository
        """
        if self.debug:
            print "login(%s, %s, %s)" % (branch, path, userid)

#
# make_dest
#
    def _CreateDest(self, ref, tagname, module, prefix, bugnumber):
        if self.debug:
            print "_CreateDest(%s, %s, %s, %s, %s)" %\
            (ref, tagname, module, prefix, bugnumber)

        if tagname == "N/A":
            tagname = ref

        if prefix:
            dest=prefix

            if module is not os.curdir :
                dest=("%s_%s" % (dest, module))
            else:
                dest=("%s_%s" % (dest, tagname))
        else:
            if module is not os.curdir :
                dest=module
            else:
                dest=tagname

        if bugnumber:
            dest=("%s_%s" % (dest, bugnumber))
        if self.debug:
            print "Dest: %s" % dest
        return dest


#
def scm_init():
    return Scm()

if __name__ == "__main__":
    bugnumber = 0
    prefix = None
    modulename = os.curdir

    scmRef = None
    ref = "linus"
    ver = "2.6"
    type = "kernel"
    s = Scm(scmRef, ref, ver, type)
    s.debug=0

    print "Default User id: %s" % s.userid

    print "Test 1"
    s.debug=1
    s.noise=1
    try:
        s.scmRef = s.findScmRef()
    except KeyError:
        print "issue with findScm"
        sys.exit(1)


    path = s.path()
    print "Path: %s" % path
    tag = s.branch()

    command = \
    s.cmdCreate("clone",tag, modulename, path, prefix, bugnumber, s.userid)
    ret = s.cmd(command['ScmOpts'],command['cmd'], command['cmdOpts'])
