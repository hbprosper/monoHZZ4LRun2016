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
from time import sleep
import CMS_lumi, tdrstyle
from histutil import *
from ROOT import *
#------------------------------------------------------------------
def readAndFill(filename, mlp, c, h, treename='HZZ4LeptonsAnalysisReduced'):
    ntuple = Ntuple(filename, treename)

    for row, event in enumerate(ntuple):
        if event.f_outlier: continue
            
        weight  = ntuple('f_weight')
        mass4l  = ntuple('f_mass4l')
        Dbkgkin = ntuple('f_D_bkg_kin')

        D = mlp(mass4l, Dbkgkin)

        h.Fill(D, weight)

        if row % 10000 == 0:
            c.cd()
            h.Draw("hist")
            c.Update()
            gSystem.ProcessEvents()
    h.Scale(1.0/h.Integral())
    c.cd()
    h.Draw("hist")
    c.Update()
    gSystem.ProcessEvents()
#------------------------------------------------------------------
def main():

    xtitle = \
      '#font[12]{D}(#font[12]{m}_{4l}, '\
      '#font[12]{D}^{bkg}_{kin})'
      
    MLPname     = 'm4lmela'
    sigfilename = '../../ntuple_higgs.root'
    bkgfilename = '../../ntuple_bkg.root'

    # compile code
    code = open('%s.cc' % MLPname).read()
    gROOT.ProcessLine(code)
    mlp  = m4lmela()
    
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

    msize = 0.15

    # SIGNAL
    os.system('mkdir -p figures')
    c1 = TCanvas("figures/f_%s_lin" % MLPname, MLPname, 10, 10, 500, 500)    
    mcolor  = kCyan+1
    hs  = TH1F('hs', '', 100, 0, 1)
    hs.GetXaxis().SetTitle(xtitle)
    hs.Sumw2()     # needed to handle weights correctly
    hs.SetMinimum(0)
    hs.GetXaxis().SetNdivisions(505)
    hs.GetYaxis().SetNdivisions(505)
    hs.SetFillColor(mcolor)
    hs.SetFillStyle(3002)    

    readAndFill(sigfilename, mlp, c1, hs)
    # BACKGROUND
    mcolor  = kMagenta+1
    hb  = TH1F('hb', '', 100, 0, 1)
    hb.GetXaxis().SetTitle(xtitle)
    hb.Sumw2()     # needed to handle weights correctly
    hb.SetMinimum(0)
    hb.GetXaxis().SetNdivisions(505)
    hb.GetYaxis().SetNdivisions(505)
    hb.SetFillColor(mcolor)
    hb.SetFillStyle(3003)

    readAndFill(bkgfilename, mlp, c1, hb)

    # ---------------------------------------------------------
    # Plot
    # ---------------------------------------------------------
    k = int(1.05*max(hb.GetMaximum(), hs.GetMaximum())/0.1)
    ymax = (k+1)*0.1
    hb.SetMaximum(ymax)
    hs.SetMaximum(ymax)

    c1.cd()
    hs.Draw("hist")
    hb.Draw("hist same")
    c1.Update()
    gSystem.ProcessEvents()
    c1.SaveAs('.png')

    c2 = TCanvas("figures/f_%s_log" % MLPname, MLPname, 520, 10, 500, 500)    
    c2.SetLogy()
    c2.cd()
    hs.Draw("hist")
    hb.Draw("hist same")
    gSystem.ProcessEvents()
    c2.Update()
    c2.SaveAs('.png')
        
    sleep(10)
#----------------------------------------------------------------------
main()
