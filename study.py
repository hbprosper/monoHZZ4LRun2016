#!/usr/bin/env python
# ----------------------------------------------------------------------------
#  File:        study.py
#  Description: perform various studies
#  Created: 09-May-2017 HBP, Suho Kim
# ----------------------------------------------------------------------------
# os  : operating system module
# sys : system module
# re  : regular expression module
import os, sys, re
# ROOT package from CERN (http://root.cern.ch)
from ROOT import *
# string: contains split, replace, atof, atoi, join, joinfields, etc.
from string import *
# some ROOT histogram utilities
from histutil import *
from time import sleep
# ----------------------------------------------------------------------------
def main():
    
    # setup some standard graphics style (see histutil.py)
    setStyle()
    # display number of entries (e), integral (i), mean (m), RMS (r)
    gStyle.SetOptStat('eimr')
    
    filename = 'ntuple_bkg.root'
    treename = 'HZZ4LeptonsAnalysisReduced'

    # load discriminant D(f_mass4l, f_D_bkg_kin)
    gROOT.ProcessLine('.L m4lmela.cpp')
    
    # define the branches to be read from the ntuple
    # f_finalstate: 1 = 2e2mu
    #               2 = 4e
    #               3 = 4mu
    # f_sample:     event type (see appropriate filelist file under store)
    branchnames = '''
    float f_weight
    float f_mass4l
    float f_D_bkg_kin
    int   f_sample
    int   f_finalstate
    int   f_outlier
    '''
    branchnames = map(split, split(strip(branchnames), '\n'))

    # create a C++ struct with the desired fields to be read from
    # the ntuples
    struct = 'struct Event{'
    for ftype, field in branchnames:
        record = '%s %s;' % (ftype, field)
        struct += record
    struct += '};'
    
    # compile this C++ struct
    gROOT.ProcessLine(struct)
    # load the C++ struct Event into the Python namespace
    from ROOT import Event

    # create an instance of struct Event
    event = Event()
    
    # open root file to be read
    ntuple = TFile(filename, 'READ')
    if not ntuple.IsOpen():
        sys.exit("* *can't open file %s" % filename)
        
    # get root tree
    tree = ntuple.Get(treename)
    if not tree:
        sys.exit("** can't access tree %s" % treename)

    # tell ROOT the addresses of the fields so that ROOT knows
    # where to load the data from the ntuples
    for ftype, field in branchnames:
        tree.SetBranchAddress(field, AddressOf(event, field))

    # now loop over events in current file
    nevents = tree.GetEntries()
    print "\n\t=> number of entries: %d" % nevents

    # create a canvas for histogram
    cD = TCanvas('fig_D', 'fig_D', 10, 10, 500, 500)

    # create an empty histogram for discriminant distribution
    xtitle = '#font[12]{D}(#font[12]{m}_{4l}, #font[12]{D}^{bkg}_{kin})'
    ytitle = ''
    xbins  =  60   # number of bins
    xmin   = 0.0   # lower histogram limit 
    xmax   = 0.3   # upper histogram limit
    hD = mkhist1('hD', xtitle, ytitle, xbins, xmin, xmax)
    hD.SetFillStyle(3001)
    hD.SetFillColor(kMagenta+1)

    count = 0
    for index in xrange(nevents):
        # read an event into memory
        tree.GetEntry(index)

        # skip events outside desired phase space
        if event.f_mass4l <  70: continue
        if event.f_mass4l > 170: continue
        
        # skip events with overly large weights
        if event.f_outlier: continue
            
        # compute signal/background discriminant
        # D(x) = s(x) / [s(x) + b(x)], x = mass4l, D_bkg_kin
        D = m4lmela(event.f_mass4l, event.f_D_bkg_kin)

        # fill histogram, weighted by the event weight
        hD.Fill(D, event.f_weight)

        # periodically update plot
        if count % 10000 == 0:
            cD.cd()
            hD.Draw('hist')
            cD.Update()
            gSystem.ProcessEvents()
            
        count += 1
            
    cD.cd()
    hD.Draw('hist')
    cD.Update()
    gSystem.ProcessEvents()            
    cD.SaveAs('.png')
    
    sleep(5)
# -------------------------------------------------------------------------
try:     
    main()
except KeyboardInterrupt:
    print '\nciao!\n'
