#!/usr/bin/env python
# ---------------------------------------------------------------------
#  File:        write.py
#  Description: write out training data
#  Created:     28-Apr-2017 Harrison B. Prosper
# ---------------------------------------------------------------------
import os, sys, re
from string import *
from time import sleep
from histutil import Ntuple, nameonly
from ROOT import *
from random import shuffle
# ---------------------------------------------------------------------
MASSMIN =  70
MASSMAX = 170

def wrout(filename, name):
    treename   = "HZZ4LeptonsAnalysisReduced"  # name of Root tree 
    weightname = "f_weight"  # name of event weight variable
        
    ntuple = Ntuple(filename, treename)
    size   = len(ntuple)
    if find(filename, 'SM') > 0:
        ntrain = 50000
    else:
        ntrain = 3000
        
    print "\n\n==> filename: %s" % filename
    
    total1  = 0.0
    total2  = 0.0
    etotal2 = 0.0
    records = []
    fmt = ' %15.3e' * 4 + '\n'

    count = 0
    for ii, event in enumerate(ntuple):
        if ii % 10000 == 0:
            print '.',
            sys.stdout.flush()
        
        if event.f_outlier: continue
        if event.f_mass4l < MASSMIN: continue
        if event.f_mass4l > MASSMAX: continue
            
        total1  += 1.0
        total2  += event.f_weight
        etotal2 += event.f_weight**2
        
        record = fmt % \
          (event.f_weight,
           event.f_mass4l,
           event.f_D_bkg_kin,
           event.f_pfmet)
        records.append(record)
        
        count += 1
        if count >= ntrain: break
            
    shuffle(records)
    fmt = ' %s' * 4 + '\n'
    
    record = fmt % ('f_weight',
                    'f_mass4l',
                    'f_D_bkg_kin',
                    'f_pfmet')
    records.insert(0, record)
    outfilename = '%s_weighted.txt' % name
    print
    print outfilename
    open(outfilename, 'w').writelines(records)

    ecount = total2**2/etotal2
    print
    print 'training sample from file %s' % filename
    print "\ttotal:                       %10d events" % size
    print "\ttotal (without outliers):    %10.0f events" % total1
    print "\teffective total:             %10.0f events" % ecount

    print
# ---------------------------------------------------------------------    
def main():
    wrout('../../ntuple_ZpBary_MZp00100_MA00010.root',  'ZpBary')
    wrout('../../ntuple_Zprime_MZp00600_MA00300.root',  'Zprime1')
    wrout('../../ntuple_Zprime_MZp01700_MA00300.root',  'Zprime2')
    wrout('../../ntuple_SM.root',   'bkg')
# ---------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "bye!"


