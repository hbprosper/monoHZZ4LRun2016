#!/usr/bin/env python
# ----------------------------------------------------------------------------
#  File:        getYield.pt
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
finalstate= re.compile('(?<=histos).*(?=_25ns)')
sample    = re.compile('(?<=output_).*(?=.root)')
isdata    = re.compile('Run20')
ishiggs   = re.compile('HToZZ')
issignal  = re.compile('MZp|MZP|Zprime|ZpBaryonic')
# ----------------------------------------------------------------------------
def main():
    if len(sys.argv) > 1:
        filenames = sys.argv[1:]
    else:
        sys.exit('''
    Usage:
        python getYields.py root-files

    Example:
        python getYields.py store/histos4e_25ns/*.root
        ''')    

    # get final state (4e, 4mu, 2e2mu)
    name = finalstate.findall(filenames[0])
    if len(name) == 0:
        sys.exit("** can't get sample name from %s" % filenames[0])

    name = name[0]

    # construct name of yield file
    yieldfile = "yields_%s.txt" % name
    print yieldfile
    
    out = open(yieldfile, 'w')
    record = 'Yields (70 < m4l < 170 GeV): %s\n' % ctime()
    out.write('%s\n' % record)
    print record
    
    record = '%-48s  %7s %10s %10s' % \
      ('sample', 'count', 'yield', 'dyield')
    print record
    out.write('%s\n' % record)

    # lists for data, higgs, signal, and background
    datarecs = []
    higgsrecs= []
    sigrecs  = []
    bkgrecs  = []

    # counts for data, higgs, and background
    t_d1 = 0.0
    t_d2 = 0.0
    t_h1 = 0.0
    t_h2 = 0.0
    t_b1 = 0.0
    t_b2 = 0.0


    d1 = 0.0
    d2 = 0.0
    h1 = 0.0
    h2 = 0.0
    b1 = 0.0
    b2 = 0.0    
    
    # do some PyRoot magic to read from tree
    struct = '''
    struct Event{
    Float_t f_weight;
    Float_t f_mass4l;
    Float_t f_lept1_pt;
    Float_t f_lept2_pt;
    Float_t f_lept3_pt;
    Float_t f_lept4_pt;
    };'''
    gROOT.ProcessLine(struct)
    from ROOT import Event
    event = Event()

    # loop over files    
    for filename in filenames:
        
        # check whether this is a data, Higgs, or signal files
        isData   = isdata.findall(filename)   != []
        isHiggs  = ishiggs.findall(filename)  != []
        isSignal = issignal.findall(filename) != []
        
        # get sample name and truncate it
        name = sample.findall(filename)[0]
        name = name[:min(len(name), 48)]
            
        # open root file
        ntuple = TFile(filename)
        if not ntuple.IsOpen():
            record = '%-48s  %7d %10.2e %10.2e' % (name, -1, -1, -1)
            if isData:
                datarecs.append('%s\n' % record)
            elif isHiggs:
                higgsrecs.append('%s\n' % record)
            elif isSignal:
                sigrecs.append('%s\n' % record)                            
            else:
                bkgrecs.append('%s\n' % record)
            continue

        # get tree
        tree = ntuple.Get("HZZ4LeptonsAnalysisReduced")
        if not tree:
            record = '%-48s  %7d %10.2e %10.2e' % (name, -2, -2, -2)
            if isData:
                datarecs.append('%s\n' % record)
            elif isHiggs:
                higgsrecs.append('%s\n' % record)
            elif isSignal:
                sigrecs.append('%s\n' % record)                            
            else:
                bkgrecs.append('%s\n' % record)
            continue

        tree.SetBranchAddress('f_weight',
                              AddressOf(event, 'f_weight'))
        tree.SetBranchAddress('f_mass4l',
                              AddressOf(event, 'f_mass4l'))
        for ii in xrange(4):
            jj = ii+1
            field = 'f_lept%d_pt' % jj
            tree.SetBranchAddress(field,
                                  AddressOf(event, field))

        
        # now loop over events in current file
        nevents = tree.GetEntries()

        count = 0        
        w1 = 0.0
        w2 = 0.0
        for index in xrange(nevents):
            tree.GetEntry(index)
            if event.f_mass4l <  70: continue
            if event.f_mass4l > 170: continue
                
            w = event.f_weight
            if isData:
                t_d1 += w
                t_d2 += w*w
            elif isHiggs:
                t_h1 += w
                t_h2 += w*w
            elif isSignal:
                pass
            else:
                t_b1 += w
                t_b2 += w*w

            count += 1
            w1 += w
            w2 += w*w
            if isData:
                d1 += w
                d2 += w*w
            elif isHiggs:
                h1 += w
                h2 += w*w
            elif isSignal:
                pass
            else:
                b1 += w
                b2 += w*w

        w2 = sqrt(w2)
        record = '%-48s  %7d %10.2e %10.2e' % (name, count, w1, w2)
        if isData:
            datarecs.append('%s\n' % record)
        elif isHiggs:
            higgsrecs.append('%s\n' % record)
        elif isSignal:
            sigrecs.append('%s\n' % record)            
        else:
            bkgrecs.append('%s\n' % record)

        print record
        
        ntuple.Close()

    out.write('%-16s %7d\t%7d\n' % ('Data', int(d1), int(t_d1)))
    out.write('----------------------------------------------\n')
    out.writelines(datarecs)
    
    out.write('\n%-16s %10.2f +/- %10.2f\t%10.2f\n' % \
              ('Background', b1, b2, t_b1))
    out.write('----------------------------------------------\n')
    out.writelines(bkgrecs)    

    out.write('\n%-16s %10.2f +/- %10.2f\t%10.2f\n' % \
              ('Higgs', h1, h2, t_h1))
    out.write('----------------------------------------------\n')        
    out.writelines(higgsrecs)    

    out.write('\nSignals\n')
    out.write('----------------------------------------------\n')
    out.writelines(sigrecs)    
        
    out.close()
# -------------------------------------------------------------------------
try:     
    main()
except KeyboardInterrupt:
    print '\nciao!\n'
