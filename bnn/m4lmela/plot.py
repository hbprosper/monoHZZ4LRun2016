#!/usr/bin/env python
#------------------------------------------------------------------
#- File: plot.py
#- Description: Make plots...duh!
#- Created:     20-Dec-2013 HBP, Tallahassee
#------------------------------------------------------------------
import os, sys
from time import sleep
from string import *
from ROOT import *
import tdrstyle, CMS_lumi
from histutil import Ntuple, nameonly, mkroc
#------------------------------------------------------------------
SCOLOR = kCyan+1
BCOLOR = kMagenta+1
SSTYLE = 3004
BSTYLE = 3005
RCOLOR = kRed

MASSBIN=  50
MASSMIN=  70
MASSMAX= 170

DBIN   = 50

XTITLE = '#font[12]{m}_{4l}'
YTITLE = '#font[12]{D}_{bkg}^{kin}'
BNNXTITLE = 'D(%s, %s)' % (XTITLE, YTITLE)
XTITLE += ' (GeV)'
#------------------------------------------------------------------
def readAndFillHist(filename, bnn,
                    c1, h1,
                    c2, h2,
                    c3, h3,
                    c4, h4,
                        treename='HZZ4LeptonsAnalysisReduced'):
    # ---------------------------------------
    # open ntuple file
    # ---------------------------------------
    isData = find(filename, 'data') > 0
    
    ntuple = Ntuple(filename, treename)           

    for row, event in enumerate(ntuple):

        o = event.f_outlier
        x = event.f_mass4l
        
        if o: continue        
        if x < MASSMIN: continue
        if x > MASSMAX: continue
            
        w = event.f_weight        
        y = event.f_D_bkg_kin

        D = bnn(x, y)

        h1.Fill(D, w)
        h2.Fill(x, y, w)
        h3.Fill(x, w)
        h4.Fill(y, w)
        
        if row % 10000 == 0:
            for c, h in [(c1, h1),
                         (c3, h3),
                         (c4, h4)]:
                c.cd()
                if isData:
                    h.Draw('ep')
                else:
                    h.Draw("hist")
                c.Update()
                gSystem.ProcessEvents()            

            c2.cd()
            h2.Draw("p")
            c2.Update()

    for c, h in [(c1, h1),
                 (c2, h2),
                 (c3, h3),
                 (c4, h4)]:
        c.cd()
        if isData:
            h.Draw('ep')
        else:
            h.Scale(1.0/h.Integral())
            h.Draw("hist")
        c.Update()
        gSystem.ProcessEvents()

#------------------------------------------------------------------
def main():
    os.system("mkdir -p figures")

    sigfilename = '../../ntuple_higgs.root'
    bkgfilename = '../../ntuple_bkg.root'
    datfilename = '../../ntuple_data.root'
    BNNname = 'm4lmela'
    
    print "="*80        
    print 'BNN:             %s' % BNNname
    print 'signal file:     %s' % sigfilename
    print 'background file: %s' % bkgfilename
    print "="*80

    # compile bnn function
    gROOT.ProcessLine('.L %s.cpp' % BNNname)        
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

        
    # 2-D plot in (f_mass4l, f_D_bkg_kin) space
    massmin =  MASSMIN # GeV
    massmax =  MASSMAX # GeV
    Dmin    =  0
    Dmax    =  1
    nmass   =  MASSBIN
    nbnn    =  DBIN
    msize   = 0.01

    hfile = TFile("figures/h_%s.root" % BNNname,"RECREATE")
    hfile.cd()

    # DATA
    hd1  = TH1F('hd1', '', nbnn, 0, 1)
    hd1.GetXaxis().SetTitle(BNNXTITLE)
    hd1.SetMinimum(0)
    hd1.GetXaxis().SetNdivisions(505)
    hd1.GetYaxis().SetNdivisions(505)
    hd1.SetLineColor(kBlack)

    hd3  = TH1F('hd3', '', nmass, massmin, massmax)
    hd3.GetXaxis().SetTitle(XTITLE)
    hd3.SetMinimum(0)
    hd3.GetXaxis().SetNdivisions(505)
    hd3.GetYaxis().SetNdivisions(505)
    hd3.SetLineColor(kBlack)

    hd4  = TH1F('hd4', '', nbnn, 0, 1)
    hd4.GetXaxis().SetTitle(YTITLE)
    hd4.SetMinimum(0)
    hd4.GetXaxis().SetNdivisions(505)
    hd4.GetYaxis().SetNdivisions(505)
    hd4.SetLineColor(kBlack)

    hd2  = TH2F('hd2', '', nmass, massmin, massmax, nbnn,  0,  1)
    hd2.SetMarkerSize(msize)
    hd2.SetMarkerColor(kBlack)
    hd2.GetXaxis().SetTitle(XTITLE)
    hd2.GetYaxis().SetTitle(YTITLE)
    hd2.SetMinimum(0)
    hd2.GetXaxis().SetNdivisions(505)
    hd2.GetYaxis().SetNdivisions(505)
    
    
    # SIGNAL
    mcolor  = kCyan+1
    hs1  = TH1F('hs1', '', nbnn, 0, 1)
    hs1.GetXaxis().SetTitle(BNNXTITLE)
    hs1.Sumw2()     # needed to handle weights correctly
    hs1.SetMinimum(0)
    hs1.GetXaxis().SetNdivisions(505)
    hs1.GetYaxis().SetNdivisions(505)
    hs1.SetFillColor(mcolor)
    hs1.SetFillStyle(3002)    

    hs3  = TH1F('hs3', '', nbnn, massmin, massmax)
    hs3.GetXaxis().SetTitle(XTITLE)
    hs3.Sumw2()     # needed to handle weights correctly
    hs3.SetMinimum(0)
    hs3.GetXaxis().SetNdivisions(505)
    hs3.GetYaxis().SetNdivisions(505)
    hs3.SetFillColor(mcolor)
    hs3.SetFillStyle(3002)    

    hs4  = TH1F('hs4', '', nbnn, 0, 1)
    hs4.GetXaxis().SetTitle(YTITLE)
    hs4.Sumw2()     # needed to handle weights correctly
    hs4.SetMinimum(0)
    hs4.GetXaxis().SetNdivisions(505)
    hs4.GetYaxis().SetNdivisions(505)
    hs4.SetFillColor(mcolor)
    hs4.SetFillStyle(3002)        

    hs2  = TH2F('hs2', '', nmass, massmin, massmax, nbnn,  0, 1)
    hs2.SetMarkerSize(msize)
    hs2.SetMarkerColor(mcolor)
    hs2.GetXaxis().SetTitle(XTITLE)
    hs2.GetYaxis().SetTitle(YTITLE)
    hs2.Sumw2()     # needed to handle weights correctly
    hs2.SetMinimum(0)
    hs2.GetXaxis().SetNdivisions(505)
    hs2.GetYaxis().SetNdivisions(505)
    
    # BACKGROUND
    mcolor  = kMagenta+1
    hb1  = TH1F('hb1', '', nbnn, 0, 1)
    hb1.GetXaxis().SetTitle(BNNXTITLE)
    hb1.Sumw2()     # needed to handle weights correctly
    hb1.SetMinimum(0)
    hb1.GetXaxis().SetNdivisions(505)
    hb1.GetYaxis().SetNdivisions(505)
    hb1.SetFillColor(mcolor)
    hb1.SetFillStyle(3002)

    hb3  = TH1F('hb3', '', nmass, massmin, massmax)
    hb3.GetXaxis().SetTitle(XTITLE)
    hb3.Sumw2()     # needed to handle weights correctly
    hb3.SetMinimum(0)
    hb3.GetXaxis().SetNdivisions(505)
    hb3.GetYaxis().SetNdivisions(505)
    hb3.SetFillColor(mcolor)
    hb3.SetFillStyle(3002)

    hb4  = TH1F('hb4', '', nbnn, 0, 1)
    hb4.GetXaxis().SetTitle(YTITLE)
    hb4.Sumw2()     # needed to handle weights correctly
    hb4.SetMinimum(0)
    hb4.GetXaxis().SetNdivisions(505)
    hb4.GetYaxis().SetNdivisions(505)
    hb4.SetFillColor(mcolor)
    hb4.SetFillStyle(3003)              
        
    hb2  = TH2F('hb2', '', nmass, massmin, massmax, nbnn, 0, 1)
    hb2.SetMarkerSize(msize)
    hb2.SetMarkerColor(mcolor)
    hb2.GetXaxis().SetTitle(XTITLE)
    hb2.GetYaxis().SetTitle(YTITLE)
    hb2.Sumw2()     # needed to handle weights correctly
    hb2.SetMinimum(0)
    hb2.GetXaxis().SetNdivisions(505)
    hb2.GetYaxis().SetNdivisions(505)    

    # ---------------------------------------------------------
    # Fill 
    # ---------------------------------------------------------
    cbnn1 = TCanvas("figures/f_%s_1D_lin" % BNNname, BNNname,  10, 10, 500, 500)
    cbnn1log = TCanvas("figures/f_%s_1D_log" % BNNname, BNNname,
                       520, 10, 500, 500)
    cbnn2 = TCanvas("figures/f_%s_2D" % BNNname, BNNname, 1040, 10, 500, 500)

    cbnn3 = TCanvas("figures/f_%s_1D" % 'm4l', 'm4l',  10, 510, 500, 500)

    cbnn4 = TCanvas("figures/f_%s_1D" % 'mela', 'mela', 520, 510, 500, 500)
    
    # read data

    readAndFillHist(sigfilename, bnn,
                    cbnn1, hs1,
                    cbnn2, hs2,
                    cbnn3, hs3,
                    cbnn4, hs4)
    
    readAndFillHist(bkgfilename, bnn,
                    cbnn1, hb1,
                    cbnn2, hb2,
                    cbnn3, hb3,
                    cbnn4, hb4)

    readAndFillHist(datfilename, bnn,
                    cbnn1, hd1,
                    cbnn2, hd2,
                    cbnn3, hd3,
                    cbnn4, hd4)    

    # ---------------------------------------------------------
    # Plot
    # ---------------------------------------------------------
    # plot ROC curve
    hroc = mkroc('hroc', hs1, hb1, lcolor=kRed)
    croc = TCanvas("figures/f_%s_roc" % BNNname, BNNname,
                    520, 520, 500, 500)
    croc.cd()
    hroc.Draw('al')
    croc.Update()
    gSystem.ProcessEvents()
    croc.SaveAs('.png')

    
    cdata = TCanvas("figures/f_%s_1D_data" % BNNname, BNNname,
                    10, 10, 500, 500)
    cdata.cd()
    hd1.Draw("ep")
    cdata.Update()
    gSystem.ProcessEvents()
    cdata.SaveAs('.png')
    sleep(2)
    
    k = int(1.05*max(hb1.GetMaximum(), hs1.GetMaximum())/0.1)
    ymax = (k+1)*0.1
    hb1.SetMaximum(ymax)
    hs1.SetMaximum(ymax)

    cbnn1.cd()
    hs1.Draw("hist")
    hb1.Draw("hist same")
    cbnn1.Update()
    gSystem.ProcessEvents()
    cbnn1.SaveAs('.png')

    cbnn3.cd()
    hs3.Draw("hist")
    hb3.Draw("hist same")
    cbnn3.Update()
    gSystem.ProcessEvents()
    cbnn3.SaveAs('.png')

    cbnn4.cd()
    hb4.Draw("hist")
    hs4.Draw("hist same")
    cbnn4.Update()
    gSystem.ProcessEvents()
    cbnn4.SaveAs('.png')          
    
    cbnn1log.cd()
    cbnn1log.SetLogy()
    hs1.Draw("hist")
    hb1.Draw("hist same")    
    cbnn1log.Update()
    gSystem.ProcessEvents()
    cbnn1log.SaveAs('.png')

    
    # create 2-D histogram of BNN function
    nxbin = hs2.GetNbinsX()
    xaxis = hs2.GetXaxis()
    xmin  = xaxis.GetBinLowEdge(1)
    xmax  = xaxis.GetBinLowEdge(nxbin)+xaxis.GetBinWidth(nxbin)
    
    nybin = hs2.GetNbinsY()
    yaxis = hs2.GetYaxis()
    ymin  = yaxis.GetBinLowEdge(1)
    ymax  = yaxis.GetBinLowEdge(nybin)+yaxis.GetBinWidth(nybin)    

    nybin = 100
    nxbin = 100    
    hbnn  = TH2F('hbnn2d', '', nxbin, xmin, xmax, nybin, ymin, ymax)
    hbnn.SetLineWidth(2)
    xstep = (xmax-xmin)/nxbin
    ystep = (ymax-ymin)/nybin
    for ii in xrange(nxbin):
        x = xmin + (ii+0.5)*xstep
        for jj in xrange(nybin):
            y = ymin + (jj+0.5)*ystep
            D    = bnn(x, y)
            hbnn.SetBinContent(ii+1, jj+1, D)
            hbnn.SetBinError(ii+1, jj+1, 0)

    hbnn3 = hbnn.Clone('hbnn3')
    hbnn3.SetLineWidth(4)
    hbnn3.SetLineColor(kWhite)
    
    # define contours of equal BNN value = s(x)/[s(x) + b(x)]
    from array import array
    contours = array('d')
    contours.append(0.1)
    contours.append(0.2)
    contours.append(0.3)
    contours.append(0.4)
    contours.append(0.5)
    contours.append(0.6)
    contours.append(0.7)
    contours.append(0.8)
    contours.append(0.9)    
    hbnn.SetContour(len(contours), contours)

    contours[0] = 0.3
    hbnn3.SetContour(1, contours)

    # plot BNN function
    cbnn2.cd()
    gStyle.SetOptStat('')
    hD    = hs2.Clone('hD')
    hsum  = hs2.Clone('hsum')
    hsum.Add(hb2)

    hD.Divide(hsum)
    hD.GetXaxis().SetNdivisions(505)
    hD.GetYaxis().SetNdivisions(505)
    hD.SetMinimum(0)
    hD.SetMaximum(1)
    hD.Draw('col2z')
    hbnn.Draw('cont3 same')
    hbnn3.Draw('cont3 same')
    CMS_lumi.CMS_lumi(cbnn2, iPeriod, iPos)

    cbnn2.Update()
    gSystem.ProcessEvents()
    cbnn2.SaveAs('.png')


    cbnn5 = TCanvas("figures/f_%s_2D_surf" % BNNname, BNNname,
                    520, 510, 500, 500)
    hbnn.SetMinimum(0)
    hbnn.SetMaximum(1)    
    hbnn.GetXaxis().SetNdivisions(501)
    hbnn.GetYaxis().SetNdivisions(501)    
    hbnn.Draw('surf2z')
    CMS_lumi.CMS_lumi(cbnn5, iPeriod, iPos)
    cbnn5.Update()
    gSystem.ProcessEvents()
    cbnn5.SaveAs('.png')
    hfile.cd()
    cbnn1.Write()
    cbnn2.Write()
    cbnn3.Write()
    cbnn4.Write()
    cbnn5.Write()
    cdata.Write()
    hfile.Write()
    sleep(5)    
#----------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "ciao!"
    
