#!/bin/python

from setuptools import setup

import glob
import os

pkgname = 'rqt_launchtree'

#fgn: get all extra ressources:
configPath = os.path.join('config')
configList = glob.glob(os.path.join(configPath, "*"))

imagesPath = os.path.join('resource', 'img')
imagesList = glob.glob(os.path.join(imagesPath, "*"))
uifilesPath = os.path.join('resource', 'ui')
uifilesList = glob.glob(os.path.join(uifilesPath, "*"))


setup(
   name=pkgname,
   version='1.1.0',
   description='tool for displaying sts stack (launch-) information',
   license="STS",
   author='Nick Fiege',
   author_email='nick.fiege@streetscooter.eu',
   url='http://gitlab_al.streetscooter.eu/fgn/rqt_launchtree',
   packages=[ pkgname ],
   package_dir={pkgname: os.path.join('src', pkgname) },
   #this is necessary, so that the instlal will not zip everyting into an egg file
   #instead, everything wil lbe placed into /usr/local/lib/python2.7/dist-packages/start_utils-1.0-py2.7.egg/
   zip_safe = False, 
   scripts=[ os.path.join('scripts', pkgname) ],
   #https://docs.python.org/2/distutils/setupscript.html#installing-additional-files
   data_files=[
                (configPath, configList),
                (imagesPath, imagesList),
                (uifilesPath, uifilesList),
              ]
)