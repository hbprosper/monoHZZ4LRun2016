#!/usr/bin/env python
#------------------------------------------------------------------
# File: binBackground.py
# Description: bin background
# Created: 04-Feb-2017 HBP
#------------------------------------------------------------------
import os, sys
from hzz4lutil import *
from ROOT import *
from time import sleep
from glob import glob
import CMS_lumi, tdrstyle
#------------------------------------------------------------------
def readAndFill(filename, net, c, h, option='hist'):
    ntuple = NtupleReader(filename, ['f_weight',
                                     'f_mass4l',
                                     'f_D_bkg_kin',
                                     'f_pfmet'])
    for row in xrange(ntuple.size()):
        ntuple.read(row)

        weight  = ntuple('f_weight')
        mass4l  = ntuple('f_mass4l')
        Dbkgkin = ntuple('f_D_bkg_kin')
        pfmet   = ntuple('f_pfmet')

        D = net(mass4l, Dbkgkin, pfmet)

        h.Fill(D, weight)

        if row % 10000 == 0:
            c.cd()
            c.SetLogx()
            c.SetLogy()
            h.Draw(option)
            c.Update()
            gSystem.ProcessEvents()

    c.cd()
    c.SetLogx()
    c.SetLogy()
    h.Draw(option)
    c.Update()
    gSystem.ProcessEvents()
    c.SaveAs('.png')
    #del ntuple
#------------------------------------------------------------------
def main():

    xmin =      0
    xmax =      1
    nbins=   1000
    
    xtitle = \
      '#font[12]{D}(#font[12]{m}_{4l}, '\
      '#font[12]{D}^{bkg}_{kin}, ' \
      '#font[12]{E}_{T}^{miss})'
      
    MLPname     = 'm4lmelamet'
    bkgfilename = ['ntuple_bkg.root', 'ntuple_higgs.root']

    # compile code
    code = open('%s.cpp' % MLPname).read()
    gROOT.ProcessLine(code)
    net  = eval(MLPname)    
    
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

    os.system('mkdir -p figures')
    c1 = TCanvas("figures/f_%s_bkg" % MLPname,
                 MLPname, 10, 10, 500, 500)

    mcolor  = kMagenta+1
    hb1  = TH1F('hb1', '', nbins, xmin, xmax)
    hb1.GetXaxis().SetTitle(xtitle)
    hb1.Sumw2()     # needed to handle weights correctly
    hb1.GetXaxis().SetNdivisions(505)
    hb1.GetYaxis().SetNdivisions(505)
    hb1.SetFillColor(mcolor)
    hb1.SetFillStyle(3003)
        
    readAndFill(bkgfilename, net, c1, hb1)
        
    sleep(10)
#----------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print '\nciao!'
