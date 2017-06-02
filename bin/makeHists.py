#!/usr/bin/env python
# ----------------------------------------------------------------------------
#  File:        makeHists.py
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
METBINS  = 200
METMIN   =   0
METMAX   =1000

MASSBINS =  50
MASSMIN  = 100
MASSMAX  = 150

DBINS    =  50

BNNCUT   = 0.3
SKIP     = 50000

# fields to be read from ntuples 
FIELDS = ['f_weight',
          'f_mass4l',
          'f_D_bkg_kin',
          'f_pfmet',
          'f_pt4l',
          'f_mT',
          'f_sample',
          'f_finalstate',
          'f_outlier']

BNNXTITLE = '#font[12]{D}(#font[12]{m}_{4l}, #font[12]{D}_{bkg}^{kin})'

PLOTS = [('pfmet',  '#font[12]{E}_{T}^{miss} (GeV)', 10,  10,
              200, 0, 1000),
         ('pt4l',   '#font[12]{p}_{T4l} (GeV)',     515,  10,
              200, 0, 1000),
         ('mT',     '#font[12]{m}_{T} (GeV)',      1030,  10,
              200, 0, 1000),
         ('mass4l', '#font[12]{m}_{m4l} (GeV)',      10, 510,
              MASSBINS, MASSMIN, MASSMAX),
         ('metd',   'D(#font[12]{E}_{T}^{miss})',   515, 510,
              DBINS, 0, 1)]             

PLOTSZOOM = [('pfmet',  '#font[12]{E}_{T}^{miss} (GeV)', 10,  10,
              50, 0, 200),
            ('pt4l',   '#font[12]{p}_{T4l} (GeV)',     515,  10,
              50, 0, 200),
            ('mT',     '#font[12]{m}_{T} (GeV)',      1030,  10,
              50, 0, 200)]
    

stripit= re.compile('_2e2mu|_4e|_4mu')

gROOT.ProcessLine('.L metd.cpp')
gROOT.ProcessLine('.L m4lmela.cpp')
gROOT.ProcessLine('.L m4lmelamet.cpp')

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
    
class HistBag:
    def __init__(self, ntuple, plotname, name, xtitle,
                 xoff=10, yoff=10, xbins=100, xmin=0, xmax=500,
                 ymin=1.e-9,
                 postfix=''):
        
        self.ntuple = ntuple
        self.xtitle = xtitle
        self.xoff   = xoff
        self.yoff   = yoff
        self.name   = name
        if name == 'metd':
            self.field = 'f_pfmet'
            xmin = 0
            xmax = 1
            self.metd = metd
        else:
            self.field  = 'f_%s' % name

        self.plotname = plotname + '_%s%s' % (name, postfix)

    
        cname = 'histos/%s' % self.plotname
        print cname
        c  = TCanvas(cname, cname, xoff, yoff, 500, 500)
    
        # signal region    
        hs  = TH1F('h%ss' % name+postfix, '', xbins, xmin, xmax)
        hs.SetLineWidth(1)
        hs.SetMarkerColor(kRed)
        hs.SetFillColor(kRed)
        hs.SetFillStyle(3002)
        hs.GetXaxis().SetTitle(xtitle)
        hs.GetXaxis().SetNdivisions(505)
        hs.GetYaxis().SetNdivisions(505)    
        hs.Sumw2()
        hs.SetMinimum(ymin)

        # control region
        hc  = TH1F('h%sc' % name+postfix, '', xbins, xmin, xmax)
        hc.SetLineWidth(1)
        hc.SetMarkerColor(kBlue)
        hc.SetFillColor(kBlue)
        hc.SetFillStyle(3003)
        hc.GetXaxis().SetTitle(xtitle)
        hc.GetXaxis().SetNdivisions(505)
        hc.GetYaxis().SetNdivisions(505)        
        hc.Sumw2()
        hc.SetMinimum(ymin)
                    
        self.c  = c
        self.hs = hs
        self.hc = hc
        
    def __del__(self):
        pass

    def fillSR(self):
        w = self.ntuple('f_weight')
        x = self.ntuple(self.field)
        if self.name == 'metd': x = self.metd(x)
        self.hs.Fill(x, w)

    def fillCR(self):
        w = self.ntuple('f_weight')
        x = self.ntuple(self.field)
        if self.name == 'metd': x = self.metd(x)        
        self.hc.Fill(x, w)

    def scale(self, scaleFactor):
        self.hs.Scale(scaleFactor)
        self.hc.Scale(scaleFactor)

    def integralSR(self):
        nbins = hs.GetNbinsX()
        error = Double()
        count = hs.IntegralAndError(1, nbins, error)
        return (count, error)

    def integralCR(self):
        nbins = hc.GetNbinsX()
        error = Double()
        count = hc.IntegralAndError(1, nbins, error)
        return (count, error)    
    
    def draw(self, save=False):
        self.c.cd()
        if self.hs.Integral() > 0:
            self.hs.DrawNormalized('hist')
            if self.hc.Integral() > 0:
                self.hc.DrawNormalized('histsame')
        self.c.Update()
        gSystem.ProcessEvents()
        if save:
            if self.hs.Integral() > 0:
                self.c.SaveAs('.png')

    def write(self):
        self.c.Write()        
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

    bnn  = m4lmela
    bnn3 = m4lmelamet
    
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
        makeHists.py ntuple-file ...
        ''')

    # name of graphics file
    name = nameonly(filenames[0])
    plotname  = replace(name, 'ntuple_', 'fig_')
    plotnameSRCR  = replace(name, 'ntuple_', 'fig_regions_')
    histfname = replace(name, 'ntuple_', 'histos_')
    if len(filenames) > 1:
        plotname = stripit.sub('', plotname)
        histfname= stripit.sub('', histfname)
    outfilename = 'histos/%s.root' % histfname
        
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
    cname = 'histos/%s' % plotname 
    cm4lD = TCanvas(cname, cname, 10, 10, 500, 500)    
    hm4lD = TH2F('hm4lD', '', MASSBINS, MASSMIN, MASSMAX, DBINS, 0, 1)
    hm4lD.SetMarkerSize(msize)
    hm4lD.SetMarkerColor(mcolor)
    hm4lD.GetXaxis().SetTitle('#font[12]{m}_{4l} (GeV)')
    hm4lD.GetYaxis().SetTitle('#font[12]{D}_{bkg}^{kin}')
    hm4lD.Sumw2()     # needed to handle weights correctly
    hm4lD.SetMinimum(0)
    hm4lD.GetXaxis().SetNdivisions(505)
    hm4lD.GetYaxis().SetNdivisions(505)
    
    # 1-D plot in D(f_mass4l, f_D_bkg_kin) space
    cname = 'histos/%s_bnn' % plotname
    cbnn  = TCanvas(cname, cname, 520, 10, 500, 500)    
    hbnn  = TH1F('hbnn', '', DBINS, 0, 1)
    hbnn.SetLineWidth(1)
    hbnn.SetFillColor(mcolor)
    hbnn.SetFillStyle(3001)
    hbnn.GetXaxis().SetTitle('D(#font[12]{m}_{4l}, '\
                             '#font[12]{D}_{bkg}^{kin})')
    hbnn.GetXaxis().SetNdivisions(505)
    hbnn.Sumw2()
    hbnn.SetMinimum(0)

    # 1-D plot in f_mass4l
    cname = 'histos/%s_m4l' % plotname
    cm4l  = TCanvas(cname, cname, 1040, 10, 500, 500)    
    hm4l  = TH1F('hm4l', '', MASSBINS, MASSMIN, MASSMAX)
    hm4l.SetLineWidth(1)
    hm4l.SetFillColor(mcolor)
    hm4l.SetFillStyle(3001)
    hm4l.GetXaxis().SetTitle('#font[12]{m}_{4l} (GeV)')
    hm4l.GetXaxis().SetNdivisions(505)
    hm4l.Sumw2()
    hm4l.SetMinimum(0)


    # 1-D plot in f_pfmet
    cname = 'histos/%s_met' % plotname
    cmet  = TCanvas(cname, cname, 10, 510, 500, 500)    
    hmet  = TH1F('hmet', '', METBINS, METMIN, METMAX)
    hmet.SetLineWidth(1)
    hmet.SetFillColor(mcolor)
    hmet.SetFillStyle(3001)
    hmet.GetXaxis().SetTitle('#font[12]{E}_{T}^{miss} (GeV)')
    hmet.GetXaxis().SetNdivisions(505)
    hmet.Sumw2()
    hmet.SetMinimum(0)    

    
    # 1-D plot in D(f_mass4l, f_D_bkg_kin, f_pfmet)
    cname = 'histos/%s_bnn3' % plotname
    cbnn3  = TCanvas(cname, cname, 510, 510, 500, 500)    
    hbnn3  = TH1F('hbnn3', '', DBINS, 0, 1)
    hbnn3.SetLineWidth(1)
    hbnn3.SetFillColor(mcolor)
    hbnn3.SetFillStyle(3001)
    hbnn3.GetXaxis().SetTitle('D(#font[12]{m}_{4l}, '\
                             '#font[12]{D}_{bkg}^{kin}, '\
                                  '#font[12]{E}_{T}^{miss})')
    hbnn3.GetXaxis().SetNdivisions(505)
    hbnn3.Sumw2()
    hbnn3.SetMinimum(0)    


    hbag = []
    for ii, (name, xtitle, xoff, yoff, xbins, xmin, xmax) in enumerate(PLOTS):
        hbag.append(HistBag(ntuple, plotnameSRCR, name, xtitle, xoff, yoff,
                                xbins, xmin, xmax))

    for ii,(name,xtitle, xoff, yoff, xbins, xmin, xmax) in enumerate(PLOTSZOOM):
        hbag.append(HistBag(ntuple, plotnameSRCR, name, xtitle, xoff, yoff,
                            xbins, xmin, xmax,
                            ymin=1.e-9,
                            postfix='_zoom'))
 
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

        if m4l  < MASSMIN: continue
        if m4l  > MASSMAX: continue

        #if (m4l >= 100) and (m4l <=150): continue
                        
        w = event.f_weight
        t1 += w
        t2 += w*w
        
        if event.f_outlier: continue
        w1 += w
        w2 += w*w

        Dbkg = event.f_D_bkg_kin
        met  = event.f_pfmet
        
        Dbnn = bnn(m4l, Dbkg)
        Dbnn3= bnn3(m4l, Dbkg, met)
        
        hm4l.Fill(m4l, w)
        hm4lD.Fill(m4l, Dbkg, w)
        hbnn.Fill(Dbnn, w)
        hbnn3.Fill(Dbnn3, w)
        hmet.Fill(met, w)
        
        if Dbnn > BNNCUT:
            for h in hbag:
                h.fillSR()            
        else:
            for h in hbag:
                h.fillCR()               
            
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
            
            for h in hbag:
                h.draw()      
        passed += 1
        
    # now re-scale histograms to compensate for removal of
    # outlier events.
    scaleFactor = t1 / w1
    t2 = sqrt(t2)
    w2 = sqrt(w2)
    
    hm4l.Scale(scaleFactor)
    hm4lD.Scale(scaleFactor)
    hbnn.Scale(scaleFactor)
    hbnn3.Scale(scaleFactor)
    hmet.Scale(scaleFactor)
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

    cbnn3.cd()
    if isData:
        hbnn3.Draw('ep')
    else:
        hbnn3.Draw('hist')
    CMS_lumi.CMS_lumi(cbnn3, iPeriod, iPos)            
    cbnn3.Update()
    gSystem.ProcessEvents()
    cbnn3.SaveAs('.png')    

    cmet.cd()
    if isData:
        hmet.Draw('ep')
    else:
        hmet.Draw('hist')
    CMS_lumi.CMS_lumi(cmet, iPeriod, iPos)            
    cmet.Update()
    gSystem.ProcessEvents()
    cmet.SaveAs('.png')    

    
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
    cbnn3.Write()
    cmet.Write()
    cm4l.Write()
    
    for h in hbag:
        h.write()      

    hfile.Write()
    hfile.Close()
    
    sleep(2)
# -------------------------------------------------------------------------
try:     
    main()
except KeyboardInterrupt:
    print '\nciao!\n'
