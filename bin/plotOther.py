#!/usr/bin/env python
# ----------------------------------------------------------------------------
#  File:        plotBackground.py
#  Description: mono-H->ZZ->4lepton analysis using reduced ntuples from Bari
#               plot histograms created with makeHists.py
#  Created:     25-Oct-2016 HBP    
# ----------------------------------------------------------------------------
import os, sys, re
from ROOT import *
from string import *
from math import *
from time import sleep
import CMS_lumi, tdrstyle
# ---------------------------------------------------------------------------
FILES = '''
fig_data.root
fig_bkg.root
fig_higgs.root
'''
FILES = split(strip(FILES), '\n')
getsrc = re.compile('(?<=fig_).+(?=.root)')
# ---------------------------------------------------------------------------
def main():

    # ---------------------------------------
    # set up some standard graphics style
    # ---------------------------------------
    tdrstyle.setTDRStyle()
    gStyle.SetPadRightMargin(0.12)
    #change the CMS_lumi variables (see CMS_lumi.py)
    iPeriod = 4
    iPos    = 0
    CMS_lumi.relPosX = 0.12
    CMS_lumi.lumi_13TeV = "30 fb^{-1}"
    CMS_lumi.writeExtraText = 1
    CMS_lumi.extraText = "Simulation"

    tfile = []
    hbnn  = []
    hmet  = []
    hpt4l = []
    colorbase = 39
    for filename in FILES:
        source = getsrc.findall(filename)[0]
        print source
        f = TFile(filename); 
        if not f.IsOpen(): sys.exit("can't open %s" % filename)
        # get BNN histogram
        hbnn.append(f.Get('hbnn').Clone('hbnn_%s' % source))
        # get signal region (SR) missing-ET (MET)
        hmet.append(f.Get('hpfmets').Clone('hmet_%s' % source))
        hpt4l.append(f.Get('hpt4ls').Clone('hpt4l_%s' % source))
        tfile.append(f)


        colorbase += 1
        plotname = 'fig_%s_met' % source
        cmet = TCanvas(plotname, plotname, 10, 10, 500, 500)
        cmet.cd()
        hmet[-1].SetFillColor(colorbase)
        hmet[-1].SetFillStyle(3001)
        hmet[-1].Draw('hist')
        if source == 'data':
            hmet[-1].SetMarkerColor(kBlack)
            hmet[-1].Draw('epsame')
        CMS_lumi.CMS_lumi(cmet, iPeriod, iPos)            
        cmet.Update()
        gSystem.ProcessEvents()
        cmet.SaveAs('.png')

        plotname = 'fig_%s_pt4l' % source
        cpt4l = TCanvas(plotname, plotname, 520, 10, 500, 500)
        cpt4l.cd()
        hpt4l[-1].SetFillColor(colorbase)
        hpt4l[-1].SetFillStyle(3001)
        hpt4l[-1].Draw('hist')
        if source == 'data':
            hpt4l[-1].SetMarkerColor(kBlack)
            hpt4l[-1].Draw('epsame')
        CMS_lumi.CMS_lumi(cpt4l, iPeriod, iPos)            
        cpt4l.Update()
        gSystem.ProcessEvents()
        cpt4l.SaveAs('.png')


        plotname = 'fig_%s_bnn' % source
        cbnn = TCanvas(plotname, plotname, 520, 510, 500, 500)
        cbnn.cd()
        hbnn[-1].SetFillColor(colorbase)
        hbnn[-1].SetFillStyle(3001)
        hbnn[-1].Draw('hist')
        if source == 'data':
            hbnn[-1].SetMarkerColor(kBlack)
            hbnn[-1].Draw('epsame')            
        CMS_lumi.CMS_lumi(cbnn, iPeriod, iPos)            
        cbnn.Update()
        gSystem.ProcessEvents()
        cbnn.SaveAs('.png')

        sleep(5)
# -------------------------------------------------------------------------
try:     
    main()
except KeyboardInterrupt:
    print '\nciao!\n'
