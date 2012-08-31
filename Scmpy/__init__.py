#this is a wrapper module for different platform implementations
#
# (C)2007  Armin Kuster <akuster@kama-aina.net>
# this is distributed under a free software license, see license.txt

import sys
import os
import re
from scm import Scm

__version__=0.1

__debug = 0
def ScmpyVersion():
    return __version__

def scm_init(scmRef=None, ref=None, ver=None, type=None):
    return Scm(scmRef, ref, ver, type)
#
#
def TRACE(*str):
    f = sys._getframe().f_back
    print "TRACE:: [%s: %d] %s" % \
    (f.f_code.co_name, f.f_lineno, str)
#
#
def DEBUG(*str):
    f = sys._getframe().f_back
    print "DEBUG:: [%s:%d] %s" %\
    (f.f_code.co_name, f.f_lineno,str)


def listAll(__scmRef="all", __ref="all", __ver="all", __type="all"):
    """
    This returns a listing of a  given repository
    by the refrenece, version and catagory
    """
    scm = scm_init()
    if __debug:
        print "listAll(%s, %s, %s, %s)" % \
        (__scmRef, __type, __ref, __ver)

    for repo in scm.db.keys():
        if repo == __scmRef or __scmRef == "all" \
        or __scmRef == None:
            for ref in scm.db[repo]:
                if  __ref != None and __ref != "all":
                    if re.search(__ref,ref):
                        __ref = ref
                if ref == __ref or __ref == "all" \
                or __ref == None:
                    for ver in scm.db[repo][ref]:
                        if ver == __ver or __ver == "all" \
                        or  __ver == None:
                            for type in scm.db[repo][ref][ver]:
                                if type == __type  or \
                                __type == "all" or __type == None:
                                    scm.setScmVars(repo, ref, ver, type)
                                    print "=="*30
                                    print "%s %s (%s)" % \
                                    (ref, ver, repo)
                                    print "--"*30
                                    print "\t%s:" % type
                                    print "\t\tRoot:\t\t%s" % \
                                    scm.path()
                                    print "\t\tBranch:\t\t%s" % \
                                    scm.branch()
                                    print "\t\tTop of Branch:\t%s" % \
                                    scm.topObranch()
                                    print "\t\tScm:\t\t%s" % \
                                    scm.GetScm(repo)

