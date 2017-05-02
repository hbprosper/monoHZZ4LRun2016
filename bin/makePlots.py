#!/usr/bin/env python
# ----------------------------------------------------------------------------
#  File:        makePlots.py
#  Description: make some standard Higgs plots
#  Created:     15-Oct-2016 HBP    
# ----------------------------------------------------------------------------
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
          'f_eta4l',
          'f_pt4l',
          'f_finalstate']

#          name     x-title         plot location(x,  y) xbins   xmin xmax
PLOTS = [('mass4l', '#font[12]{m}_{4l} (GeV)',   10, 10,   200,     0, 400),
         ('pt4l',   '#font[12]{p}_{T4l} (GeV)', 520, 10,   100,     0, 400),
         ('eta4l',  '#font[12]{#eta}_{4l}',    1040, 10,    80,    -8,   8)]

SKIP  = 10000
stripit= re.compile('_2e2mu|_4e|_4mu')
# ----------------------------------------------------------------------------
class HistBag:
    def __init__(self, ntuple, plotname, fcolor, name, xtitle,
                 xoff=10, yoff=10, xbins=100, xmin=0, xmax=1000):
        
        self.plotname = plotname + '_%s' % name
        print self.plotname
        
        self.ntuple = ntuple
        self.xtitle = xtitle
        self.xoff   = xoff
        self.yoff   = yoff        
        self.field  = 'f_%s' % name
        
        c  = TCanvas(self.plotname, name, xoff, yoff, 500, 500)
        
        # signal region    
        hs  = TH1F('h%s' % name, '', xbins, xmin, xmax)
        hs.SetLineWidth(1)
        hs.SetFillColor(fcolor)
        hs.SetFillStyle(3002)
        hs.GetXaxis().SetTitle(xtitle)
        hs.GetXaxis().SetNdivisions(505)
        hs.GetYaxis().SetNdivisions(505)    
        hs.Sumw2()
        hs.SetMinimum(0)
                    
        self.c  = c
        self.hs = hs
        
    def __del__(self):
        pass

    def fill(self):
        w = self.ntuple('f_weight')
        x = self.ntuple(self.field)
        self.hs.Fill(x, w)

    def draw(self, save=False):
        self.c.cd()
        self.hs.Draw('hist')
        self.c.Update()
        gSystem.ProcessEvents()    
        if save: self.c.SaveAs('.png')

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
    
    #change the CMS_lumi variables (see CMS_lumi.py)
    iPeriod = 4
    iPos    = 0
    CMS_lumi.relPosX = 0.12
    CMS_lumi.lumi_13TeV = "30 fb^{-1}"
    CMS_lumi.writeExtraText = 1
    CMS_lumi.extraText = "Simulation"
                
    if len(sys.argv) > 1:
        filenames = sys.argv[1:]
    else:
        sys.exit('''
    Usage:
        makePlots.py ntuple-file ...
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
        fcolor = 20
        isData = True
        
    elif find(plotname, 'bkg') > -1:
        msize  = 0.01
        fcolor = kMagenta+1
        
    elif find(plotname, 'higgs') > -1:
        msize  = 0.01
        fcolor = kCyan+1
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
    hbag = []
    for ii, (name, xtitle, xoff, yoff, nbins, xmin, xmax) in enumerate(PLOTS):
        hbag.append(HistBag(ntuple, plotname, fcolor,
                                name, xtitle, xoff, yoff, nbins, xmin, xmax))
 
    
    # ---------------------------------------
    # Loop over events
    # ---------------------------------------

    t1 = 0.0
    t2 = 0.0
 
    for index in xrange(nevents):
        ntuple.read(index)
        
        w = ntuple('f_weight')
        t1 += w
        t2 += w*w

        for h in hbag:
            h.fill()            
            
        if index % SKIP == 0:
            print '.',; sys.stdout.flush()
            for h in hbag:
                h.draw()      
            
    t2 = sqrt(t2)
    
    print
    print '='*80
    txtfilename = '%s.txt' % plotname
    print txtfilename
    out = open(txtfilename, 'w')
    record = 'number of entries: %d' % nevents
    print record
    out.write('%s\n' % record)

    record = "number of events:    %10.2f   +/-%-5.2f" % (t1, t2)
    print record
    out.write('%s\n' % record)
    out.close()            
    print '='*80

    for h in hbag:
        h.draw(True)      
    hfile.cd()

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
