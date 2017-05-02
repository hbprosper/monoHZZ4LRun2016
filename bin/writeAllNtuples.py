#!/usr/bin/env python
# ----------------------------------------------------------------------------
#  File:        writeAll.py
#  Description: call writeNtuples.py on filelists
#  Created:     29-Oct-2016 HBP    
# ----------------------------------------------------------------------------
import os, sys, re
from string import *
# ----------------------------------------------------------------------------
def main():
    filenames = map(strip, open("filelists.txt").readlines())
    for filename in filenames:
        cmd = './writeNtuples.py %s' % filename
        print cmd
        os.system(cmd)
# ----------------------------------------------------------------------------
try:     
    main()
except KeyboardInterrupt:
    print '\nciao!\n'
