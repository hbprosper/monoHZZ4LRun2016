#!/usr/bin/env python
# ----------------------------------------------------------------------------
#  File:        makeFitHists.py
#  Description: mono-H->ZZ->4lepton analysis using reduced ntuples from Bari
#               make summary histograms for further analysis.
#  Created:     15-Oct-2016 HBP    
# ----------------------------------------------------------------------------
import os, sys, re
from ROOT import *
from string import *
from math import *
from time import sleep, ctime
from array import array
import CMS_lumi, tdrstyle
from histutil import Ntuple, nameonly
# ----------------------------------------------------------------------------
BNNXTITLE = '#font[12]{D}(#font[12]{m}_{4l}, #font[12]{D}_{bkg}^{kin})'

PLOTS = [('mass4l', '#font[12]{m}_{m4l} (GeV)',      10, 510)]
    
MASSBINS = 100
MASSMIN  = 100
MASSMAX  = 200
DBINS    = 100
BNNCUT   = 0.3
SKIP     = 50000
stripit  = re.compile('_2e2mu|_4e|_4mu')
# ----------------------------------------------------------------------------
def hintegral(h, cut=-1.0):
    lbin = h.GetNbinsX()
    if cut > 0:
        ii = 1
        xlow = h.GetBinLowEdge(ii)
        while (xlow < cut) and (ii < lbin):
            ii += 1
            xlow = h.GetBinLowEdge(ii)
        lbin = ii-1
        
    e1 = Double()
    c1 = h.IntegralAndError(lbin+1, h.GetNbinsX(), e1)

    e2 = Double()
    c2 = h.IntegralAndError(1, lbin, e2)    
    
    return (c1, e1, c2, e2)   
# ----------------------------------------------------------------------------
def main():
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

    gROOT.ProcessLine('.L ../m4lmela.cpp')
    mvd = m4lmela
    
    #change the CMS_lumi variables (see CMS_lumi.py)
    iPeriod = 4
    iPos    = 0
    CMS_lumi.relPosX = 0.12
    CMS_lumi.lumi_13TeV = "36 fb^{-1}"
    CMS_lumi.writeExtraText = 1
    CMS_lumi.extraText = "Simulation"
                
    if len(sys.argv) > 1:
        filenames = sys.argv[1:]
    else:
        sys.exit('''
    Usage:
        makeFitHists.py ntuple-file ...
        ''')

    # name of graphics file
    name = nameonly(filenames[0])
    plotname = replace(name, 'ntuple_', 'fig_')
    if len(filenames) > 1:
        plotname = stripit.sub('', plotname)
    outfilename = '%s.root' % plotname
        
    # change marker size and color depending on filename
    isData = False
    isHiggs= False
    if find(plotname, 'data') > -1:
        msize  = 0.8
        mcolor = kBlack
        isData = True
        CMS_lumi.extraText = "Preliminary"
        
    elif find(plotname, 'bkg') > -1:
        msize  = 0.01
        mcolor = kMagenta+1
        
    elif find(plotname, 'higgs') > -1:
        msize  = 0.01
        mcolor = kCyan+1
        isHiggs = True
                
    else:
        msize  = 0.01
        mcolor = kCyan+2

    # ---------------------------------------
    # open ntuple file
    # ---------------------------------------        
    ntuple  = Ntuple(filenames, treename='HZZ4LeptonsAnalysisReduced')
    nevents = ntuple.size()

    print '='*80            
    print 'number of entries: %d' % nevents
    print 'output file: %s' % outfilename    
    print '='*80

    # open output root file for histograms
    hfile = TFile(outfilename, 'recreate')
    hfile.cd()


    # ---------------------------------------
    # book histograms
    # ---------------------------------------
    # 2-D plot in (f_mass4l, f_D_bkg_kin) space
    
    cm4lD  = TCanvas(plotname, plotname, 10, 10, 500, 500)    
    hm4lD  = TH2F('hm4lD', '', MASSBINS, MASSMIN, MASSMAX, DBINS, 0, 1)
    hm4lD.SetMarkerSize(msize)
    hm4lD.SetMarkerColor(mcolor)
    hm4lD.GetXaxis().SetTitle('#font[12]{m}_{4l} (GeV)')
    hm4lD.GetYaxis().SetTitle('#font[12]{D}_{bkg}^{kin}')
    hm4lD.Sumw2()     # needed to handle weights correctly
    hm4lD.SetMinimum(0)
    hm4lD.GetXaxis().SetNdivisions(505)
    hm4lD.GetYaxis().SetNdivisions(505)
    
    # 1-D plot in D(f_mass4l, f_D_bkg_kin) space    
    cbnn  = TCanvas(plotname+'_bnn', plotname, 520, 10, 500, 500)    
    hbnn  = TH1F('hbnn', '', DBINS, 0, 1)
    hbnn.SetLineWidth(1)
    hbnn.SetFillColor(mcolor)
    hbnn.SetFillStyle(3001)
    hbnn.GetXaxis().SetTitle('#font[12]{D}(#font[12]{m}_{4l}, '\
                             '#font[12]{D}_{bkg}^{kin})')
    hbnn.GetXaxis().SetNdivisions(505)
    hbnn.Sumw2()
    hbnn.SetMinimum(0)

    hbnnf  = TH1F('hbnnf', '', DBINS, 0, 1)
    hbnnf.SetLineWidth(1)
    hbnnf.SetFillColor(mcolor)
    hbnnf.SetFillStyle(3001)
    hbnnf.GetXaxis().SetTitle('#font[12]{D}(#font[12]{m}_{4l}, '\
                             '#font[12]{D}_{bkg}^{kin})')
    hbnnf.GetXaxis().SetNdivisions(505)
    hbnnf.Sumw2()
    hbnnf.SetMinimum(0)    

    # 1-D plot in f_mass4l    
    cm4l  = TCanvas(plotname+'_m4l', plotname, 1040, 10, 500, 500)    
    hm4l  = TH1F('hm4l', '', MASSBINS, MASSMIN, MASSMAX)
    hm4l.SetLineWidth(1)
    hm4l.SetFillColor(mcolor)
    hm4l.SetFillStyle(3001)
    hm4l.GetXaxis().SetTitle('#font[12]{m}_{4l} (GeV)')
    hm4l.GetXaxis().SetNdivisions(505)
    hm4l.Sumw2()
    hm4l.SetMinimum(0)

    hm4lf  = TH1F('hm4lf', '', MASSBINS, MASSMIN, MASSMAX)
    hm4lf.SetLineWidth(1)
    hm4lf.SetFillColor(mcolor)
    hm4lf.SetFillStyle(3001)
    hm4lf.GetXaxis().SetTitle('#font[12]{m}_{4l} (GeV)')
    hm4lf.GetXaxis().SetNdivisions(505)
    hm4lf.Sumw2()
    hm4lf.SetMinimum(0)
      
    # ---------------------------------------
    # Loop over events
    # ---------------------------------------

    t1 = 0.0
    t2 = 0.0
    w1 = 0.0
    w2 = 0.0
    passed = 0
    for index, event in enumerate(ntuple):
        
        m4l  = event.f_mass4l
        if m4l < MASSMIN: continue
        if m4l > MASSMAX: continue

        Dbkg = event.f_D_bkg_kin
        Dbnn = mvd(m4l, Dbkg)
                        
        w = event.f_weight
        t1 += w
        t2 += w*w

        hm4lf.Fill(m4l, w)
        hbnnf.Fill(Dbnn, w)
        
        if event.f_outlier: continue
        w1 += w
        w2 += w*w
        
        hm4l.Fill(m4l, w)
        hm4lD.Fill(m4l, Dbkg, w)
        hbnn.Fill(Dbnn, w)
            
        if passed % SKIP == 0:
            print '%10d %10d' % (passed, index)
            
            cm4lD.cd()
            hm4lD.Draw('p')
            cm4lD.Update()
            gSystem.ProcessEvents()
            
            cbnn.cd()
            if isData:
                hbnn.Draw('ep')
            else:
                hbnn.Draw('hist')
            cbnn.Update()
            gSystem.ProcessEvents()
        passed += 1
        
    # now re-scale histograms to compensate for removal of
    # outlier events.
    scaleFactor = t1 / w1
    t2 = sqrt(t2)
    w2 = sqrt(w2)
    
    hm4l.Scale(scaleFactor)
    hm4lD.Scale(scaleFactor)
    hbnn.Scale(scaleFactor)
    for h in hbag:
        h.scale(scaleFactor)

    s1, s2, c1, c2 = hintegral(hbnn, BNNCUT)

    print '='*80
    txtfilename = '%s.txt' % plotname
    print txtfilename
    out = open(txtfilename, 'w')
    record = 'number of entries: %d' % nevents
    print record
    out.write('%s\n' % record)

    record = "number of events (with outliers):     %10.2e +/- %-10.1e" % \
      (t1, t2)
    print record
    out.write('%s\n' % record)

    record = "number of events (without outliers):  %10.2e +/- %-10.1e" % \
      (w1, w2)
    print record
    out.write('%s\n' % record)    

    record = ' '
    print record
    out.write('%s\n' % record)    
    
    record = 'histograms scaled by factor %10.3f' % scaleFactor
    print record
    out.write('%s\n' % record)
    
    record = "number of events (BNN >  %3.1f):        %10.2e +/- %-10.1e" % \
      (BNNCUT, s1, s2)
    print record
    out.write('%s\n' % record)
          
    record = "number of events (BNN <= %3.1f):        %10.2e +/- %-10.1e" % \
      (BNNCUT, c1, c2)
    print record
    out.write('%s\n' % record)

    out.close()            
    print '='*80

    
    cm4lD.cd()
    hm4lD.Draw('p')
    CMS_lumi.CMS_lumi(cm4lD, iPeriod, iPos)
    cm4lD.Update()
    gSystem.ProcessEvents()
    cm4lD.SaveAs('.png')

    cbnn.cd()
    if isData:
        hbnn.Draw('ep')
    else:
        hbnn.Draw('hist')
    CMS_lumi.CMS_lumi(cbnn, iPeriod, iPos)            
    cbnn.Update()
    gSystem.ProcessEvents()
    cbnn.SaveAs('.png')

    cm4l.cd()
    if isData:
        hm4l.Draw('ep')
    else:
        hm4l.Draw('hist')
    CMS_lumi.CMS_lumi(cm4l, iPeriod, iPos)            
    cm4l.Update()
    gSystem.ProcessEvents()
    cm4l.SaveAs('.png')        

    for h in hbag:
        h.draw(True)      
    hfile.cd()
    cm4lD.Write()
    cbnn.Write()
    cm4l.Write()
    
    for h in hbag:
        h.write()      

    hfile.Write()
    hfile.Close()
    
    sleep(10)
# -------------------------------------------------------------------------
try:     
    main()
except KeyboardInterrupt:
    print '\nciao!\n'
