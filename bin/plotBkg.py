#!/usr/bin/env python
#------------------------------------------------------------------
# File: plotBkg.py
# Description: plot results of discriminant training
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
    for row in xrange(ntuple.size()):
        ntuple.read(row)

        weight  = ntuple('f_weight')
        mass4l  = ntuple('f_mass4l')
        Dbkgkin = ntuple('f_D_bkg_kin')
        pfmet   = ntuple('f_pfmet')

        D = mlp(mass4l, Dbkgkin, pfmet)

        h.Fill(D, weight)

        if row % 10000 == 0:
            print '.',; sys.stdout.flush()
            c.cd()
            h.Draw(option)
            c.Update()
            gSystem.ProcessEvents()
    
    c.cd()
    h.Draw(option)
    c.Update()
    gSystem.ProcessEvents()    
    print
    sleep(3)    
#------------------------------------------------------------------
def main():

    xmin  =   0.00
    xmax  =   8.e-4 
    nbins =  20
    postfix = '_BR'
    
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

    os.system('mkdir -p figures')
    c1 = TCanvas("figures/f_%s_lin%s" % (MLPname, postfix),
                 MLPname, 10, 10, 500, 500)


    # DATA
    mcolor  = kBlack
    hd  = TH1F('hd', '', nbins, xmin, xmax)
    hd.GetXaxis().SetTitle(xtitle)
    hd.Sumw2()     # needed to handle weights correctly
    hd.GetXaxis().SetNdivisions(505)
    hd.GetYaxis().SetNdivisions(505)
    hd.SetMarkerColor(mcolor)
    hd.SetMarkerStyle(20)
    hd.SetLineColor(mcolor)
    hd.SetLineWidth(2)
    
    readAndFill(datfilename, mlp, c1, hd, 'ep')
    
    # BACKGROUND
    mcolor  = kMagenta+1
    hb  = TH1F('hb', '', nbins, xmin, xmax)
    hb.GetXaxis().SetTitle(xtitle)
    hb.Sumw2()     # needed to handle weights correctly
    hb.GetXaxis().SetNdivisions(505)
    hb.GetYaxis().SetNdivisions(505)
    hb.SetFillColor(mcolor)
    hb.SetFillStyle(3003)
    hb.SetLineColor(mcolor)
    hb.SetLineWidth(3)
    
    readAndFill(bkgfilename, mlp, c1, hb)

    # ---------------------------------------------------------
    # Plot
    # ---------------------------------------------------------   
    c1.cd()
    hb.Draw("hist")
    hb.Scale(hd.Integral()/hb.Integral())
    hb.SetMaximum(1.3*hd.GetMaximum())
    hb.Draw("hist")
    hd.Draw("ep same")
    CMS_lumi.CMS_lumi(c1, iPeriod, iPos)
    c1.Update()
    gSystem.ProcessEvents()    
    c1.SaveAs('.png')
    
    c2 = TCanvas("figures/f_%s_log%s" % (MLPname, postfix),
                 MLPname, 520, 10, 500, 500)
    c2.cd()
    c2.SetLogy()
    hb.Draw("hist")
    hd.Draw("ep same")    
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
