#!/usr/bin/env python
# ----------------------------------------------------------------------------
#  File:        vbfyields.py
#  Description: sum weights of ntuples
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
# ----------------------------------------------------------------------------
def main():
    
    # do some PyRoot magic to read from tree
    struct = '''
    struct Event{
    Float_t f_weight;
    Float_t f_mass4l;
    float   f_massjj;
    int     f_finalstate;
    int     f_sample;
    int     f_outlier;
    Float_t f_lept1_pt;
    Float_t f_lept2_pt;
    Float_t f_lept3_pt;
    Float_t f_lept4_pt;
    };'''
    gROOT.ProcessLine(struct)
    from ROOT import Event
    event = Event()

    treename = "HZZ4LeptonsAnalysisReduced"


    # construct name of yield file
    yieldfile = "yields_VBF_%4.4d_%4.4d.txt" % (MASSMIN, MASSMAX)
    print yieldfile
    print
    
    out = open(yieldfile, 'w')
    record = 'Integrated luminosity: 36/fb'
    out.write('%s\n' % record)
    print record
    
    record = 'Cuts: (%d <= m4l <= %d GeV) and (njets >= 2)' % \
      (MASSMIN, MASSMAX)
    out.write('%s\n' % record)
    print record
    
    record = ctime()
    out.write('%s\n' % record)
    print record

    record = '\n%-16s %19s %21s' %\
      ('sample', 'njet >= 2', 'njet >= 0')    
    print record
    out.write('%s\n' % record)
    
    record = '-' * 58
    print record
    out.write('%s\n' % record)
    
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

        for namen in ['weight',
                      'mass4l',
                      'massjj',
                      'finalstate',
                      'outlier',
                      'sample']:
            field = 'f_%s' % namen
            tree.SetBranchAddress(field, AddressOf(event, field))
        for ii in xrange(4):
            jj = ii+1
            field = 'f_lept%d_pt' % jj
            tree.SetBranchAddress(field, AddressOf(event, field))

        # now loop over events in current file
        nevents = tree.GetEntries()
        background = name == 'bkg'
        higgs = name == 'higgs'
        data = name == 'data'
        
        # counts

        T1 = 0.0
        C1 = 0.0
        T2 = 0.0
        C2 = 0.0
        
        t1 = 0.0
        c1 = 0.0
        c2 = 0.0
        v1 = 0.0
        v2 = 0.0
        g1 = 0.0
        g2 = 0.0
        o1 = 0.0
        o2 = 0.0

        count1 = 0
        count2 = 0
        count3 = 0
        for index in xrange(nevents):
            tree.GetEntry(index)

            if event.f_mass4l < 80: continue
            if event.f_mass4l > 480: continue  

            w = event.f_weight

            if background:
                T1 += w
                T2 += w*w
                
                if event.f_outlier: continue
                    
                C1 += w
                C2 += w*w
            
            if event.f_mass4l < MASSMIN: continue
            if event.f_mass4l > MASSMAX: continue            
            
            t1 += w

            # require 2-jets
            
            if event.f_massjj <= 0:    continue

            if background:
                if event.f_sample == ZZ:
                    count1 += 1 
                    v1 += w
                    v2 += w*w
                else:
                    count2 += 1
                    g1 += w
                    g2 += w*w
                
            if higgs:
                if   event.f_sample == VBF:
                    count1 += 1 
                    v1 += w
                    v2 += w*w
                elif event.f_sample == ggF:
                    count2 += 1
                    g1 += w
                    g2 += w*w
                else:
                    count3 += 1
                    o1 += w
                    o2 += w*w
            c1 += w
            c2 += w*w
            
        ntuple.Close()

        v2 = sqrt(v2)
        g2 = sqrt(g2)
        c2 = sqrt(c2)
        o2 = sqrt(o2)
        
        if background:
            scale = T1 / C1
            s2 = scale*sqrt(T2/T1/T1 + C2/C1/C1)
            T2 = sqrt(T2)
            C2 = sqrt(C2)
            
            t1 *= scale
            c1 *= scale
            c2 *= scale
                
        record = '%-16s %10.1f +/- %-10.2f\t%10.1f' % (name, c1, c2, t1)
        print record
        out.write('%s\n' % record)

        if data:
            print
            out.write('\n')
            
        if higgs:
            
            record = '%-16s %10.2f +/- %-10.2f %7d' % \
              ('  VBF', v1, v2, count1)
            print record
            out.write('%s\n' % record)


            record = '%-16s %10.2f +/- %-10.2f %7d' % \
              ('  ggF', g1, g2, count2)
            print record
            out.write('%s\n\n' % record)

            record = '%-16s %10.2f +/- %-10.2f %7d' % \
              ('  other', o1, o2, count3)
            print record
            out.write('%s\n' % record)            

            print
            out.write('\n')
            
            s += v1
            b += g1

        if background:

            scale = T1 / C1
            s2 = scale*sqrt(T2/T1/T1 + C2/C1/C1)
            T2 = sqrt(T2)
            C2 = sqrt(C2)

            v1 *= scale
            v2 *= scale

            g1 *= scale
            g2 *= scale            

            b += v1
            
            record = '%-16s %10.2f +/- %-10.2f %7d' % \
              ('  ZZ', v1, v2, count1)
            print record
            out.write('%s\n' % record)
            
            record = '%-16s %10.2f +/- %-10.2f %7d' % \
              ('  non-ZZ', g1, g2, count2)
            print record
            print
            out.write('%s\n\n' % record)                  

            record = 'total bkg with m4l in [80, 480] GeV'
            print record
            out.write('%s\n' % record)
            
            record = '%-16s \t\t       %10.2f +/- %-10.2f' % \
              ('  with outliers', T1, T2)
            print record
            out.write('%s\n' % record)

            record = '%-16s \t\t       %10.2f +/- %-10.2f' %\
              ('  no outliers', C1, C2)
            print record
            out.write('%s\n' % record)

            record = '%-16s \t\t         %8.3f +/-%-8.3f' % \
              ('  scale factor', scale, s2)
            print record
            out.write('%s\n' % record)              

    L = 100.0
    scale = L/36.0
    s *= scale
    b *= scale
    x = s / b
    K = b * ((1 + x) * log(1 + x) - x)
    Z = sqrt(2 * K)

    #
    print
    out.write('\n')
    
    record = '%-16s' % ('VBF significance for 100/fb (using s=VBF, b=ggF+ZZ)')
    print record
    out.write('%s\n' % record)

    record = '%-16s \t %8.3f' % ('  sig', s)
    print record
    out.write('%s\n' % record)

    record = '%-16s \t %8.3f' % ('  bkg', b)
    print record
    out.write('%s\n' % record)    
    
    record = '%-16s \t %8.3f' % ('  S/N', x)
    print record
    out.write('%s\n' % record)

    record = '%-16s \t %8.3f' % ('  Z', Z)
    print record
    out.write('%s\n' % record)    
    
    out.close()
# -------------------------------------------------------------------------
try:     
    main()
except KeyboardInterrupt:
    print '\nciao!\n'
