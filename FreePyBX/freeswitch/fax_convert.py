#!/usr/bin/python
#

import os,sys
from subprocess import call


call("convert "+str(sys.argv[1])+" "+str(sys.argv[2]), shell=True)

os.remove(str(sys.argv[1]))
