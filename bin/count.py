#!/usr/bin/env python
# ----------------------------------------------------------------------------
#  File:        count.py
#  Description: sum weights of ntuples
#  Created: ??-Oct-2016 HBP
#           21-Oct-2016 apply to new ntuples from Nic.
# ----------------------------------------------------------------------------
import os, sys, re
from ROOT import *
from string import *
from rgsutil import *
from time import sleep
# ----------------------------------------------------------------------------
def main():
    setStyle()
    gStyle.SetOptStat('eimr')
    
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        sys.exit('''
    Usage:
        python count.py root-file [sample] [fstate]

    Example:
        python count.py ntuple_higgs.root 1
        ''')    
    filenames = [filename]
    
    if len(sys.argv) > 2:
        sample = atoi(sys.argv[2])
    else:
        sample = 0

    if len(sys.argv) > 3:
        fstate = atoi(sys.argv[3])
    else:
        fstate = 0        
        
    # do some PyRoot magic to read from tree
    struct = '''
    struct Event{
    float f_weight;
    int f_sample;
    int f_finalstate;
    float f_lept1_pt;
    float f_lept2_pt;
    float f_lept3_pt;
    float f_lept4_pt;
    };'''
    
    gROOT.ProcessLine(struct)
    from ROOT import Event
    event = Event()
    Lumi = 1.0
    
    # loop over files    
    for filename in filenames:
        # open root file
        ntuple = TFile(filename)
        # get tree
        tree = ntuple.Get("HZZ4LeptonsAnalysisReduced")
        tree.SetBranchAddress('f_weight',
                              AddressOf(event, 'f_weight'))
        
        tree.SetBranchAddress('f_sample',
                              AddressOf(event, 'f_sample'))

        tree.SetBranchAddress('f_finalstate',
                              AddressOf(event, 'f_finalstate'))        

        for ii in xrange(4):
            jj = ii+1
            field = 'f_lept%d_pt' % jj
            print field
            tree.SetBranchAddress(field,
                                  AddressOf(event, field))
        
        # now loop over events in current file
        nevents = tree.GetEntries()
        print "\n\t=> number of entries: %d" % nevents
        
        gname = replace(filename, '.root', '')
        gname = replace(gname, 'ntuple', 'fig')
        if sample < 0:
            gname += "_not_sample_%d" % abs(sample)
        elif sample > 0:
            gname += "_sample_%d" % sample

        if fstate > 0:
            gname += "_fstate_%d" % fstate
            
        c = TCanvas(gname, gname, 10, 10, 800, 800)
        c.Divide(2, 2)

        h = []
        for ii in xrange(4):
            jj = ii+1
            hname = 'h_l%dpt' % jj
            h.append(mkhist1(hname, '#font[12]{p}_{Tl%d}' % jj, '',
                                 150, 0, 300))
            h[ii].SetFillColor(kBlue+2)
            h[ii].SetFillStyle(3001)
            
        w1 = 0.0
        w2 = 0.0
        for index in xrange(nevents):
            tree.GetEntry(index)
            if sample < 0:
                if event.f_sample == abs(sample): continue
            elif sample > 0:
                if event.f_sample != sample: continue

            if fstate > 0:
                if event.f_finalstate != fstate: continue
    
            w = event.f_weight*Lumi
            w1 += w
            w2 += w*w

            pt = []
            for ii in xrange(4):
                jj = ii+1
                field = 'f_lept%d_pt' % jj
                pt.append(event.__getattribute__(field))
            pt.sort()
            pt.reverse()
            
            for ii in xrange(4):
                jj = ii+1
                h[ii].Fill(pt[ii], w)
                
            if index % 10000 == 0:
                for ii in xrange(4):
                    jj = ii+1
                    c.cd(jj)
                    h[ii].Draw('hist')
                c.Update()
                gSystem.ProcessEvents()
    w2 = sqrt(w2)
    print '\n\t=> total: %10.3f +/- %-10.3f events\n' % (w1, w2)
    
    for ii in xrange(4):
        jj = ii+1
        c.cd(jj)
        h[ii].Draw('hist')
        c.Update()
    gSystem.ProcessEvents()
    c.SaveAs('.png')
    sleep(5)
# -------------------------------------------------------------------------
try:     
    main()
except KeyboardInterrupt:
    print '\nciao!\n'
