#!/usr/bin/env python
#------------------------------------------------------------------
#- File: plotROC.py
#- Description: Make plots...duh!
#- Created:     20-Dec-2013 HBP, Tallahassee
#------------------------------------------------------------------
import os, sys
from time import sleep
from string import *
from ROOT import *
import tdrstyle, CMS_lumi
from glob import glob
from histutil import Ntuple, nameonly, mkroc
#------------------------------------------------------------------
VARNAME = 'f_pfmet'
BNNNAME = 'metd'
MASSMIN = 100
MASSMAX = 150
BNNCUT  = 0.3
#------------------------------------------------------------------
def readAndFillHist(filename, bnn, c1, h1, m4lmela, step=10000, SR=False,
                        treename="HZZ4LeptonsAnalysisReduced"):
    # ---------------------------------------
    # open ntuple file
    # ---------------------------------------
    data  = Ntuple(filename, treename)
    print filename
    size  = data.size()
    if find(filename, 'SM') > 0:
        ntrain = 50000
    else:
        ntrain = 3000
        
    print 'ntrain: %s' % ntrain

    fields = [VARNAME]
    inputs= vector('double')(len(fields))

    count = 0
    for row, event in enumerate(data):
        
        if event.f_outlier: continue
        if event.f_mass4l < MASSMIN: continue
        if event.f_mass4l > MASSMAX: continue

        if count % step == 0:
            print "%10d\t%10d" % (row, count)
            
        count += 1
        if count < ntrain: continue

        if SR:
            d = m4lmela(event.f_mass4l, event.f_D_bkg_kin)
            if d < BNNCUT: continue
            
        w = event.f_weight
        for ii in xrange(len(fields)):
            inputs[ii] = event.__getattr__(fields[ii])
        D = bnn(inputs)

        h1.Fill(D, w)
        if count % step == 0:
            c1.cd()
            h1.Draw("hist")
            c1.Update()
            gSystem.ProcessEvents()                       
    c1.cd()
    h1.Scale(1.0/h1.Integral())
    h1.Draw("hist")
    c1.Update()
    gSystem.ProcessEvents()
#------------------------------------------------------------------
def main():
    argv = sys.argv[1:]
    argc = len(argv)
    if argc < 1:
        print '''
Usage:
    plot.py <sig-filename1> [SR]
    '''
        sys.exit()
            
    print "="*80
    os.system("mkdir -p figures")

    SR = argv[-1] == 'SR'
    if SR:
        argv = argv[:-1]
        postfix = '_SR'
    else:
        postfix = ''
        
    sigfilenames = argv
        
    sigfilenames.sort()
    bkgfilename = '../../ntuple_SM.root'

    BNNname = BNNNAME
        
    print 'BNN:             %s' % BNNname
    print
    print 'signal file:     %s' % sigfilenames
    print
    print 'background file: %s' % bkgfilename
    print "="*80

    # compile bnn function
    #gSystem.Load("libmvd")
    gROOT.ProcessLine('.L metd.cpp')
    gROOT.ProcessLine('.L m4lmela.cpp')
    bnn = eval(BNNname)
    
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
    CMS_lumi.lumi_13TeV = "36.0 fb^{-1}"
    CMS_lumi.writeExtraText = 1
    CMS_lumi.extraText = "Simulation"

        
    hfile = TFile("figures/h_%s.root" % BNNname,"RECREATE")
    hfile.cd()
    nbins = 100
    kolors= [kRed, kOrange, kYellow+2, kGreen+1, kBlue, kMagenta+1, kCyan+1]
    icolor= 0
    h = []
    # SIGNAL
    for ii, sigfilename in enumerate(sigfilenames):
        color = kolors[icolor]
        icolor += 1
        if icolor >= len(kolors):
            icolor = 0
        name  = replace(nameonly(sigfilename), 'ntuple_', '')
        hs1  = TH1F(name, '', nbins, 0, 1)
        hs1.GetXaxis().SetTitle('D_{%s}' % name)
        hs1.Sumw2()     # needed to handle weights correctly
        hs1.SetMinimum(1.e-6)
        hs1.GetXaxis().SetNdivisions(505)
        hs1.GetYaxis().SetNdivisions(505)
        hs1.SetFillColor(color)
        hs1.SetFillStyle(3001)    
        h.append(hs1)
    
    # BACKGROUND
    mcolor  = kMagenta+1
    hb1  = TH1F('hb1', '', nbins, 0, 1)
    hb1.GetXaxis().SetTitle('D_{bkg}')
    hb1.Sumw2()     # needed to handle weights correctly
    hb1.SetMinimum(1.e-6)
    hb1.GetXaxis().SetNdivisions(505)
    hb1.GetYaxis().SetNdivisions(505)
    hb1.SetFillColor(mcolor)
    hb1.SetFillStyle(3003)
    h.append(hb1)
    
    # ---------------------------------------------------------
    # Fill 
    # ---------------------------------------------------------
    cbnn1 = TCanvas("figures/f_%s_lin%s" % (BNNname, postfix), BNNname,
                        10, 10, 500, 500)
    
    # plot
    for ii, sigfilename in enumerate(sigfilenames):
        name = h[ii].GetName()
        cbnn1.SetTitle(name)
        print name
        readAndFillHist(sigfilename, bnn, cbnn1, h[ii], m4lmela, 500, SR)
    
    readAndFillHist(bkgfilename, bnn, cbnn1, hb1, m4lmela, 10000, SR)

    icolor = 0
    hroc = []
    for ii, sigfilename in enumerate(sigfilenames):
        name = '%s_roc' % h[ii].GetName()
 
        color = kolors[icolor]
        icolor += 1
        if icolor >= len(kolors):
            icolor = 0

        hroc.append(mkroc(name, h[ii], h[-1], lcolor=color))
    # ---------------------------------------------------------
    # Plot
    # ---------------------------------------------------------
    cbnn1.cd()
    h[0].SetMaximum(1.0)
    h[-1].SetMaximum(1.0)
    h[-1].Draw('hist')
    for hist in h:
        hist.Draw("histsame")
    cbnn1.Update()
    gSystem.ProcessEvents()
    cbnn1.SaveAs('.png')

    cbnn1log = TCanvas("figures/f_%s_log%s" % (BNNname, postfix), BNNname,
                       520, 10, 500, 500)
    cbnn1log.cd()
    cbnn1log.SetLogy()
    h[-1].Draw('hist')
    for hist in h:
        hist.Draw("histsame")
    cbnn1log.Update()
    gSystem.ProcessEvents()
    cbnn1log.SaveAs('.png')


    croc = TCanvas("figures/f_%s_roc%s" % (BNNname, postfix), BNNname,
                    1040, 10, 500, 500)
    croc.cd()
    hroc[0].Draw('al')
    for hist in hroc:
        hist.Draw("lsame")
    croc.Update()
    gSystem.ProcessEvents()
    croc.SaveAs('.png')      
    
    sleep(5)
#----------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "ciao!"
    
