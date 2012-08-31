#!/usr/bin/python
"""
The SCM module contains a common interface to
some of the other scm programs such as cvs and git
"""
import os
import sys
import re
import string
import ConfigParser
from scmcfg import ScmCfg

"""
There are two dictionaries used here.
1) is created from data in the default data config
2) is created from data in the data file
"""

class ScmCfgDB(ScmCfg):
    def __init__(self, db):
        """ This requires database dict and
            config object from ScmCfg()
        """
        self.noise=0
        self.debug=0
        self.trace=0
        self.cfgDB = {}
        self.db = db
        ScmCfg.__init__(self)

        files = self.GetDataFiles()
        for file in files:
            self.PrimeDataDB(file)

    def setScmVars(self, scmRef, ref, ver, type):
        self.scmRef = scmRef
        self.ref = ref
        self.ver = ver
        self.type = type

    def findScmRef(self):
        """
        This will find which scm to use for a
        given reference, version and type.
        It will return None if not found
        """
        if self.debug:
            print "findScmRef: (%s, %s, %s)" % (self.ref, self.ver, self.type)

        if not self.ref or not self.ver or not self.type:
            raise KeyError, "findScmRef: Params need value"

        for scmRef in self.db.keys():
            for reference in self.db[scmRef].keys():
                if re.search(self.ref,reference):
                    if self.ver in self.db[scmRef][reference]:
                        if self.type in self.db[scmRef][reference][self.ver]:
                            self.ref = reference
                            return scmRef

        raise KeyError, "findScmRef: Code not fine a valid scm"

    def GetScmRefByValue(self, ref, ver, type):
        for scm in self.db.keys():
            try:
                self.db[scm][ref][ver][type]
                return scm
            except KeyError:
                pass
        return None

    def _PrimeConfigDB(self,file):
        if self.debug:
            print "_PrimeConfiDB: (%s)" % file
        sections = []
        db = {}
        name = os.path.basename(file)
        c = ConfigParser.ConfigParser()
        try:
            c.read(file)
        except ConfigParser.NoSectionError:
            raise

        sections = c.sections()
        for section in sections:
            options = []
            options = c.options(section)
            for opt in options:
                datum = c.get(section, opt).strip(' ')

                d1 = {"%s" % name : {"%s" % section: \
                {"%s" % opt: {'data': ""}}}}
                d2 = {"%s" % section: {"%s" % opt: {'data': ""}}}
                d3 = {"%s" % opt: {'data': ""}}
                d4 = {'data': ""}

                if db.has_key(name):
                    if db[name].has_key(section):
                        if db[name][section].has_key(opt):
                            d4['data'] = datum
                            db[name][section][opt].update(d4)
                        else:
                            d3[opt]['data'] = datum
                            db[name][section].update(d3)
                    else:
                        d2[section][opt]['data'] = datum
                        db[name].update(d2)
                else:
                    d1[name][section][opt]['data'] = datum
                    db.update(d1)

        self.cfgDB.update(db)

    def GetDataFiles(self):
        files = []
        f = []

        files =  self.GetCfgFiles()

        if self.debug:
            print "GetDataFiles: %s: " % files

        for file in files:
            self._PrimeConfigDB(file)

        for name in self.cfgDB.keys():
            for scmRef in self.cfgDB[name].keys():
                for opt in self.cfgDB[name][scmRef].keys():
                    #print "%s) %s: %s = %s" % \
                    #(name, scmRef, opt, \
                    #self.cfgDB[name][scmRef][opt]['data'])
                    if opt == 'data':
                        f.append(self.cfgDB[name][scmRef][opt]['data'])
        return f

    def _GetFromDataFile(self,scmRef,field):
            data = None
            for name in self.cfgDB.keys():
                try:
                    if self.cfgDB[name].has_key(scmRef):
                        data = self.cfgDB[name][scmRef][field]['data']
                except KeyError:
                    raise

            return data

    def GetScm(self,scmRef):
            scm = None
            try:
                scm = self._GetFromDataFile(scmRef,'scm')
            except KeyError:
                raise

            return scm


    def GetRoot(self,scmRef):
            """
            get location from *.dat file
            """
            root = None
            try:
                root = self._GetFromDataFile(scmRef,'root')
            except KeyError:
                raise

            return root

    def GetAllScmRefs(self):
            scms=[]
            for name in self.cfgDB.keys():
                for scm in self.cfgDB[name]:
                    scms.append(scm)

            return scms

    def GetUserid(self):
        """
        This returns the user id for a given repository
        as defined by the refrenece, version and catagory
        """
        if self.scmRef == None or  self.ref == None or \
            self.ver == None or self.type == None:
            raise KeyError, "getuid: Params can't be empty"

        if self.debug:
            print "GetUserID(%s, %s, %s)" % \
            (self.scmRef, self.ver, self.type)

        try:
            userid = \
            self.db[self.scmRef][self.ref][self.ver][self.type]['misc'][0]
        except ( IndexError, KeyError):
            userid = self.userid
        except:
            raise

        if self.debug:
            print "GetUserid: %s" % userid

        return string.strip(userid)

    def PrimeDataDB(self,datafile):
        """ This parses the *.dat files
            and creates a mem resident
            dict for it
        """
        db = {}
        scms = self.cfgDataFileSections(datafile)
        for scm in scms:
            lines  = self.ParseDataFile(datafile,scm)
            for line in lines:
                uid = self.userid
                top = "N/A"
                branch = "N/A"

                try:
                    reference, version, type, location, branch ,\
                    top,uid =  line.split(',')
                    top = top.strip(' ')
                    uid = uid.strip(' ')
                except ValueError:
                    try:
                        reference, version, type, location, branch ,\
                        top =  line.split(',')
                    except ValueError:
                        try:
                            reference, version, type, location, branch ,\
                            =  line.split(',')
                        except ValueError:
                            try:
                                reference, version, type, location, \
                                =  line.split(',')

                            except ValueError:
                                raise
                except:
                    raise

                if len(uid) <= 0:
                    uid = self.userid
                if len(top) <= 0:
                    top = "N/A"

                type = type.strip(' ')
                reference = reference.strip(' ')
                version = version.strip(' ')
                location = location.strip(' ')
                branch = branch.strip(' ')

                d1 = {"%s" % scm : {"%s" % reference: { "%s" % version : \
                {"%s" % type: { 'location': "", 'branch': "", \
                'misc':["",""]}}}}}
                d2 = {"%s" % reference : { "%s" % version: \
                {"%s" % type: {'location': "", 'branch': "", \
                'misc':["",""]}}}}
                d3 = {"%s" % version :\
                {"%s" % type: {'location': "", 'branch': "", \
                'misc':["",""]}}}
                d4 = {"%s" % type: {'location': "", 'branch': "", \
                'misc':["",""]}}
                d5 = {'location': "", 'branch': "", \
                'misc':["",""]}

                if db.has_key(scm):
                    if db[scm].has_key(reference):
                        if db[scm][reference].has_key(version):
                            if db[scm][reference][version].has_key(type):
                                d5['location'] = location
                                d5['branch'] = branch
                                d5['misc'][0] = uid
                                d5['misc'][1] = top
                                db[scm][reference][version][type].update(d5)
                            else:
                                d4[type]['location'] = location
                                d4[type]['branch'] = branch
                                d4[type]['misc'][0] = uid
                                d4[type]['misc'][1] = top
                                db[scm][reference][version].update(d4)
                        else:
                            d3[version][type]['location'] = location
                            d3[version][type]['branch'] = branch
                            d3[version][type]['misc'][0] = uid
                            d3[version][type]['misc'][1] = top
                            db[scm][reference].update(d3)
                    else:
                        d2[reference][version][type]['location'] = location
                        d2[reference][version][type]['branch'] = branch
                        d2[reference][version][type]['misc'][0] = uid
                        d2[reference][version][type]['misc'][1] = top
                        db[scm].update(d2)
                else:
                    d1[scm][reference][version][type]['location'] = location
                    d1[scm][reference][version][type]['branch'] = branch
                    d1[scm][reference][version][type]['misc'][0] = uid
                    d1[scm][reference][version][type]['misc'][1] = top
                    db.update(d1)

        # save the db now
        self.db.update(db)

if __name__ == "__main__":
    db = {}
    s = ScmCfgDB(db)
    s.debug=1
    s.scmRef = None
    s.ref = "linus"
    s.ver = "2.6"
    s.type = "kernel"

    print "Test 1"
    print "Test 2"
    scm = s.GetScmRefByValue(s.ref, s.ver, s.type)
    print "SCMref: %s" % scm

    s.ref = "linus"
    s.ver = "2.6"
    s.type = "kernel"

    print "Test 3"
    try:
        s.scmRef = s.findScmRef()
    except KeyError:
        print "issue with findScm"
        sys.exit(1)

    print "scmRef: %s" % s.scmRef

    print "Test 4"
    print "userid %s" % s.GetUserid()

    print "SCM: %s" % s.GetScm(s.scmRef)
