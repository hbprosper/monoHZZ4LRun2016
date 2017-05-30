#!/usr/bin/env python
# ----------------------------------------------------------------------------
#  File:        plothists.py
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
# ----------------------------------------------------------------------------
PLOTS = [('pfmet',  '#font[12]{E}_{T}^{miss} (GeV)', 210, 100, 5.99),
         ('pt4l',   '#font[12]{p}_{T4l} (GeV)', 410, 100, 5.99),
         ('mT',     '#font[12]{m}_{T} (GeV)', 610, 100, 5.99)]
# ----------------------------------------------------------------------------
def drawLine(hr, Y=1):
    from array import array
    xbins = int(hr.GetNbinsX())
    width = hr.GetXaxis().GetBinWidth(1)
    xmin  = int(hr.GetXaxis().GetBinLowEdge(1))
    xmax  = int(hr.GetXaxis().GetBinLowEdge(xbins)+width)    
    x = array('d'); x.append(xmin); x.append(xmax)
    y = array('d'); y.append(Y); y.append(Y)
    hline = TGraph(2, x, y)
    hline.SetLineColor(kRed+1)
    hline.SetLineWidth(2)
    hline.Draw('lsame')
    SetOwnership(hline, 0)
        
def plotRatio(hs1, hc1, name, xtitle, ytitle, iPeriod, iPos,
              ratioymax=5.99,
              ymin=1.07e-7, ymax=1.0):

    gStyle.SetOptStat(0)
    gStyle.SetStatFont(42)
    gStyle.SetStatFontSize(0.03)
    gStyle.SetStatBorderSize(1)
    gStyle.SetStatH(0.2)
    gStyle.SetStatW(0.3)
    gStyle.SetStatX(0.83)
    gStyle.SetStatY(0.93)       

    hs = hs1.Clone('hs_%s' % name)
    hc = hc1.Clone('hc_%s' % name)
    hs.Scale(1.0/hs.Integral())
    hc.Scale(1.0/hc.Integral())

    hs.SetMinimum(ymin)
    hc.SetMinimum(ymin)

    hs.SetMaximum(ymax)
    hc.SetMaximum(ymax)    
        
    # --------------------------------------------------
    hratio = hs.Clone('%sratio' % name)
    hratio.Divide(hc)
    
    hratio.SetMarkerColor(kBlack)
    hratio.SetMarkerSize(0.6)
    hratio.SetMinimum(0)
    hratio.SetMaximum(ratioymax)
    
    hratio.GetXaxis().SetTitle(xtitle)
    hratio.GetXaxis().SetNdivisions(505)
    
    hratio.GetYaxis().SetTitle(ytitle)
    hratio.GetYaxis().SetNdivisions(510)
    
    plotname = 'fig_%s_ratio' % name
    cratio   = TCanvas(plotname, plotname, 10, 10, 500, 500)
    cratio.cd()
    cratio.SetGridy()
    hratio.Draw('ep')
    CMS_lumi.CMS_lumi(cratio, iPeriod, iPos)    
    cratio.Update()
    gSystem.ProcessEvents()
    cratio.SaveAs('.png')
    gStyle.SetOptStat(0)
    
    # --------------------------------------------------
    hr = hratio.Clone(hratio.GetName()+'2')    
    hr.GetXaxis().SetTitleOffset(1.15)
    hr.GetYaxis().SetTitleOffset(0.55)                
    hr.GetYaxis().SetLabelSize(0.10)
    hr.GetYaxis().SetTitleSize(0.10)         
    
    plotname = 'fig_%s' % name
    c  = TCanvas(plotname, plotname, 550, 10, 500, 575)

    # plot upper pad (within current canvas)
    c.cd()
    pad1  = TPad("pad1_%s" % name, "pad1", 0, 0.3, 1.0, 1.0)
    pad1.SetBottomMargin(0)
    pad1.Draw()
    
    pad1.cd()
    pad1.SetLogy()
    hc.SetFillStyle(3001)
    hs.SetFillStyle(3002)
         
    hc.Draw('hist')
    hs.Draw('histsame')

    xx = 0.50
    yy = 0.70
    wx = 0.36
    wy = 0.22
    lg = TLegend(xx, yy, xx+wx, yy+wy, 'Control Region #font[12]{D} < 0.3')
    lg.SetFillColor(kWhite)
    lg.SetTextFont(42)
    lg.SetBorderSize(0)
    lg.SetShadowColor(kWhite)    
    lg.AddEntry(hs, 'Signal Region', 'f')
    lg.AddEntry(hc, 'Control Region','f')
    lg.Draw()
    
    CMS_lumi.CMS_lumi(pad1, iPeriod, iPos)
    
    # plot lower pad (within current canvas)    
    c.cd()
    pad2  = TPad("pad2_%s" % name, "pad2", 0, 0.0, 1, 0.36)
    pad2.SetTopMargin(0.012)
    pad2.SetBottomMargin(0.28)
    pad2.SetGridy()
    pad2.Draw()
    pad2.cd()

    hr.SetStats(0)
    hr.GetXaxis().SetLabelSize(0.10)
    hr.GetXaxis().SetTitleSize(0.10)

    hr.GetYaxis().SetLabelSize(0.10)
    hr.GetYaxis().SetTitleSize(0.10)    
    hr.SetNdivisions(505, 'Y')    

    hr.Draw('ep')
    drawLine(hr)
    hr.Draw('epsame')
    
    c.Update()
    gSystem.ProcessEvents()
    c.SaveAs('.png')

    SetOwnership(c, 0)
    SetOwnership(cratio, 0)
    SetOwnership(pad1, 0)
    SetOwnership(pad2, 0)
    SetOwnership(hratio, 0)
    SetOwnership(hr, 0)
    SetOwnership(hs, 0)
    SetOwnership(hc, 0)
    SetOwnership(lg, 0)
# ----------------------------------------------------------------------------  
def plotDataMCRatio(hd, hmc, name, xtitle, ytitle, iPeriod, iPos,
              ratioymax=5.99,
              ymin=1.1e-1):

    gStyle.SetOptStat('')
    gStyle.SetStatFont(42)
    gStyle.SetStatFontSize(0.03)
    gStyle.SetStatBorderSize(1)
    gStyle.SetStatH(0.2)
    gStyle.SetStatW(0.3)
    gStyle.SetStatX(0.83)
    gStyle.SetStatY(0.93)       
    
    hd.SetMinimum(ymin)
    hmc.SetMinimum(ymin)
    hmc.SetFillColorAlpha(30, 0.50)    
    # --------------------------------------------------
    hratio = hd.Clone('data_mc_%sratio' % name)
    hratio.Divide(hmc)
    
    hratio.SetMarkerColor(kBlack)
    hratio.SetMarkerSize(0.6)
    hratio.SetMinimum(0)
    hratio.SetMaximum(ratioymax)
    
    hratio.GetXaxis().SetTitle(xtitle)
    hratio.GetXaxis().SetNdivisions(505)
    
    hratio.GetYaxis().SetTitle(ytitle)
    hratio.GetYaxis().SetNdivisions(510)
    
    plotname = 'fig_data_mc_%s_ratio' % name
    cratio   = TCanvas(plotname, plotname, 10, 10, 500, 500)
    cratio.cd()
    cratio.SetGridy()
    hratio.Draw('ep')
    CMS_lumi.CMS_lumi(cratio, iPeriod, iPos)    
    cratio.Update()
    gSystem.ProcessEvents()    
    cratio.SaveAs('.png')
    gStyle.SetOptStat(0)

    # --------------------------------------------------
    hr = hratio.Clone(hratio.GetName()+'2')
    hr.GetXaxis().SetTitleOffset(1.15)
    #hr.GetXaxis().SetLabelSize(0.08)
    #hr.GetXaxis().SetTitleSize(0.08)

    hr.GetYaxis().SetTitleOffset(0.55)                
    hr.GetYaxis().SetLabelSize(0.10)
    hr.GetYaxis().SetTitleSize(0.10)         
    
    plotname = 'fig_data_mc_%s' % name
    c  = TCanvas(plotname, plotname, 750, 110, 500, 575)

    # plot upper pad (within current canvas)
    c.cd()
    pad1  = TPad("data_mc_pad1_%s" % name, "pad1", 0, 0.3, 1.0, 1.0)
    pad1.SetBottomMargin(0)
    pad1.Draw()
    
    pad1.cd()
    pad1.SetLogy()
    hmc.GetXaxis().SetLabelSize(0)
    hmc.GetXaxis().SetTitleSize(0)
    hmc.SetFillStyle(3001)
    width = hmc.GetXaxis().GetBinWidth(1)    
    hmc.GetYaxis().SetTitle('Events / %3.1f GeV' % width)
    hmc.Draw('histsame')
    hd.SetMarkerColor(kBlack)
    hd.Draw('epsame')

    xx = 0.50
    yy = 0.70
    wx = 0.36
    wy = 0.22
    lg = TLegend(xx, yy, xx+wx, yy+wy, 'Control Region #font[12]{D} < 0.3')
    lg.SetFillColor(kWhite)
    lg.SetTextFont(42)
    lg.SetBorderSize(0)
    lg.SetShadowColor(kWhite)    
    lg.AddEntry(hd,  'Data (all channels)', 'p')
    lg.AddEntry(hmc, 'MC (all channels)', 'f')
    lg.Draw()
    
    CMS_lumi.extraText = "Preliminary"
    CMS_lumi.CMS_lumi(pad1, iPeriod, iPos)
    
    # plot lower pad (within current canvas)    
    c.cd()
    pad2  = TPad("data_mc_pad2_%s" % name, "pad2", 0, 0.0, 1, 0.36)
    pad2.SetTopMargin(0.012)
    pad2.SetBottomMargin(0.28)
    pad2.SetGridy()
    pad2.Draw()

    pad2.cd()
    hr.SetStats(0)
    hr.GetXaxis().SetLabelSize(0.10)
    hr.GetXaxis().SetTitleSize(0.10)

    hr.GetYaxis().SetLabelSize(0.10)
    hr.GetYaxis().SetTitleSize(0.10)    
    hr.SetNdivisions(505, 'Y')
    
    hr.Draw('ep')
    drawLine(hr)
    hr.Draw('epsame')
    
    c.Update()
    gSystem.ProcessEvents()    
    c.SaveAs('.png')

    SetOwnership(c, 0)
    SetOwnership(cratio, 0)
    SetOwnership(pad1, 0)
    SetOwnership(pad2, 0)
    SetOwnership(hr, 0)
    SetOwnership(hratio, 0)
    SetOwnership(lg, 0)
# ----------------------------------------------------------------------------       
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
    CMS_lumi.lumi_13TeV = "36 fb^{-1}"
    CMS_lumi.writeExtraText = 1
    CMS_lumi.extraText = "Simulation"

    fSM = TFile('histos/histos_SM.root')
    if not fSM.IsOpen(): sys.exit("can't open histos_SM.root")
    
    # open background histograms file
    fbkg = TFile('histos/histos_bkg.root')
    if not fbkg.IsOpen(): sys.exit("can't open histos_bkg.root")

    # open signal histograms file       
    fsig = TFile('histos/histos_higgs.root')
    if not fsig.IsOpen(): sys.exit("can't open histos_higgs.root")

    # open data histograms file       
    fdat = TFile('histos/histos_data.root')
    if not fdat.IsOpen(): sys.exit("can't open histos_data.root")        
    
    # scale background to match data in control region (CR)
    # defined by BNN < 0.3
    scale = 1.0
    
    # get bkg BNN histogram and scale it
    hbnn_b = fbkg.Get('hbnn').Clone('hbnn_b')
    hbnn_b.Scale(scale)

    # get sig BNN histogram (assume predicted Higgs event count is accurate)
    hbnn_s = fsig.Get('hbnn').Clone('hbnn_s')

    # get 2-D f_D_bkg_kin vs f_mass_4l histograms. normalize to unity
    hb = fbkg.Get('hm4lD').Clone('hb'); hb.Scale(1.0/hb.Integral())
    hs = fsig.Get('hm4lD').Clone('hs'); hs.Scale(1.0/hs.Integral())

    # compute hp = hs / (hs + hb)
    hd = hs.Clone()
    hd.Add(hb)
    hp = hs.Clone()
    hp.Divide(hd)
                
    # compile BNN (=D(f_mass_4l, f_D_bkg_kin))discriminant
    gROOT.ProcessLine('.L m4lmela.cpp')
    bnn = m4lmela
    
    # create 2-D histogram of BNN function
    nxbin = hs.GetNbinsX()
    xaxis = hs.GetXaxis()
    xmin  = xaxis.GetBinLowEdge(1)
    xmax  = xaxis.GetBinLowEdge(nxbin)+xaxis.GetBinWidth(nxbin)
    
    nybin = hs.GetNbinsY()
    yaxis = hs.GetYaxis()
    ymin  = yaxis.GetBinLowEdge(1)
    ymax  = yaxis.GetBinLowEdge(nybin)+yaxis.GetBinWidth(nybin)    

    nybin = 100
    nxbin = 100    
    hbnn  = TH2F('hbnn2d', '', nxbin, xmin, xmax, nybin, ymin, ymax)
    hbnn.SetLineWidth(2)
    xstep = (xmax-xmin)/nxbin
    ystep = (ymax-ymin)/nybin
    for ii in xrange(nxbin):
        mass4l = xmin + (ii+0.5)*xstep
        for jj in xrange(nybin):
            D = ymin + (jj+0.5)*ystep
            # call BNN discriminant
            z = bnn(mass4l, D)
            
            hbnn.SetBinContent(ii+1, jj+1, z)
            hbnn.SetBinError(ii+1, jj+1, 0)

    hbnn3 = hbnn.Clone('hbnn3')
    hbnn3.SetLineWidth(4)
    hbnn3.SetLineColor(kWhite)
    
    # define contours of equal BNN value = s(x)/[s(x) + b(x)]
    # x = (mass4l, D)
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
    
    # plot BNN function over hp (see above)
    plotname = 'fig_discriminant'
    cp  = TCanvas(plotname, plotname, 10, 10, 500, 500)
    cp.cd()    
    hp.Draw('col2z')
    hbnn.Draw('cont3same')
    hbnn3.Draw('cont3same')
    CMS_lumi.CMS_lumi(cp, iPeriod, iPos)
    cp.Update()
    gSystem.ProcessEvents()    
    cp.SaveAs('.png')
            
    # plot BNN distributions
    plotname = 'fig_bnn'
    cbnn  = TCanvas(plotname, plotname, 550, 510, 500, 500)
    hbnn_b.SetFillColorAlpha(kMagenta+1, 0.30)
    hbnn_s.SetFillColorAlpha(kAzure+1, 0.32)
    hbnn_b.SetMinimum(0)
    hbnn_s.SetMinimum(0)        
    hbnn_b.Draw('hist')
    hbnn_s.Draw('histsame')
    CMS_lumi.CMS_lumi(cbnn, iPeriod, iPos)    
    cbnn.Update()
    gSystem.ProcessEvents()    
    cbnn.SaveAs('.png')

    # plot BNN distributions
    plotname = 'fig_bnn_log'
    cbnnlog  = TCanvas(plotname, plotname, 650, 610, 500, 500)
    cbnnlog.SetLogy()
    hbnn_b.SetMinimum(1.e-3)
    hbnn_s.SetMinimum(1.e-3)
    hbnn_b.Draw('hist')
    hbnn_s.Draw('histsame')
    CMS_lumi.CMS_lumi(cbnnlog, iPeriod, iPos)    
    cbnnlog.Update()
    gSystem.ProcessEvents()    
    cbnnlog.SaveAs('.png')

    hist = []
    for ii, (name, xtitle, xoff, yoff, ymax) in enumerate(PLOTS):
        hname = 'h%ss' % name
        hs = fSM.Get(hname)

        hname = 'h%sc' % name
        hc = fSM.Get(hname)

        # plot missing-ET and ratio
        plotRatio(hs, hc, name, xtitle,
                      'SR / CR',
                      iPeriod, iPos, ymax)
        
    
    for ii, (name, xtitle, xoff, yoff, ymax) in enumerate(PLOTS):
        hname = 'h%sc_zoom' % name
        hmc = fSM.Get(hname)

        hname = 'h%sc_zoom' % name
        hd  = fdat.Get(hname)
        
        # plot missing-ET and ratio
        plotDataMCRatio(hd, hmc, name, xtitle,
                            'Data / MC',
                            iPeriod, iPos, ymax)
        
    #gApplication.Run()
    sleep(10)
# -------------------------------------------------------------------------
try:     
    main()
except KeyboardInterrupt:
    print '\nciao!\n'
