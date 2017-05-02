#!/usr/bin/env python
# ---------------------------------------------------------------------
#  File:        cat.py
# ---------------------------------------------------------------------
import os, sys, re
from string import *
from time import sleep
from histutil import Ntuple, nameonly
from ROOT import *
from random import shuffle
# ---------------------------------------------------------------------    
def main():
    txtfiles = sys.argv[1:]
    if len(txtfiles) < 3:
        sys.exit('''
    Usage:
        ./cat.py file1 file2 output-file
''')
    recs = open(txtfiles[0]).readlines()
    header = recs[0]
    recs = recs[1:]
    for f in txtfiles[1:-1]:
        recs += open(f).readlines()[1:]
    shuffle(recs)
    recs.insert(0, header)
    print '\nwriting %s' % txtfiles[-1]
    open(txtfiles[-1], 'w').writelines(recs)
# ---------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "bye!"


