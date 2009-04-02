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


data_files.append(('share/thinblue/static', get_files("webpanel/static") ))
data_files.append(('share/thinblue/templates', get_files("webpanel/templates") ))

data_files.append(('/var/lib/thinblue/files', ["data/thinetic.jpg"] ))
data_files.append(('/var/lib/thinblue/sessions', ["data/.placeholder"] ))

data_files.append(('/etc/logrotate.d', ["data/thinblue.conf"] ))


setup(name='ThinBlue',
      description = 'Send files using 2 bluetooth devices',
      version='0.3.1',
      author = 'Mario Izquierdo',
      author_email = 'mario.izquierdo@thinetic.es',
      url = 'http://www.thinetic.es',
      license = 'GPLv2',
      platforms = ['linux'],
      keywords = ['bluetooth', 'files', 'daemon'],
      packages=['thinblue' ],
      package_dir = {'':''},
      scripts=['thinblue.py', 'thinblueweb.py'],
      data_files=data_files
      )

