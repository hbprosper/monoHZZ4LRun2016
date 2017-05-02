#!/usr/bin/env python
# ----------------------------------------------------------------------------
#  File:        countall.py
#  Description: sum weights of ntuples HBP
# ----------------------------------------------------------------------------
import os, sys, re
from ROOT import *
from string import *
from math import *
# ----------------------------------------------------------------------------
def main():
    if len(sys.argv) > 1:
        filelists = sys.argv[1:]
    else:
        sys.exit(
'''Usage
        ./countall.py filelist1 filelist2 ...
        ''')
        
    for filename in filelists:
        cmd = './count.py %s' % filename
        print 
        print cmd
        os.system(cmd)
# -------------------------------------------------------------------------
try:     
    main()
except KeyboardInterrupt:
    print '\nciao!\n'
