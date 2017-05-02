#!/usr/bin/env python
#------------------------------------------------------------------------------
# File: analyze.py
# Description: analyze BDT/MLP produced by TMVA
# Created: 07-Apr-2017 HBP (for Meena)
#------------------------------------------------------------------------------
import os, sys
from ROOT import *
from math import *
# to get do
# git clone https://github.com/hbprosper/histutil.git
# source histutil/setup.sh
from histutil import *
from time import sleep
#------------------------------------------------------------------------------
def main():

    # load BDT (C++ wrapped version)
    
    gSystem.Load("libmyBDT.so")

    # instantiate
    bdt = myBDT()
    
    print "number of trees: %6d" % bdt.size()
    print "summed weights:  %10.3f" % bdt.summedWeights()
    
    print "variables"
    vs = bdt.variables()
    for ii in xrange(vs.size()):
        print "\t%5d\t%s" % (ii, vs[ii])
    
    print
    print 'variable ranking by frequency'
    R = bdt.ranking()
    top = R[0].first
    for ii in xrange(R.size()):
        print '%5d\t%10.3f\t%s' % \
          (ii, R[ii].first/top, R[ii].second)

    print
    for itree in xrange(5):
        print
        bdt.printTree(itree)

    setStyle()
    hrank = TH1F('hrank', 'rank by frequency', len(vs), 0, len(vs))
    hrank.SetFillColor(kBlue)
    hrank.SetFillStyle(3001)
    hrank.GetYaxis().SetTitle('relative rank')
    hrank.GetYaxis().SetTitleOffset(0.9)
    hrank.GetXaxis().SetLabelSize(0.05)
    for ii in xrange(vs.size()):
        hrank.GetXaxis().SetBinLabel(ii+1, vs[ii])
        hrank.SetBinContent(ii+1, R[ii].first/top)
        hrank.SetBinError(ii+1, 0)
    canvas = TCanvas('fig_ranking', 'ranking', 10, 10, 1000, 500)
    canvas.cd()
    canvas.SetLeftMargin(0.10)
    canvas.SetBottomMargin(0.25)
    hrank.Draw('hist')
    canvas.Update()
    gSystem.ProcessEvents()
    canvas.SaveAs('.png')
    sleep(5)
    
#------------------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "\nciao"
