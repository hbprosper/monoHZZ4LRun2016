#!/usr/bin/env python
# ----------------------------------------------------------------------------
#  File:        computeAllLimits.py
#  Created:     07-Jun-2017 HBP    
# ----------------------------------------------------------------------------
import os, sys, re
from string import *
from glob import glob
# ----------------------------------------------------------------------------
def main():
    filenames = glob('configs/histos_*100.cfg')
    filenames.sort()
    for filename in filenames:
        cmd = 'computeLimit.py %s' % filename
        print cmd
        os.system(cmd)
# ----------------------------------------------------------------------------
try:     
    main()
except KeyboardInterrupt:
    print '\nciao!\n'
