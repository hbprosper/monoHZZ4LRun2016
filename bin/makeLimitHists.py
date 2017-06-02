#!/usr/bin/env python
# ----------------------------------------------------------------------------
#  File:        makeLimitHists.py
#  Description: mono-H->ZZ->4lepton analysis using reduced ntuples from Bari.
#               make histograms for fits and limit setting.
#
#  Created:     31-May-2017 HBP    
# ----------------------------------------------------------------------------
import os, sys, re, optparse
from ROOT import *
from string import *
from math import *
from time import sleep, ctime
from array import array
import CMS_lumi, tdrstyle
from histutil import Ntuple, nameonly
# ----------------------------------------------------------------------------
# 2 GeV bins

# control region
CRMASSBINS = 200
CRMASSMIN  =  80
CRMASSMAX  = 480

# signal region
SRMASSBINS =  25
SRMASSMIN  = 100
SRMASSMAX  = 150

SKIP      = 50000

SRPLOTS  = [('f_pfmet',  'met',     '#font[12]{E}_{T}^{miss} (GeV)',
              10,  10, 200, 0, 1000),
              
            ('f_pfmet', 'metzoom',  '#font[12]{E}_{T}^{miss} (GeV)',
              10,  10, 100, 0, 200),
              
            ('f_pt4l',   'pt4l',     '#font[12]{p}_{T4l} (GeV)', 
                515,  10, 200, 0, 1000),

            ('f_pt4l',   'pt4lzoom', '#font[12]{p}_{T4l} (GeV)', 
                515,  10, 100, 0, 200),                
                
            ('f_mT',     'mT',      '#font[12]{m}_{T} (GeV)',
                1030,  10, 200, 0, 1000),

            ('f_mT',     'mTzoom',  '#font[12]{m}_{T} (GeV)',
                1030,  10, 100, 0, 200),                
                
            ('f_mass4l', 'm4l',    '#font[12]{m}_{m4l} (GeV)',
                 10, 510, SRMASSBINS, SRMASSMIN, SRMASSMAX),
                 
            ('bnn1',   'bnn1',    'D(#font[12]{E}_{T}^{miss})',
                515, 510, 50,  0, 1),
                
            ('bnn2',   'bnn2', 'D(#font[12]{m}_{4l}, #font[12]{D}_{bkg}^{kin})',
                1030, 510, 50,  0, 1),
                
            ('bnn3',   'bnn3', 'D(#font[12]{m}_{4l}, '\
                 '#font[12]{D}_{bkg}^{kin}, #font[12]{E}_{T}^{miss})',
            1030, 510, 50,  0, 1)]

CRPLOTS  = [('f_pfmet',  'met',     '#font[12]{E}_{T}^{miss} (GeV)',
              10,  10, 200, 0, 1000),
              
            ('f_pfmet', 'metzoom',  '#font[12]{E}_{T}^{miss} (GeV)',
              10,  10, 100, 0, 200),
              
            ('f_pt4l',   'pt4l',     '#font[12]{p}_{T4l} (GeV)', 
                515,  10, 200, 0, 1000),

            ('f_pt4l',   'pt4lzoom', '#font[12]{p}_{T4l} (GeV)', 
                515,  10, 100, 0, 200),                
                
            ('f_mT',     'mT',      '#font[12]{m}_{T} (GeV)',
                1030,  10, 200, 0, 1000),

            ('f_mT',     'mTzoom',  '#font[12]{m}_{T} (GeV)',
                1030,  10, 100, 0, 200),

            ('f_mass4l', 'm4l',    '#font[12]{m}_{m4l} (GeV)',
                 10, 510, CRMASSBINS, CRMASSMIN, CRMASSMAX),                
                 
            ('bnn1',   'bnn1',    'D(#font[12]{E}_{T}^{miss})',
                515, 510, 50,  0, 1),
                
            ('bnn2',   'bnn2', 'D(#font[12]{m}_{4l}, #font[12]{D}_{bkg}^{kin})',
                1030, 510, 50,  0, 1),
                
            ('bnn3',   'bnn3', 'D(#font[12]{m}_{4l}, '\
                 '#font[12]{D}_{bkg}^{kin}, #font[12]{E}_{T}^{miss})',
            1030, 510, 50,  0, 1)]
    

stripit= re.compile('_2e2mu|_4e|_4mu')


FIELDS = '''
float f_weight
float f_mass4l
float f_D_bkg_kin
float f_pfmet
float f_mT
float f_pt4l
int   f_sample
int   f_finalstate
int   f_outlier
'''

gROOT.ProcessLine('.L metd.cpp')
gROOT.ProcessLine('.L m4lmela.cpp')
gROOT.ProcessLine('.L m4lmelamet.cpp')

# ----------------------------------------------------------------------------
def decodeCommandLine():
    VERSION = 'v1.0.0'
    USAGE = '''
    Usage:
        makeLimitHists.py [options] ntuple-file ... 

    options:
    -b background normalization uncertainty [0.3]
    -s signal normalization uncertainty     [0.1]
        '''
    parser = optparse.OptionParser(usage=USAGE, version=VERSION)

    parser.add_option('-b', '--berror',
                          action='store',
                          dest='berror',
                          type='float',
                          default=0.3,
                          help='relative bkg normalization uncertainty')

    parser.add_option('-s', '--serror',
                          action='store',
                          dest='serror',
                          type='float',
                          default=0.1,
                          help='relative sig normalization uncertainty')
 
    options, args = parser.parse_args()
    
    if len(args) == 0: sys.exit(USAGE)

    filename = args[0]
    return (filename, options)
# ----------------------------------------------------------------------------
def getNtuple(filename,
                  branchnames=FIELDS,
                   treename='HZZ4LeptonsAnalysisReduced'):
    
    branchnames = map(split, split(strip(branchnames), '\n'))

    # create a C++ struct with the desired fields to be read from
    # the ntuples
    struct = 'struct MiniNtuple{'
    for ftype, field in branchnames:
        record = '%s %s;' % (ftype, field)
        struct += record
    struct += '};'
    
    # compile this C++ struct
    gROOT.ProcessLine(struct)
    # load the C++ struct Event into the Python namespace
    from ROOT import MiniNtuple

    # create an instance of struct Event
    ntuple = MiniNtuple()
    
    # open root file to be read
    rfile = TFile(filename, 'READ')
    if not rfile.IsOpen():
        sys.exit("* *can't open file %s" % filename)
        
    # get root tree
    tree = rfile.Get(treename)
    if not tree:
        sys.exit("** can't access tree %s" % treename)

    # tell ROOT the addresses of the fields so that ROOT knows
    # where to load the data from the ntuples
    for ftype, field in branchnames:
        tree.SetBranchAddress(field, AddressOf(ntuple, field))

    # now loop over events in current file
    nevents = tree.GetEntries()
    print "\n\t=> number of entries: %d" % nevents
    ntuple.rfile= rfile
    ntuple.tree = tree
    ntuple.read = tree.GetEntry
    ntuple.nevents = nevents
    return ntuple
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
class HistBag:
    def __init__(self, CMS_lumi, iPeriod, iPos,
                     prefix, plotname,
                     ntuple, field,
                     hname, xtitle,
                     xoff=10, yoff=10, xbins=100, xmin=0, xmax=500):

        self.CMS_lumi = CMS_lumi
        self.iPeriod  = iPeriod
        self.iPos     = iPos
        self.prefix = prefix
        self.ntuple = ntuple
        self.field  = field
        self.hname  = hname        
        self.bnn1   = metd
        self.bnn2   = m4lmela
        self.bnn3   = m4lmelamet


        # change marker size and color depending on filename
        if find(plotname, 'data') > -1:
            msize  = 0.8
            mcolor = kBlack
            fcolor = 20
            self.option = 'ep'
            self.CMS_lumi.extraText = "Preliminary"
                
        elif find(plotname, 'higgs') > -1:
            msize  = 0.01
            mcolor = kAzure+1
            fcolor = kAzure+1
            self.option = 'hist'
            
        elif find(plotname, 'bkg') > -1:
            msize  = 0.01
            mcolor = kMagenta+1            
            fcolor = kMagenta+1
            self.option = 'hist'
            
        else:
            msize  = 0.01
            mcolor = kAzure+2
            fcolor = kAzure+2
            self.option = 'hist'
            
        self.plotname = 'fig_%s_%s_%s' % (prefix, hname, plotname)
    
        cname = 'histos/%s' % self.plotname
        print cname
        
        c  = TCanvas(cname, cname, xoff, yoff, 500, 500)
    
        h  = TH1F('%s_%s' % (prefix, hname), '', xbins, xmin, xmax)
        h.SetLineWidth(1)
        h.SetMarkerColor(mcolor)
        h.SetMarkerSize(msize)
        h.SetFillColor(fcolor)
        h.SetFillStyle(3002)
        h.GetXaxis().SetTitle(xtitle)
        h.GetXaxis().SetNdivisions(505)
        h.GetYaxis().SetNdivisions(505)    
        h.Sumw2()
                    
        self.c  = c
        self.h = h
        
    def __del__(self):
        pass

    def fill(self):
        if self.hname == 'bnn1':
            met = self.ntuple.f_pfmet
            x   = self.bnn1(met)
            
        elif self.hname == 'bnn2':
            m4l = self.ntuple.f_mass4l
            D   = self.ntuple.f_D_bkg_kin
            x   = self.bnn2(m4l, D)
            
        elif self.hname == 'bnn3':
            m4l = self.ntuple.f_mass4l
            D   = self.ntuple.f_D_bkg_kin
            met = self.ntuple.f_pfmet
            x   = self.bnn3(m4l, D, met)
            
        else:
            x   = self.ntuple.__getattribute__(self.field)

        w = self.ntuple.f_weight
        
        self.h.Fill(x, w)

    def scale(self, scaleFactor):
        self.h.Scale(scaleFactor)

    def integral(self):
        error = Double()
        nbins = self.h.GetNbinsX()
        count = self.h.IntegralAndError(1, nbins, error)
        return (count, error)
    
    def draw(self):
        self.c.cd()
        self.h.Draw(self.option)
        CMS_lumi.CMS_lumi(self.c, self.iPeriod, self.iPos)
        self.c.Update()
        gSystem.ProcessEvents()

    def save(self):
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

    #change the CMS_lumi variables (see CMS_lumi.py)
    iPeriod = 4
    iPos    = 0
    CMS_lumi.relPosX = 0.12
    CMS_lumi.lumi_13TeV = "36 fb^{-1}"
    CMS_lumi.writeExtraText = 1
    CMS_lumi.extraText = "Simulation"
                
    filename, options = decodeCommandLine()
    
    # name of graphics file
    name = nameonly(filename)
    plotname    = replace(name, 'ntuple_', '')
    histfname   = replace(name, 'ntuple_', 'histos_')
    outfilename = 'histos/%s.root' % histfname
        
    # ---------------------------------------
    # open ntuple file
    # ---------------------------------------        
    ntuple  = getNtuple(filename)
    nevents = ntuple.nevents

    print '='*80            
    print 'number of entries: %d' % nevents
    print 'output file: %s' % outfilename    
    print '='*80
    
    # open output root file for histograms
    hfile = TFile(outfilename, 'recreate')
    hfile.cd()

    CRbag = []
    for ii, (field, hname,
                 xtitle, xoff, yoff, xbins, xmin, xmax) in enumerate(CRPLOTS):
        CRbag.append(HistBag(CMS_lumi, iPeriod, iPos, 'CR', plotname, 
                                ntuple, field, hname, xtitle,
                                xoff, yoff, xbins, xmin, xmax))
    
    SRbag = []
    for ii, (field, hname,
                 xtitle, xoff, yoff, xbins, xmin, xmax) in enumerate(SRPLOTS):
        SRbag.append(HistBag(CMS_lumi, iPeriod, iPos, 'SR', plotname, 
                                ntuple, field, hname, xtitle,
                                xoff, yoff, xbins, xmin, xmax))

 
    # ---------------------------------------
    # Loop over events
    # ---------------------------------------
    t1 = 0.0
    t2 = 0.0
    w1 = 0.0
    w2 = 0.0
    passed = 0
    for index in xrange(nevents):
        
        ntuple.read(index)
        
        m4l  = ntuple.f_mass4l

        if m4l  < CRMASSMIN: continue
        if m4l  > CRMASSMAX: continue
                        
        w = ntuple.f_weight
        t1 += w
        t2 += w*w
        
        if ntuple.f_outlier: continue

        w1 += w
        w2 += w*w

        SR = (m4l >= SRMASSMIN) and (m4l <= SRMASSMAX)

        if SR:
            for h in SRbag: h.fill()
        else:
            for h in CRbag: h.fill()
        
        if passed % SKIP == 0:
            print '%10d %10d' % (passed, index)

            for h in SRbag: h.draw()            

        passed += 1
        
    # now re-scale histograms to compensate for removal of
    # outlier events.
    scaleFactor = t1 / w1
    t2 = sqrt(t2)
    w2 = sqrt(w2)

    for h in SRbag: h.scale(scaleFactor)
    for h in CRbag: h.scale(scaleFactor)        

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
    out.close()            
    print '='*80

    for h in CRbag:
        h.draw()
        h.save()
        h.write()
        
    for h in SRbag:
        h.draw()
        h.save()
        h.write()

    hfile.Write()
    hfile.Close()
    
    sleep(2)
# -------------------------------------------------------------------------
try:     
    main()
except KeyboardInterrupt:
    print '\nciao!\n'
