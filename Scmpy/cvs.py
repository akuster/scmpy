"""
The SCM module contains a common interface to
some of the other scm programs such as cvs and git
"""

#
# cmdCreate
#

def cmdCreate(scm, command, dest, branch, module, path, user):
    scmOpts = ("%s -d :ext:%s@%s " % \
    (scm, user, path))
    cmdOpts = (" -r %s -d %s" % (branch, dest))
    mod = (" %s" % module)
    cmdOpts = cmdOpts + mod

    return dict([('ScmOpts', scmOpts), ('cmd', command), ('cmdOpts', cmdOpts)])
