#!/usr/bin/env python
#------------------------------------------------------------------
# File: plot.py
# Description: plot results of training with TMVA
# Created: 01-Jun-2013 INFN SOS 2013, Vietri sul Mare, Italy, HBP
#    adapt to CMSDAS 2015 Bari HBP
#    adapt to HATS@LPC 2016 June 9th
#    adapt to check writeMLP wrapper 2017 Feb. 2nd
#------------------------------------------------------------------
import os, sys
from hzz4lutil import *
from ROOT import *
from time import sleep
from glob import glob
import CMS_lumi, tdrstyle
#------------------------------------------------------------------
def readAndFill(filename, mlp, c, h, option='hist'):
    ntuple = NtupleReader(filename, ['f_weight',
                                     'f_mass4l',
                                     'f_D_bkg_kin',
                                     'f_pfmet'])
    exec('hFill=h.Fill')
    for row in xrange(ntuple.size()):
        ntuple.read(row)

        weight  = ntuple('f_weight')
        mass4l  = ntuple('f_mass4l')
        Dbkgkin = ntuple('f_D_bkg_kin')
        pfmet   = ntuple('f_pfmet')

        D = mlp(mass4l, Dbkgkin, pfmet)

        h.Fill(D, weight)

        if row % 10000 == 0:
            c.cd()
            h.Draw(option)
            c.Update()
            gSystem.ProcessEvents()
            
    c.cd()
    h.Draw(option)
    c.Update()
    gSystem.ProcessEvents()    
    exec('del hFill')
    sleep(3)    
#------------------------------------------------------------------
def main():

    xmin  =   0.00
    xmax  =   1.00 
    nbins = 100
    postfix = '_SR'
    
    xtitle = \
      '#font[12]{D}(#font[12]{m}_{4l}, '\
      '#font[12]{D}^{bkg}_{kin}, ' \
      '#font[12]{E}_{T}^{miss})'
      
    MLPname     = 'm4lmelamet'
    
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

    os.system('mkdir -p figures')
    c1 = TCanvas("figures/f_%s_lin%s" % (MLPname, postfix),
                 MLPname, 10, 10, 500, 500)

    # SIGNALS        
    fsignals= glob('ntuple_Z*.root')
    fsignals.sort()
    ymax = -1.0
    hsig = []
    for ii, filename in enumerate(fsignals):
        print filename
        hs  = TH1F('hs%3.3d' % ii, '', nbins, xmin, xmax)
        hs.GetXaxis().SetTitle(xtitle)
        hs.Sumw2()     # needed to handle weights correctly
        hs.GetXaxis().SetNdivisions(505)
        hs.GetYaxis().SetNdivisions(505)
        mcolor = 20+ii
        hs.SetLineColor(mcolor)
        hs.SetLineWidth(2)    
        hsig.append(hs)
        
        readAndFill(filename, mlp, c1, hs)
        ymx = hs.GetMaximum()
        if ymx > ymax: ymax = ymx
            
    # ---------------------------------------------------------
    # Plot
    # ---------------------------------------------------------
    
    c1.cd()
    hs = hsig[0]
    hs.SetMaximum(0.06)
    hs.Draw("hist")
    for hs in hsig[1:]:
        hs.Draw("hist same")
    CMS_lumi.CMS_lumi(c1, iPeriod, iPos)
    c1.Update()
    gSystem.ProcessEvents()    
    c1.SaveAs('.png')
    
    c2 = TCanvas("figures/f_%s_log%s" % (MLPname, postfix),
                 MLPname, 520, 10, 500, 500)
    c2.cd()
    c2.SetLogy()
    hs = hsig[0]
    hs.SetMaximum(10*ymax)    
    hs.Draw("hist")
    for hs in hsig[1:]:
        hs.Draw("hist same")
    CMS_lumi.CMS_lumi(c2, iPeriod, iPos)
    c2.Update()
    gSystem.ProcessEvents()    
    c2.SaveAs('.png')

    sleep(10)
#----------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "\nciao!"
