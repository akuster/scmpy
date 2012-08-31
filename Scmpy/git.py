#
"""
The SCM module contains a common interface to
some of the other scm programs such as cvs and git
"""

#class ScmCmd():
#
# cmdCreate
#

def cmdCreate(scm, command, dest, branch, module, path, user):
    scmOpts  = scm
    cmdOpts = ("%s %s" % (path, dest))
    return dict([('ScmOpts', scmOpts), ('cmd', command), ('cmdOpts', cmdOpts)])
