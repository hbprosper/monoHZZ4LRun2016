#!/usr/bin/env python
# ----------------------------------------------------------------------------
#  File:        writeOut.py
#  Description: write out data
#  Created: ??-Oct-2016 HBP
#           21-Oct-2016 apply to new ntuples from Nic.
# ----------------------------------------------------------------------------
import os, sys, re
from ROOT import *
from string import *
from math import *
from glob import glob
from time import ctime
# ----------------------------------------------------------------------------
MASSMIN = 100.0
MASSMAX = 150.0
ggF     =  0
VBF     =  1
ZZ      = 27
VARS = '''
    float   f_weight
    float   f_pt4l
    float   f_eta4l
    float   f_mass4l
    float   f_massjj
    float   f_deltajj
    float   f_Z1mass
    float   f_Z2mass
    float   f_angle_costhetastar
    float   f_angle_costheta1
    float   f_angle_costheta2
    float   f_angle_phi
    float   f_angle_phistar1
    float   f_njets_pass
    int     f_finalstate
    int     f_sample
    int     f_outlier
    float   f_jet1_pt
    float   f_jet1_eta
    float   f_jet1_phi
    float   f_jet2_pt
    float   f_jet2_eta
    float   f_jet2_phi
'''
VARS = map(split, split(strip(VARS), '\n'))
# ----------------------------------------------------------------------------
def main():
    
    # do some PyRoot magic to read from tree
    struct = 'struct Event {'
    for ftype, field in VARS:
        struct += '%s %s; ' % (ftype, field)
    struct += '};'
    gROOT.ProcessLine(struct)
    from ROOT import Event
    event = Event()
    
    treename = "HZZ4LeptonsAnalysisReduced"
    
    # loop over files

    s = 0.0
    b = 0.0    
    for name in ['data', 'higgs', 'bkg']:

        filename = 'ntuple_%s.root' % name
       
        # open root file
        ntuple = TFile(filename)
        if not ntuple.IsOpen():
            sys.exit("** can't open file %s" % filename)

        # get tree
        tree = ntuple.Get(treename)
        if not tree:
            sys.exit("** can't get tree %s" % treename)

        for ftype, field in VARS:
            tree.SetBranchAddress(field, AddressOf(event, field))

        # now loop over events in current file
        nevents = tree.GetEntries()

        print '\t%s\t%10d' % (filename, nevents)
        
        # counts
        t1 = 0.0
        t2 = 0.0
        count = 0
        records = []
        for index in xrange(nevents):
            tree.GetEntry(index)

            if event.f_mass4l < 100:   continue
            if event.f_mass4l > 150:   continue
            if event.f_outlier:        continue
            if event.f_njets_pass < 1: continue

            w = event.f_weight
            
            t1 += w
            t2 += w * w

            record = [0]*len(VARS)
            for ii, (ftype, field) in enumerate(VARS):
                record[ii] = event.__getattribute__(field)
            records.append(record)

            if count % 10000 == 0:
                print count
                
            count += 1            

        #tree.ResetBranchAddresses()
        ntuple.Close()
        
        # write out training data
        if name == 'data':
            outfilename = 'mvd_%s.txt' % name
        else:
            outfilename = 'mvd_%s_train_w.txt' % name
            
        print '\nwriting: %s\n' % outfilename
        
        out = open(outfilename, 'w')
        header = ''
        for ii, (ftype, field) in enumerate(VARS):
            header += '%s ' % field
        out.write('%s\n' % header)

        if name == 'data':
            ntrain = len(records)
        else:
            scale = 0.667
            ntrain = int(scale * len(records))
            
        for jj, record in enumerate(records[:ntrain]):
            rec = ''
            for ii, (ftype, field) in enumerate(VARS):
                if ftype[0] == 'f':
                    rec += ' %9.3e' % record[ii]
                else:
                    rec += '  %9d' % record[ii]
            out.write('%s\n' % rec)
        out.close()

        if name == 'data':
            print 'data count: %d' % ntrain
            continue
        
        c1 = scale * t1
        c2 = scale * t2
        neff = int(c1 * c1 / c2)
        print 'effective count: %d' % neff
        
        os.system('unweight.py %s %s %d' % (outfilename,
                                             replace(outfilename,
                                                         '_w.txt', '_u.txt'),
                                                neff))

        # write out test data
        outfilename = 'mvd_%s_test_w.txt' % name
        print '\nwriting: %s\n' % outfilename
        out = open(outfilename, 'w')
        header = ''
        for ii, (ftype, field) in enumerate(VARS):
            header += '%s ' % field
        out.write('%s\n' % header)

        for jj, record in enumerate(records[ntrain:]):
            rec = ''
            for ii, (ftype, field) in enumerate(VARS):
                if ftype[0] == 'f':
                    rec += ' %9.3e' % record[ii]
                else:
                    rec += ' %9d' % record[ii]
                    
            out.write('%s\n' % rec)
        out.close()

        scale = 1.0 - scale
        c1 = scale * t1
        c2 = scale * t2
        neff = int(c1 * c1 / c2)
        print 'effective count: %d' % neff
        
        os.system('unweight.py %s %s %d' % (outfilename,
                                             replace(outfilename,
                                                         '_w.txt', '_u.txt'),
                                                neff))
# -------------------------------------------------------------------------
try:     
    main()
except KeyboardInterrupt:
    print '\nciao!\n'
