#!/usr/bin/env python
#------------------------------------------------------------------
# File: binData.py
# Description: try to bin data in an optimal way
# Created: 02-07-2017 HBP
#------------------------------------------------------------------
import os, sys
from hzz4lutil import *
from ROOT import *
from time import sleep
from glob import glob
import CMS_lumi, tdrstyle
#------------------------------------------------------------------
def read(filename, mlp):
    ntuple = NtupleReader(filename, ['f_weight',
                                     'f_mass4l',
                                     'f_D_bkg_kin',
                                     'f_pfmet'])
    records = [0]*ntuple.size()
    total = 0.0
    for row in xrange(ntuple.size()):
        ntuple.read(row)
        
        mass4l  = ntuple('f_mass4l')
        Dbkgkin = ntuple('f_D_bkg_kin')
        pfmet   = ntuple('f_pfmet')
        D = mlp(mass4l, Dbkgkin, pfmet)
        w = ntuple('f_weight')
        records[row] = (D, w)

        total += w
        
        if row % 10000 == 0:
            print '.',; sys.stdout.flush()
    
    records.sort()
    data   = [0]*len(records)
    weight = [0]*len(records)
    for ii, (d, w) in enumerate(records):
        data[ii] = d
        weight[ii] = w

    print
    print '=> number of events: %10.2f (%d)' % (total, ntuple.size())       
    return (data, weight)
#------------------------------------------------------------------
def main():
    xtitle = \
      '#font[12]{D}(#font[12]{m}_{4l}, '\
      '#font[12]{D}^{bkg}_{kin}, ' \
      '#font[12]{E}_{T}^{miss})'
      
    MLPname     = 'm4lmelamet'
    bkgfilename = ['ntuple_bkg.root', 'ntuple_higgs.root']
    datfilename = 'ntuple_data.root'
    
    # compile code
    code = open('%s.cpp' % MLPname).read()
    gROOT.ProcessLine(code)
    mlp  = eval(MLPname)
    
    # ---------------------------------------
    # set up some standard graphics style
    # ---------------------------------------
    tdrstyle.setTDRStyle()
    gStyle.SetPadRightMargin(0.12)
    gStyle.SetOptStat('ei')
    gStyle.SetStatFont(42)
    gStyle.SetStatFontSize(0.03)
    gStyle.SetStatBorderSize(1)
    gStyle.SetStatH(0.2)
    gStyle.SetStatW(0.3)
    gStyle.SetStatX(0.83)
    gStyle.SetStatY(0.93)    
    
    #change the CMS_lumi variables (see CMS_lumi.py)
    iPeriod = 4
    iPos    = 0
    CMS_lumi.relPosX = 0.12
    CMS_lumi.lumi_13TeV = "30.0 fb^{-1}"
    CMS_lumi.writeExtraText = 1
    CMS_lumi.extraText = "Simulation"
    
    data, wdata = read(datfilename, mlp)
    total= sum(wdata)

    bkg, weight = read(bkgfilename, mlp)
    btotal= sum(weight)

    # scale background to unity
    weight= map(lambda x: x/btotal, weight)

#----------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "\nciao!"
