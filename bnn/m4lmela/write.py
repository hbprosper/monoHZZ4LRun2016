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
    print "\n\n==> filename: %s" % filename
    
    total1  = 0.0
    total2  = 0.0
    etotal2 = 0.0
    records = []
    fmt = ' %15.3e' * 13 + '\n'

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
           event.f_D_bkg_kin,
           event.f_pt4l,
           event.f_pfmet,
           event.f_mT,
           event.f_mass4l,
           event.f_Z1mass,
           event.f_Z2mass,
           event.f_angle_costhetastar,
           event.f_angle_costheta1,
           event.f_angle_costheta2,
           event.f_angle_phi,
           event.f_angle_phistar1)
        records.append(record)
    shuffle(records)
    fmt = ' %s' * 13 + '\n'
    
    record = fmt % ('f_weight',
                    'f_D_bkg_kin',
                    'f_pt4l',
                    'f_pfmet',
                    'f_mT',
                    'f_mass4l',
                    'f_Z1mass',
                    'f_Z2mass',
                    'f_angle_costhetastar',
                    'f_angle_costheta1',
                    'f_angle_costheta2',
                    'f_angle_phi',
                    'f_angle_phistar1')
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
    wrout('../../ntuple_bkg.root',   'bkg')
    wrout('../../ntuple_higgs.root', 'sig')
    # unweight and mix
    open('vars.txt', 'w').writelines(['f_mass4l\n','f_D_bkg_kin\n'])
    cmd = '''
    unweight.py bkg_weighted.txt bkg.dat 5000
    unweight.py sig_weighted.txt sig.dat 5000
    mixsigbkg.py -v vars.txt m4lmela
'''
    print cmd
    os.system(cmd)
# ---------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "bye!"


