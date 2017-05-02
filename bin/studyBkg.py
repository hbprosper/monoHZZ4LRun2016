#!/usr/bin/env python
# ----------------------------------------------------------------------------
#  File:        studyBkg.py
#  Description: mono-H->ZZ->4lepton analysis
#               compare distribution of pt4l within signal and control
#               regions for different control regions defined by mass4l
#               cuts. 
#
#  Created:     15-Oct-2016 HBP    
#               29 Nov 2016   ST   replaced DMass4l with Dmass4l ( line 161)
#               30 Nov 2016 ST   study cuts on m4l                            
#                5 Dec 2016 ST  Zero Division Error in drawRatio: hs.Scale
#                5 Dec 2016 HBP apply lower and upper m4l bounds to control
#                           region only. the distribution in signal region
#                           should remain unchanged. Also, now use all
#                           three final states (2e2mu, 4e, 4mu) 
#----------------------------------------------------------------------------
import os, sys, re
from ROOT import *
from string import *
from math import *
from time import sleep, ctime
from array import array
import CMS_lumi, tdrstyle
from hzz4lutil import NtupleReader, nameonly
# ----------------------------------------------------------------------------
# fields to be read from ntuples 
FIELDS = ['f_weight',
          'f_mass4l',
          'f_D_bkg_kin',
          'f_Dm4lmet',
          'f_pfmet',
          'f_pt4l',
          'f_mT',
          'f_sample',
          'f_finalstate',
          'f_outlier']
    
PLOTS = [('pfmet',  '#font[12]{E}_{T}^{miss} (GeV)', 200, 50),
         ('pt4l',   '#font[12]{p}_{T,4l} (GeV)', 300, 100),
         ('mT',     '#font[12]{m}_{T} (GeV)', 400, 150)]
    
BNNCUT = 0.4
SKIP   = 50000
# ----------------------------------------------------------------------------
# class to fill, plot, and write out histograms
class HistBag:
    def __init__(self, ntuple, plotname, name, xtitle, ytitle,
                 xoff=10, yoff=10,
                 xbins=100, xmin=0, xmax=1000,
                 iPeriod=4,
                 iPos=0,
                 ratioymax=3,
                 ymin=1.e-9):
        
        self.plotname = plotname
        self.name   = name
        self.ntuple = ntuple
        self.xtitle = xtitle
        self.ytitle = ytitle
        self.xoff   = xoff
        self.yoff   = yoff        
        self.field  = 'f_%s' % name
        self.iPeriod= iPeriod
        self.iPos   = iPos
        self.ratioymax = ratioymax
        self.ymin   = ymin
        
        cname = '%s_%s' % (plotname, name)
        c = TCanvas(cname, cname, xoff, yoff, 500, 500)
        
        # signal region    
        hs  = TH1F('h%ss' % name, '', xbins, xmin, xmax)
        hs.SetLineWidth(1)
        hs.SetMarkerColor(kRed)
        hs.SetFillColor(kRed)
        hs.SetFillStyle(3002)
        hs.GetXaxis().SetTitle(xtitle)
        hs.GetXaxis().SetNdivisions(505)
        hs.GetYaxis().SetNdivisions(505)    
        hs.Sumw2()
        hs.SetMinimum(ymin)

        hc  = TH1F('h%sc' % name, '', xbins, xmin, xmax)
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
        self.hs.Fill(x, w)

    def fillCR(self):
        w = self.ntuple('f_weight')
        x = self.ntuple(self.field)
        self.hc.Fill(x, w)

    def draw(self, save=False):
        self.c.cd()
        if self.hs.Integral() > 0:
            self.hs.DrawNormalized('hist')
            if self.hc.Integral() > 0:
                self.hc.DrawNormalized('histsame')
        if save:
            CMS_lumi.CMS_lumi(self.c, self.iPeriod, self.iPos)                            
        self.c.Update()
        if save:
            if self.hs.Integral() > 0:
                self.c.SaveAs('.png')

    def drawRatio(self):
        hs = self.hs.Clone('%s_%s_s' % (self.plotname, self.name))
        hc = self.hc.Clone('%s_%s_c' % (self.plotname, self.name))

        cr  = TCanvas('%s_%s_ratio' % (self.plotname, self.name),
                      self.name, self.xoff+50, self.yoff+50, 500, 500)
        self.cr = cr
        
        hs.SetMinimum(0)
        if hs.Integral()>0:
            hs.Scale(1.0/hs.Integral())
        if hc.Integral()>0:
            hc.Scale(1.0/hc.Integral())
        # --------------------------------------------------
        hratio = hs.Clone('%sratio' % self.name)
        hratio.Divide(hc)

        hratio.SetMarkerColor(kBlack)
        hratio.SetMarkerSize(0.6)
        hratio.SetMinimum(0)
        hratio.SetMaximum(self.ratioymax)

        hratio.GetXaxis().SetTitle(self.xtitle)
        hratio.GetXaxis().SetNdivisions(505)

        hratio.GetYaxis().SetTitle(self.ytitle)
        hratio.GetYaxis().SetNdivisions(505)

        cr.cd()
        cr.SetGridy()
        hratio.Draw('ep')
        CMS_lumi.CMS_lumi(cr, self.iPeriod, self.iPos)    
        cr.Update()    
        cr.SaveAs('.png')
        self.hratio = hratio

    def write(self):
        self.c.Write()
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
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

    iPeriod = 4
    iPos    = 0
    CMS_lumi.relPosX = 0.12
    CMS_lumi.lumi_13TeV = "30 fb^{-1}"
    CMS_lumi.writeExtraText = 1
    CMS_lumi.extraText = "Simulation"

    # ---------------------------------------
    # get name of ntuple file from the command
    # line
    # ---------------------------------------
    if len(sys.argv) > 1:
        filenames = sys.argv[1:]
    else:
        sys.exit('''
    Usage:
        studyBkg.py ntuple-file1 ...

        Example:

        python studyBkg.py ntuple_higgs.root ntuple_bkg.root
        ''')

    # name of graphics file
    name = nameonly(filenames[0])
    plotname = replace(name, 'ntuple_', 'fig_')
    if len(filenames) > 1:
        plotname = 'fig_all'
    outfilename = '%s.root' % plotname
        
    isData = False
    isHiggs= False
    if find(plotname, 'data') > -1:
        msize  = 0.8
        mcolor = kBlack
        isData = True
        
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
    ntuple  = NtupleReader(filenames, FIELDS)
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
    # 2-D plot in (f_mass4l, f_pfmet) space
    massmin =  80.0 # GeV
    massmax = 180.0 # GeV
    nmass   = 100

    metmin  =   0
    metmax  = 500
    nD      = 100
    cDmass  = TCanvas(plotname, plotname, 10, 10, 500, 500)    
    hDmass  = TH2F('hDmass', '', nmass, massmin, massmax, nD, metmin, metmax)
    hDmass.SetMarkerSize(msize)
    hDmass.SetMarkerColor(mcolor)
    hDmass.GetXaxis().SetTitle('#font[12]{m}_{4#font[12]{l}} (GeV)')
    hDmass.GetYaxis().SetTitle('#font[12]{E}_{T}^{miss} (GeV)')
    hDmass.Sumw2()     # needed to handle weights correctly
    hDmass.SetMinimum(0)
    hDmass.GetXaxis().SetNdivisions(505)
    hDmass.GetYaxis().SetNdivisions(505)
    
    # 1-D plot in BNN = D(f_m4l, f_pfmet) space    
    cbnn  = TCanvas(plotname+'_bnn', plotname, 520, 10, 500, 500)    
    hbnn  = TH1F('hbnn', '', 100, 0, 1)
    hbnn.SetLineWidth(1)
    hbnn.SetFillColor(mcolor)
    hbnn.SetFillStyle(3001)
    hbnn.GetXaxis().SetTitle('#font[12]{D}(#font[12]{m}_{4#font[12]{l}}, '\
                             '#font[12]{E}_{T}^{miss}) (GeV)')
    hbnn.GetXaxis().SetNdivisions(505)
    hbnn.Sumw2()
    hbnn.SetMinimum(0)

    # other plots (See PLOTS list above)
    hbag = []
    for ii, (name, xtitle, xoff, yoff) in enumerate(PLOTS):
        hbag.append(HistBag(ntuple, plotname, name, xtitle, '', xoff, yoff))
        
    
    # ---------------------------------------
    # Loop over events
    # ---------------------------------------

    t1 = 0.0
    t2 = 0.0
    m1 = 0.0
    m2 = 0.0
    w1 = 0.0
    w2 = 0.0
    s1 = 0.0
    s2 = 0.0
    b1 = 0.0
    b2 = 0.0    

    # pick final state
    k2E2MU = 0
    k4E    = 1
    k4MU   = 2
    kALL   = 3
    WHICH = {k2E2MU: '2e2mu',
             k4E:    '4e',
             k4MU:   '4mu',
             kALL:   'all'}
        
    FINALSTATE = kALL
     
    passed = 0
    for index in xrange(nevents):
        ntuple.read(index)
        
        w = ntuple('f_weight')
        t1 += w
        t2 += w*w

        # 0 - 2e2mu
        # 1 - 4e
        # 2 - 4mu
        
        #if ntuple('f_finalstate') != FINALSTATE: continue
        m1 += w
        m2 += w*w
        
        # skip events with weight > <weight> + 4*stdv
        try:
            if ntuple('f_outlier'): continue
        except:
            pass

        passed += 1
        
        w1 += w
        w2 += w*w

        m4l = ntuple('f_mass4l')
        met = ntuple('f_pfmet')
        
        hDmass.Fill(m4l, met, w)

        # compute BNN discriminant
        D = ntuple('f_Dm4lmet')
        hbnn.Fill(D, w)

        if passed % SKIP == 0:
            print '%10d %10d' % (passed, index)
            
            cDmass.cd()
            hDmass.Draw('p')
            cDmass.Update()

            cbnn.cd()
            if isData:
                hbnn.Draw('ep')
            else:
                hbnn.Draw('hist')
            cbnn.Update()

            for h in hbag:
                h.draw()      

        # separate events into signal and control regions
        # but apply m4l cuts to control region only
        if D > BNNCUT:
            s1 += w
            s2 += w*w
            # fill signal region distributions
            for h in hbag:
                h.fillSR()            
        else:
            # ---------------------------------------
            # Silvia: here is where you can change the
            # control region bounds. 
            # ---------------------------------------
            #if m4l <   70: continue # go to next event
            #if m4l > 2000: continue # go to next event

            b1 += w
            b2 += w*w
            # fill control region distributions            
            for h in hbag:
                h.fillCR()               
            

    t2 = sqrt(t2)
    m2 = sqrt(m2)
    w2 = sqrt(w2)
    s2 = sqrt(s2)
    b2 = sqrt(b2)
    c2 = Double()
    c1 = hDmass.IntegralAndError(1, nmass, 1, nD, c2)

    # ---------------------------------------
    # make final plots
    # ---------------------------------------
    cDmass.cd()
    hDmass.Draw('p')
    CMS_lumi.CMS_lumi(cDmass, iPeriod, iPos)
    cDmass.Update()
    cDmass.SaveAs('.png')

    cbnn.cd()
    if isData:
        hbnn.Draw('ep')
    else:
        hbnn.Draw('hist')
    CMS_lumi.CMS_lumi(cbnn, iPeriod, iPos)            
    cbnn.Update()
    cbnn.SaveAs('.png')      

    for h in hbag:
        h.draw(True)
        h.drawRatio()
              
    hfile.cd()
    cDmass.Write()
    cbnn.Write()

    for h in hbag:
        h.write()      

    hfile.Write()
    hfile.Close()

    # ---------------------------------------
    # print summary
    # ---------------------------------------
    print '='*80
    txtfilename = '%s.txt' % plotname
    print txtfilename
    out = open(txtfilename, 'w')
    record = 'number of entries: %d' % nevents
    print record
    out.write('%s\n' % record)

    record = "number of events (with outliers):   %10.2f   +/-% -5.2f" % \
      (t1, t2)
    print record
    out.write('%s\n' % record)

    record = "number of events (%6s):            %10.4f +/- %-10.5f" % \
      (WHICH[FINALSTATE], m1, m2)
    print record
    out.write('%s\n' % record)
    
    record = "number of events (without outliers):  %10.4f +/- %-10.5f" % \
      (w1, w2)
    print record
    out.write('%s\n' % record)
        
    record = "number of events (BNN >  %3.1f):        %10.4f +/- %-10.5f" % \
      (BNNCUT, s1, s2)
    print record
    out.write('%s\n' % record)
          
    record = "number of events (BNN <= %3.1f):        %10.4f +/- %-10.5f" % \
      (BNNCUT, b1, b2)
    print record
    out.write('%s\n' % record)

    out.close()            
    print '='*80
    
    sleep(10)
# -------------------------------------------------------------------------
try:     
    main()
except KeyboardInterrupt:
    print '\nciao!\n'
