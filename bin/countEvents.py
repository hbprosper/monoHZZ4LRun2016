#!/usr/bin/env python
# ----------------------------------------------------------------------------
#  File:        countEvents.py
#  Description: count events
#  Created:     26-Oct-2016 HBP    
# ----------------------------------------------------------------------------
import os, sys, re
from ROOT import *
from string import *
from math import *
from time import sleep, ctime
from array import array
import tdrstyle
# ----------------------------------------------------------------------------
# fields to be read from ntuples 
FIELDS = ['f_weight',
          'f_sample',
          'f_finalstate',
          'f_mass4l',
          'f_pfmet',
          'f_pt4l',
          'f_mT',
          'f_D_bnn',
          'f_lept1_pt',
          'f_lept2_pt',
          'f_lept3_pt',
          'f_lept4_pt']
SKIP   = 50000
SCALE  = 1.0
stripit= re.compile('_2e2mu|_4e|_4mu')
k2E2MU = 0
k4E    = 1
k4MU   = 2
FINALSTATE  = {'2e2mu': k2E2MU,
               '4e':    k4E,
               '4mu':   k4MU,
               'all':  -1}

kVBF   = 1    
SAMPLE = {'vbf':   kVBF,
          'all':   -1}


# ----------------------------------------------------------------------------
def nameonly(s):
    import posixpath
    return posixpath.splitext(posixpath.split(s)[1])[0]
# ----------------------------------------------------------------------------
# Note: "self" is like the "this" pointer in C++
class NtupleReader:
    def __init__(self,
                 filenames,
                 variables=FIELDS,
                 treename="HZZ4LeptonsAnalysisReduced"):
        # ---------------------------------------        
        # create a chain of root files
        # ---------------------------------------
        chain = TChain(treename)
        for filename in filenames:
            print filename
            chain.Add(filename)

        # ---------------------------------------
        # set up which variables to read from ntuples
        # ---------------------------------------
        tree   = chain
        # create struct to cache data from ntuple
        struct = 'struct Event{'
        fields = []
        for field in variables:
            branch = tree.GetBranch(field)
            if branch:
                leaf = branch.GetLeaf(field)
                if leaf:
                    typename = leaf.GetTypeName()
                    struct += '%s %s;' % (typename, field)
                    fields.append(field)
                else:
                    print "** leaf not found %s" % field
            else:
                print "** branch not found %s" % field
        struct += '};'
        # compile struct and 
        gROOT.ProcessLine(struct)
        from ROOT import Event
        event = Event()

        # ---------------------------------------
        # now give the addresses of the fields
        # within the struct to ROOT so that ROOT
        # knows where to put the data read from
        # the ntuple.
        # ---------------------------------------
        print "variables:"
        for field in fields:
            print "\t%s" % field
            tree.SetBranchAddress(field, AddressOf(event, field))

        # cache some variables
        self.event = event
        self.chain = chain
        self.tree  = chain.GetTree()
        self.variables = variables
        self.currentTreeNumber = -1
        
    def __del__(self):
        pass

    def __call__(self, field):
        return self.event.__getattribute__(field)
    
    def size(self):
        return self.chain.GetEntries()
    
    def read(self, index):
        chain = self.chain
        tree  = self.tree
        # load data into memory
        localindex = chain.LoadTree(index)
        if chain.GetTreeNumber() != self.currentTreeNumber:
            tree = chain.GetTree()
            self.currentTreeNumber = chain.GetTreeNumber()
        tree.GetEntry(localindex)        
# ----------------------------------------------------------------------------
def main():
    # ---------------------------------------
    # set up some standard graphics style
    # ---------------------------------------
    tdrstyle.setTDRStyle()
    
    gStyle.SetPadRightMargin(0.12)
    gStyle.SetOptStat('eimr')
    gStyle.SetStatColor(kWhite)
    gStyle.SetStatFont(42)
    gStyle.SetStatFontSize(0.03)
    gStyle.SetStatTextColor(1)
    gStyle.SetStatFormat("6.4g")
    gStyle.SetStatBorderSize(1)
    gStyle.SetStatH(0.2)
    gStyle.SetStatW(0.3)
    gStyle.SetStatX(0.84)
    gStyle.SetStatY(0.92)
    
    
    if len(sys.argv) > 1:
        filenames = [sys.argv[1]]
    else:
        sys.exit('''
    Usage:
        countEvents.py ntuple-file [sample] [final-state] 
        ''')

    if len(sys.argv) > 2:
        sample = sys.argv[2]
    else:
        sample = 'all'

    if len(sys.argv) > 3:
        finalstate = sys.argv[3]
    else:
        finalstate = 'all'        
    
    # name of graphics file
    name = nameonly(filenames[0])
    plotname = replace(name, 'ntuple_', 'count_')
    if len(filenames) > 1:
        plotname = stripit.sub('', plotname)
        
    plotname = '%s_%s_%s' % (plotname, sample, finalstate)
    print plotname
    
    # change marker size and color depending on filename
    isData = False
    if find(plotname, 'data') > -1:
        msize  = 0.8
        mcolor = kBlack
        fcolor = mcolor
        isData = True
        
    elif find(plotname, 'bkg') > -1:
        msize  = 0.01
        mcolor = kMagenta+1
        fcolor = mcolor
        
    elif find(plotname, 'higgs') > -1:
        msize  = 0.01
        mcolor = kCyan+1
        fcolor = mcolor
                
    else:
        # Dark matter events
        msize  = 0.01
        mcolor = kGreen+2
        fcolor = mcolor
    
    # create empty histograms
    # 1-D pt plots
    cpt  = TCanvas(plotname+'_pt', plotname, 10, 10, 800, 800)
    cpt.Divide(2, 2)
    xmin  =   0
    xmax  = 300
    xbins =  60
    binwid= int((xmax-xmin)/xbins)
        
    hpt   = []
    for ii in xrange(4):
        jj = ii+1
        hname = 'f_lept%d_pt' % jj
        hpt.append(TH1F(hname, '', xbins, xmin, xmax))
        hpt[-1].SetLineWidth(1)
        hpt[-1].SetFillColor(mcolor)
        hpt[-1].SetFillStyle(3003)
        hpt[-1].GetXaxis().SetTitle('#font[12]{p}_{Tl%d} (GeV)' % jj)
        hpt[-1].GetXaxis().SetNdivisions(505)
        hpt[-1].GetYaxis().SetTitle('Events / (%d GeV)' % \
                                    int((xmax-xmin)/xbins))
        hpt[-1].GetYaxis().SetNdivisions(505)                
        hpt[-1].Sumw2()
        hpt[-1].SetMinimum(0)

    cmet   = TCanvas(plotname + '_met', plotname, 300, 300, 800, 800)
    cmet.Divide(2, 2)
    hpfmet = TH1F('hpfmet',  '', xbins, xmin, xmax)
    hpt4l  = TH1F('hpt4l',   '', xbins, xmin, xmax)
    hmT    = TH1F('hmT',     '', xbins, xmin, xmax)
    hbnn   = TH1F('hbnn',    '', 50, 0, 1)
    
    for h, color, xtitle in [(hpfmet, mcolor, '#font[12]{E}_{T}^{miss} (GeV)'),
                             (hpt4l,  mcolor, '#font[12]{p}_{T4l} (GeV)'),
                             (hmT,    mcolor, '#font[12]{m}_{T} (GeV)'),
                             (hbnn,   mcolor,
                              '#font[12]{D}(#font[12]{m}_{4l},'\
                             ' #font[12]{D}^{bkg}_{kin})')]:

        h.SetLineWidth(1)
        h.SetFillColor(mcolor)
        h.SetFillStyle(3003)
        h.GetXaxis().SetNdivisions(505)
        h.GetXaxis().SetTitle(xtitle)        
        if h.GetName() == 'hbnn':
            h.GetYaxis().SetTitle('Events / 0.02')
        else:
            h.GetYaxis().SetTitle('Events / %d GeV' % binwid)
        h.GetYaxis().SetNdivisions(505)                
        h.Sumw2()
        h.SetMinimum(0)
        
    hlist = [(hpfmet, 'f_pfmet'),
             (hpt4l,  'f_pt4l'),
             (hmT,    'f_mT'),
             (hbnn,   'f_D_bnn')]
        
    # ---------------------------------------
    # Loop over events
    # ---------------------------------------
    ntuple  = NtupleReader(filenames, FIELDS)
    nevents = ntuple.size()
    
    print '='*80            
    print 'number of entries: %d' % nevents

    t1 = 0.0
    t2 = 0.0
    w1 = 0.0
    w2 = 0.0
    s1 = 0.0
    s2 = 0.0
    count = 0

    ESAMPLE = SAMPLE[sample]
    FSTATE  = FINALSTATE[finalstate]

    gStyle.SetTitleXOffset(1.05)
      
    for index in xrange(nevents):
        # load variables into memory
        ntuple.read(index)

        w = ntuple('f_weight') * SCALE

        t1 += w
        t2 += w*w


        if ESAMPLE < 0:
            pass
        else:
            if ntuple('f_sample') != ESAMPLE: continue
                     
        if FSTATE < 0:
            pass
        else:
            if ntuple('f_finalstate') != FSTATE: continue

        w1 += w
        w2 += w*w
            
        pt = [0]*4
        for ii in xrange(4):
            jj = ii+1
            field  = 'f_lept%d_pt' % jj        
            pt[ii] = ntuple(field)
        pt.sort()
        pt.reverse()
                       
        if not (pt[-1] > 10): continue         

        s1 += w
        s2 += w*w
        
        for ii in xrange(4):
            hpt[ii].Fill(pt[ii], w)
        for h, name in hlist:
            x = ntuple(name)
            h.Fill(x, w)
        
        if count % SKIP == 0:
            print '%10d\t%10d' % (count, index)

            for ii in xrange(4):
                jj = ii+1            
                cpt.cd(jj)
                if isData:
                    hpt[ii].Draw('ep')
                else:
                    hpt[ii].Draw('hist')
            cpt.Update()

            for ii, (h, name) in enumerate(hlist):
                jj = ii+1
                cmet.cd(jj)
                if isData:
                    h.Draw('ep')
                else:
                    h.Draw('hist')
            cmet.Update()
            
        count += 1
        
    w2 = sqrt(w2)
    s2 = sqrt(s2)
    print
    print "number of events (weighted):   %10.4f +/- %-8.4f" % (t1, t2)
    print "number of events (weighted):   %10.4f +/- %-8.4f" % (w1, w2)
    print "number of events (weighted):   %10.4f +/- %-8.4f (pT > 10 GeV)" % \
      (s1, s2)
    print
    
    for ii in xrange(4):
        jj = ii+1            
        cpt.cd(jj)
        if isData:
            hpt[ii].Draw('ep')
        else:
            hpt[ii].Draw('hist')        
    cpt.Update()
    cpt.SaveAs('.png')

    for ii, (h, name) in enumerate(hlist):
        cmet.cd(ii+1)
        if isData:
            h.Draw('ep')
        else:
            h.Draw('hist')
    cmet.Update()
    cmet.SaveAs('.png')        
    sleep(10)
# -------------------------------------------------------------------------
try:     
    main()
except KeyboardInterrupt:
    print '\nciao!\n'
