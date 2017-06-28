#!/usr/bin/env python
# ----------------------------------------------------------------------------
#  File:        makeAllLimitHists.py
#  Created:     07-Jun-2017 HBP    
# ----------------------------------------------------------------------------
import os, sys, re
from string import *
from glob import glob
# ----------------------------------------------------------------------------
def main():
    filenames = glob('ntuples/ntuple_*.root')
    filenames.sort()
    for filename in filenames:
        cmd = 'makeLimitHists.py %s' % filename
        print cmd
        os.system(cmd)
# ----------------------------------------------------------------------------
try:     
    main()
except KeyboardInterrupt:
    print '\nciao!\n'
