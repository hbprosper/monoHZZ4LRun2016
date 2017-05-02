#!/usr/bin/env python
# ---------------------------------------------------------------------------
#  File:        mergeAllNtuples.py
#  Description: call mergeNtuples.py on filelists
#  Created:     29-Oct-2016 HBP    
# ---------------------------------------------------------------------------
import os, sys, re
from string import *
# ---------------------------------------------------------------------------
def main():
    filenames = map(strip, open("mergelists.txt").readlines())
    for filename in filenames:
        filename = replace(filename, '4mu', '*mu')
        cmd = './mergeNtuples.py %s' % filename
        print cmd
        os.system(cmd)
# ---------------------------------------------------------------------------
try:     
    main()
except KeyboardInterrupt:
    print '\nciao!\n'
