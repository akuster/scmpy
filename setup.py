#
import os
import sys
import glob
from distutils.core import setup

setup ( name='scmpy',
        description='Python scm wrapper',
        long_description='A python scm wrapper to facilitate simpler usage for many scm',
        author='Armin Kuster',
        author_email='akuster@kama-ania.net',
        version='0.1',
        license='GPL2',
        maintainer='Armin Kuster',
        packages=['Scmpy'],
        scripts=[os.path.join('bin', 'scmpy')],
        data_files=[(os.path.join(os.environ['HOME'], '.scmpy'), glob.glob(".scmpy/*.conf") + glob.glob(".scmpy/*.dat") + glob.glob(".scmpy/*.dft"))],
        classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Python Software Foundation License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: Linux, Mac OS',
        'Programming Language :: Python',
        'Topic :: Software Development',
],
        )


