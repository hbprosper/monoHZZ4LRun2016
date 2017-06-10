#!/usr/bin/env python
import os, sys, re
from histutil import Table

def main():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        sys.exit('''
    Usage:
        checkme.py filename
    ''')

    table = Table(filename)
    print filename, len(table)
    cVBF = 0
    cnonVBF = 0
    for ii, row in enumerate(table):
        sample = row('f_sample')
        if sample == 1:
            cVBF += 1
        else:
            cnonVBF += 1
    print cVBF, cnonVBF
    
try:
    main()
except KeyboardInterrupt:
    print '\nciao!\n'
    
