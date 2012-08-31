"""
The SCM module contains a common interface to
some of the other scm programs such as cvs and git
"""
import os
import re
import ConfigParser

class ScmCfg():
    def __init__(self):
        self.noise=0
        self.debug=0
        self.trace=0
        self.maincfg = ConfigParser.ConfigParser()
        self.cfgdir, self.cfgfile = self.find_conf()

        # get user id from main conf file
        try:
            self.userid = self._raw_parse_cfgfile("defaults", "userid")
        except ConfigParser.NoSectionError:
            raise

    def _raw_parse_cfgfile(self, cfg_sec, cfg_key):
        """ Gets the UserID from the config file
        """
        data = ""
        try:
            self.maincfg.read(self.cfgfile)
        except:
            raise
        else:
            try:
                data = self.maincfg.get(cfg_sec, cfg_key)
            except ConfigParser.NoSectionError:
                return None
            except:
                raise
            else:
                return data.strip(' ')

    def _ParseDataFileByType(self, file, type, filter="None"):
        """ Returns test config make
        """
        if self.debug:
            print"_ParseDataFileByType(%s, %s, %s)" % (file, type, filter)

        options = []

        section_begin = 0
        exclude_ws=re.compile('\s')
        exclude_comment=re.compile('^#')
        section_filter=re.compile('^\\[+[a-z]+\\]',re.IGNORECASE)

        try:
            c = open(os.path.join(self.cfgdir, file), 'r')
        except:
            raise
        else:
            try:
                lines = c.readlines()
                c.close()
            except:
                raise
            else:
                for line in lines:
                    if exclude_ws.match(line):
                        continue
                    if exclude_comment.match(line):
                        continue
                    if section_filter.match(line):
                        section = line.strip('[]\n')

                        if filter == 'section':
                            options.append(section.strip(' \n'))
                            section_begin = 0
                        else:
                            if section_begin:
                                break

                            if section != type:
                                continue

                            if section == type:
                                section_begin = 1
                                continue

                    if section_begin:
                        options.append(line.strip(' \n'))

                if len(options) == 0:
                    return None
                else:
                    return options


    def cfgDataFileSections(self, file):
            return self._ParseDataFileByType(file,'All', 'section')

    def ParseDataFile(self, file, type):
            return self._ParseDataFileByType(file,type)

    def GetCfgFiles(self):
        if self.noise:
            print "GetCfgFiles"
        files = []
        section = "configs"

        c = ConfigParser.ConfigParser()
        try:
            c.read(os.path.join(self.cfgdir,self.cfgfile))
        except:
            raise

        options = []
        try:
            options = c.options(section)
        except ConfigParser.NoSectionError:
            return None

        for opt in options:
            data = c.get(section, opt).strip(' ')
            files.append(os.path.join(self.cfgdir, data))

        return files


    def find_conf(self):
        """
        find the config files.
        Order is $HOME/.scmpy
        then /etc/scmpy.d
        then devel location.
        """
        config_file = None
        config_dir = None

        for cfgdir in [os.getcwd()+"/data", os.environ["HOME"]+"/.scmpy", "/etc/scmpy.d"]:
            config_file=("%s/scmpy.conf" % cfgdir)
            if os.path.isfile(config_file):
                break

        if config_file:
            config_dir = os.path.dirname(config_file)

        if self.debug:
            print "Conf dir: %s, file: %s" % (config_dir, config_file)

        return (config_dir, config_file)

    def aliasToCmdName(self, scm, alias):
        if self.debug:
            print "(%s)" % alias
        alias = self._raw_parse_cfgfile(scm, alias)
        return alias


if __name__ == "__main__":

    cfg = ScmCfg()
    cfg.debug=1

    print "Test 1"
    print "Userid: %s" % cfg.userid

    print "Test 2"
    print "cfgfiles:" ,
    for file in cfg.GetCfgFiles():
        print "%s " % file,
    print ""
    print "Alias for clone git is %s" % cfg.aliasToCmdName("git", "clone")

