#!/usr/bin/env python
# ---------------------------------------------------------------------------
#  File:        makeFilelists.py
#  Created: 21-Oct-2016 HBP
# ---------------------------------------------------------------------------
import os, sys, re
from ROOT import *
from string import *
from math import *
from glob import glob
# ---------------------------------------------------------------------------
finalstate= re.compile('(?<=histos).*(?=_25ns)')
sample    = re.compile('(?<=output_).*(?=.root)')
isdata    = re.compile('Run20')
ishiggs   = re.compile('HToZZ')
issignal  = re.compile('MZP|Zprime|ZpBaryonic')
sigmass   = re.compile('MZp.*(?=_13TeV)|MZP.*')
masses    = re.compile('[0-9]+')
# ---------------------------------------------------------------------------
def main():
    if len(sys.argv) > 1:
        filenames = sys.argv[1:]
    else:
        sys.exit('''
    Usage:
        python makeFilelists.py root-files

    Example:
        python makeFilelists.py store/histos4mu_25ns/*.root
        ''')    

    # get final state (4e, 4mu, 2e2mu)
    name = finalstate.findall(filenames[0])
    if len(name) == 0:
        sys.exit("** can't get sample name from %s" % filenames[0])
    name = name[0]
    print "\n\tfinal state: %s\n" % name
    
    dout = open('store/filelist_%s_data.txt'  % name, 'w')
    hout = open('store/filelist_%s_higgs.txt' % name, 'w')
    bout = open('store/filelist_%s_bkg.txt'   % name, 'w')
    
    # loop over files
    dcount = 0
    hcount = 0
    bcount = 0    
    for filename in filenames:
        print filename       
        # check whether this is a data, Higgs, or signal files
        isData   = isdata.findall(filename)   != []
        isHiggs  = ishiggs.findall(filename)  != []
        Signal   = issignal.findall(filename)
        isSignal = Signal != []

        if isData:
            dout.write('%5d %s\n' % (dcount, filename))
            dcount += 1
        elif isHiggs:
            hout.write('%5d %s\n' % (hcount, filename))
            hcount += 1
        elif isSignal:
            m = sigmass.findall(filename)
            signame = Signal[0][:6]
            # hack
            if signame == 'MZP': signame = 'Zprime'
            mval = map(lambda x: atoi(x), masses.findall(m[0]))
            MZpmass = mval[0]
            MAmass  = mval[-1]
            m = (name, signame, MZpmass, MAmass)
            sout = open('store/filelist_%s_%s_MZp%5.5d_MA%5.5d.txt' % m, 'w')
            sout.write('%5d %s\n' % (0, filename))
            sout.close()
        else:
            bout.write('%5d %s\n' % (bcount, filename))
            bcount += 1

    dout.close()
    hout.close()
    bout.close()
# -------------------------------------------------------------------------
try:     
    main()
except KeyboardInterrupt:
    print '\nciao!\n'
