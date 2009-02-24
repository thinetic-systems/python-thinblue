#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 
# This script is inspired by the debian package python-chardet
import os
import glob
from distutils.core import setup
from distutils.command.build import build

data_files = []


def get_files(ipath):
    files = []
    for afile in glob.glob('%s/*'%(ipath) ):
        if os.path.isfile(afile):
            files.append(afile)
    return files


data_files.append(('share/python-thinblue/webpanel', get_files("webpanel") ))

data_files.append(('/var/lib/thinblue/data', ["data/thinetic.jpg"] ))

data_files.append(('/etc/logrotate.d', ["data/python-thinblue.logrotate.conf"] ))


setup(name='ThinBlue',
      description = 'Send files using 2 bluetooth devices',
      version='0.0.1',
      author = 'Mario Izquierdo',
      author_email = 'mario.izquierdo@thinetic.es',
      url = 'http://www.thinetic.es',
      license = 'GPLv2',
      platforms = ['linux'],
      keywords = ['bluetooth', 'files', 'daemon'],
      packages=['thinblue' ],
      package_dir = {'':''},
      scripts=['thinblue.py'],
      data_files=data_files
      )

