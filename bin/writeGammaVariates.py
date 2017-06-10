#!/usr/bin/env python
#-----------------------------------------------------------------------------
# File:        writeGammaVariates.py
# Description: write gamma variates to a file using a gamma distribution
#              with unit mean and standard deviation "sigma"
# Created:     06-Jun-2017 HBP Bari
#-----------------------------------------------------------------------------
import os, sys, re
from string import *
from random import gammavariate
# ---------------------------------------------------------------------------
def USAGE():
    sys.exit('''
    Usage:
        writeGammaVariates.py rel-unc [filename=gammavariate.txt] [ntrials=400]
        ''')    
def main():
    if len(sys.argv) < 2:
        USAGE()
        
    relunc = atof(sys.argv[1])

    if len(sys.argv) > 2:
        outfilename = sys.argv[2]
    else:
        outfilename = 'gammavariates.txt'

    try:
        x = atoi(outfilename)
        USAGE()
    except:
        pass
    
    if len(sys.argv) > 3:
        ntrials = atoi(sys.argv[3])        
    else:
        ntrials = 400

    print "-" * 60
    print "relative uncertainty:       %7.2f" % relunc
    print "output gamma variate file:     %s"    % outfilename
    print "sample size:                %4d"   % ntrials
    
    u = relunc*relunc
    alpha = 1.0/u
    beta  = u
    out = open(outfilename, 'w')
    for ii in xrange(ntrials):
        x = gammavariate(alpha, beta)
        out.write('%10.4f\n' % x)
    out.close()
#-----------------------------------------------------------------------------
try:
    main()    
except KeyboardInterrupt:
    print "ciao!"
    
