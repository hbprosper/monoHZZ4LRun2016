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
PLOTS = [('pfmet',  '#font[12]{E}_{T}^{miss} (GeV)', 210, 100, 6),
         ('pt4l',   '#font[12]{p}_{T4l} (GeV)', 410, 100, 6),
         ('mT',     '#font[12]{m}_{T} (GeV)', 610, 100, 6)]
# ----------------------------------------------------------------------------
def plotRatio(hs1, hc1, name, xtitle, ytitle, iPeriod, iPos,
              ratioymax=10,
              ymin=1.e-9):

    gStyle.SetOptStat('')
    gStyle.SetStatFont(42)
    gStyle.SetStatFontSize(0.03)
    gStyle.SetStatBorderSize(1)
    gStyle.SetStatH(0.2)
    gStyle.SetStatW(0.3)
    gStyle.SetStatX(0.83)
    gStyle.SetStatY(0.93)       

    hs = hs1.Clone('hs_%s' % name)
    hc = hc1.Clone('hc_%s' % name)
    hs.SetMinimum(0)
    hs.Scale(1.0/hs.Integral())
    hc.Scale(1.0/hc.Integral())
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
    ## print name
    ## if name == 'pfmet':
    ##     hratio.Fit('pol1')
    ## elif name == 'pt4l':
    ##     hratio.Fit('pol16')
    ## else:
    ##     hratio.Fit('pol2')
        
    hratio.Draw('ep')
    CMS_lumi.CMS_lumi(cratio, iPeriod, iPos)    
    cratio.Update()    
    cratio.SaveAs('.png')
    gStyle.SetOptStat('')
    
    # --------------------------------------------------
    hr = hratio.Clone(hratio.GetName()+'2')    
    hr.GetXaxis().SetTitleOffset(1.15)
    hr.GetXaxis().SetLabelSize(0.08)
    hr.GetXaxis().SetTitleSize(0.08)

    hr.GetYaxis().SetTitleOffset(0.55)                
    hr.GetYaxis().SetLabelSize(0.08)
    hr.GetYaxis().SetTitleSize(0.08)         
    
    plotname = 'fig_%s' % name
    c  = TCanvas(plotname, plotname, 550, 10, 500, 575)

    # plot upper pad (within current canvas)
    c.cd()
    pad1  = TPad("pad1_%s" % name, "pad1", 0, 0.3, 1.0, 1.0)
    pad1.SetBottomMargin(10)
    pad1.Draw()
    
    pad1.cd()
    pad1.SetLogy()
    hc.GetXaxis().SetLabelSize(0)
    hc.GetXaxis().SetTitleSize(0)
    hc.SetFillStyle(3001)
    hs.SetFillStyle(3002)
         
    hc.Draw('hist')
    hs.Draw('histsame')
    CMS_lumi.CMS_lumi(pad1, iPeriod, iPos)
    
    # plot lower pad (within current canvas)    
    c.cd()
    pad2  = TPad("pad2_%s" % name, "pad2", 0, 0.0, 1, 0.36)
    pad2.SetTopMargin(1)
    pad2.SetBottomMargin(0.25)
    pad2.SetGridy()
    pad2.Draw()

    pad2.cd()
    hr.Draw('ep')
    c.Update()    
    c.SaveAs('.png')

    return (c, cratio, pad1, pad2, hr, hs, hc)
# ----------------------------------------------------------------------------  
def plotDataMCRatio(hd, hmc, name, xtitle, ytitle, iPeriod, iPos,
              ratioymax=10,
              ymin=1.e-9):

    gStyle.SetOptStat('')
    gStyle.SetStatFont(42)
    gStyle.SetStatFontSize(0.03)
    gStyle.SetStatBorderSize(1)
    gStyle.SetStatH(0.2)
    gStyle.SetStatW(0.3)
    gStyle.SetStatX(0.83)
    gStyle.SetStatY(0.93)       
    
    hd.SetMinimum(ymin)
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
    cratio.SaveAs('.png')
    gStyle.SetOptStat('')

    # --------------------------------------------------
    hr = hratio.Clone(hratio.GetName()+'2')
    hr.GetXaxis().SetTitleOffset(1.15)
    hr.GetXaxis().SetLabelSize(0.08)
    hr.GetXaxis().SetTitleSize(0.08)

    hr.GetYaxis().SetTitleOffset(0.55)                
    hr.GetYaxis().SetLabelSize(0.08)
    hr.GetYaxis().SetTitleSize(0.08)         
    
    plotname = 'fig_data_mc_%s' % name
    c  = TCanvas(plotname, plotname, 750, 110, 500, 575)

    # plot upper pad (within current canvas)
    c.cd()
    pad1  = TPad("data_mc_pad1_%s" % name, "pad1", 0, 0.3, 1.0, 1.0)
    pad1.SetBottomMargin(10)
    pad1.Draw()
    
    pad1.cd()
    pad1.SetLogy()
    hmc.GetXaxis().SetLabelSize(0)
    hmc.GetXaxis().SetTitleSize(0)
    hmc.SetFillStyle(3001)
    hmc.GetYaxis().SetTitle('Events / 5 GeV')
    hmc.Draw('histsame')
    hd.SetMarkerColor(kBlack)
    hd.Draw('epsame')

    xx = 0.50
    yy = 0.70
    wx = 0.36
    wy = 0.22
    lg = TLegend(xx, yy, xx+wx, yy+wy, 'Control Region #font[12]{D} < 0.2')
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
    pad2.SetTopMargin(1)
    pad2.SetBottomMargin(0.25)
    pad2.SetGridy()
    pad2.Draw()

    pad2.cd()
    hr.Draw('ep')
    c.Update()    
    c.SaveAs('.png')

    return (c, cratio, pad1, pad2, hr, lg)
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
    CMS_lumi.lumi_13TeV = "30 fb^{-1}"
    CMS_lumi.writeExtraText = 1
    CMS_lumi.extraText = "Simulation"
    
    # open background histograms file
    fbkg = TFile('fig_bkg.root')
    if not fbkg: sys.exit("can't open fig_bkg.root")

    # open signal histograms file       
    fsig = TFile('fig_higgs.root')
    if not fsig: sys.exit("can't open fig_higgs.root")

    # open data histograms file       
    #fdat = TFile('fig_data.root')
    #if not fdat: sys.exit("can't open fig_data.root")        
    fdat = None
    
    # scale background to match data in control region (CR)
    # defined by BNN < 0.3
    #   observed count in SR:   6 events
    #   observed count in CR:  98 events
    #   predicted count in CR: 113.3 (0.43 Higgs)
    scale = 1.0
    
    # get bkg BNN histogram and scale it
    hbnn_b = fbkg.Get('hbnn').Clone('hbnn_b')
    hbnn_b.Scale(scale)

    # get sig BNN histogram (assume predicted Higgs event count is accurate)
    hbnn_s = fsig.Get('hbnn').Clone('hbnn_s')

    # get 2-D f_D_bkg_kin vs f_mass_4l histograms. normalize to unity
    hb = fbkg.Get('hDmass').Clone('hb'); hb.Scale(1.0/hb.Integral())
    hs = fsig.Get('hDmass').Clone('hs'); hs.Scale(1.0/hs.Integral())

    # compute hp = hs / (hs + hb)
    hd = hs.Clone()
    hd.Add(hb)
    hp = hs.Clone()
    hp.Divide(hd)
                
    # compile BNN (=D(f_mass_4l, f_D_bkg_kin))discriminant
    print '\ncompling BNN..'
    record = open('DMass4l2016.cpp').read()
    gROOT.ProcessLine(record)
    bnn = Dmass4l2016
    
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

    # define contours of equal BNN value = s(x)/[s(x) + b(x)]
    # x = (mass4l, D)
    from array import array
    contours = array('d')
    contours.append(0.2)
    contours.append(0.4)
    contours.append(0.6)
    contours.append(0.8)
    hbnn.SetContour(len(contours), contours)

    # plot BNN function over hp (see above)
    plotname = 'fig_discriminant'
    cp  = TCanvas(plotname, plotname, 10, 10, 500, 500)
    cp.cd()    
    hp.Draw('colz')
    hbnn.Draw('cont3same')
    CMS_lumi.CMS_lumi(cp, iPeriod, iPos)
    cp.Update()
    cp.SaveAs('.png')
            
    # plot BNN distributions
    plotname = 'fig_bnn'
    cbnn  = TCanvas(plotname, plotname, 550, 510, 500, 500)
    hbnn_b.SetMinimum(0)
    hbnn_s.SetMinimum(0)        
    hbnn_b.Draw('hist')
    hbnn_s.Draw('histsame')
    CMS_lumi.CMS_lumi(cbnn, iPeriod, iPos)    
    cbnn.Update()
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
    cbnnlog.SaveAs('.png')

    hist = []
    for ii, (name, xtitle, xoff, yoff, ymax) in enumerate(PLOTS):
        hname = 'h%ss' % name
        hs = fbkg.Get(hname)
        hs.Scale(scale)
        hs.Add(fsig.Get(hname))

        hname = 'h%sc' % name
        hc = fbkg.Get(hname)
        hc.Scale(scale)
        hc.Add(fsig.Get(hname))        

        # plot missing-ET and ratio
        stuff = plotRatio(hs, hc, name, xtitle,
                          'SR / CR',
                          iPeriod, iPos, ymax)
        
        hist.append((stuff, hs, hc))

    ## for ii, (name, xtitle, xoff, yoff, ymax) in enumerate(PLOTS):
    ##     hname = 'h%sc2' % name
    ##     hmc = fbkg.Get(hname)
    ##     hmc.Scale(scale)
    ##     hmc.Add(fsig.Get(hname))

    ##     hname = 'h%sc2' % name
    ##     #hd = fdat.Get(hname)
    ##     hd = None
        
    ##     # plot missing-ET and ratio
    ##     stuff = plotDataMCRatio(hd, hmc, name, xtitle,
    ##                       'Data / MC',
    ##                       iPeriod, iPos, ymax)
        
    ##     hist.append((stuff, hd, hmc))
    
        
    gApplication.Run()
    sleep(10)
# -------------------------------------------------------------------------
try:     
    main()
except KeyboardInterrupt:
    print '\nciao!\n'
