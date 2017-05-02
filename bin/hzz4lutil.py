# ----------------------------------------------------------------------------
#  File:        hzz4lutil.py
#  Description: Some simple utilities
#  Created:     26-Oct-2016 HBP    
# ----------------------------------------------------------------------------
import os, sys, re
from ROOT import *
from string import *
from math import *
from time import sleep, ctime
from array import array
# ----------------------------------------------------------------------------
def nameonly(s):
    import posixpath
    return posixpath.splitext(posixpath.split(s)[1])[0]
# ----------------------------------------------------------------------------
# Note: "self" is like the "this" pointer in C++
NtupleReaderCount = 1
class NtupleReader:
    def __init__(self,
                 filenames,
                 variables,
                 treename="HZZ4LeptonsAnalysisReduced"):
        # ---------------------------------------        
        # create a chain of root files
        # ---------------------------------------
        global NtupleReaderCount
        NtupleReaderCount += 1
        chain = TChain(treename)
        if type(filenames) == type([]):
            for filename in filenames:
                print filename
                chain.Add(filename)
        else:
            chain.Add(filenames)

        # ---------------------------------------
        # set up which variables to read from ntuples
        # ---------------------------------------
        tree   = chain
        # create struct to cache data from ntuple
        struct = 'struct Event%d{' % NtupleReaderCount
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
        exec('from ROOT import Event%s as Event' % NtupleReaderCount)
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
        # load data into memory
        localindex = chain.LoadTree(index)
        if chain.GetTreeNumber() != self.currentTreeNumber:
            self.currentTreeNumber = chain.GetTreeNumber()
        tree = chain.GetTree()
        tree.GetEntry(localindex)        
# ----------------------------------------------------------------------------
def mkcdf(hist, minbin=1):
    c = [0.0]*(hist.GetNbinsX()-minbin+2)
    j=0
    for ibin in xrange(minbin, hist.GetNbinsX()+1):
        c[j] = c[j-1] + hist.GetBinContent(ibin)
        j += 1
    c[j] = hist.Integral()
    return c

def mkhist1(hname, xtitle, ytitle, nbins, xmin, xmax, **args):
    ymin   = getarg(args, 'ymin', None)
    ymax   = getarg(args, 'ymax', None)
    color  = getarg(args, 'color',   kBlack)
    lstyle = getarg(args, 'lstyle',  1)
    lwidth = getarg(args, 'lwidth',  1)
    ndivx  = getarg(args, 'ndivx',   505)
    ndivy  = getarg(args, 'ndivy',   510)

    h = TH1F(hname, "", nbins, xmin, xmax)		
    h.SetLineColor(color)
    h.SetLineStyle(lstyle)
    h.SetLineWidth(lwidth)

    h.SetMarkerSize(0.8)
    h.SetMarkerColor(color)
    h.SetMarkerStyle(20)

    h.GetXaxis().SetTitle(xtitle)
    h.GetXaxis().SetTitleOffset(1.2);
    h.GetXaxis().SetLimits(xmin, xmax)
    h.SetNdivisions(ndivx, "X")

    h.GetYaxis().SetTitle(ytitle)
    h.GetYaxis().SetTitleOffset(1.6)
    if ymin != None: h.SetMinimum(ymin)
    if ymax != None: h.SetMaximum(ymax)
    h.SetNdivisions(ndivy, "Y")
    return h
#------------------------------------------------------------------------------
def mkhist2(hname, xtitle, ytitle,
        nbinx, xmin, xmax,	
        nbiny, ymin, ymax, **args):
    color  = getarg(args, 'color',   kBlack)
    mstyle = getarg(args, 'mstyle',  20)
    msize  = getarg(args, 'msize',   0.5)
    ndivx  = getarg(args, 'ndivx',   505)
    ndivy  = getarg(args, 'ndivy',   505)

    h = TH2F(hname, "", nbinx, xmin, xmax, nbiny, ymin, ymax)
    h.SetLineColor(color)
    h.SetMarkerColor(color)
    h.SetMarkerSize(msize)
    h.SetMarkerStyle(mstyle)

    h.GetXaxis().SetTitle(xtitle)
    h.GetXaxis().SetTitleOffset(1.3)
    h.SetNdivisions(ndivx, "X")

    h.GetYaxis().SetTitle(ytitle)
    h.GetYaxis().SetTitleOffset(1.3)
    h.SetNdivisions(ndivy, "Y")
    return h
#------------------------------------------------------------------------------
def mkgraph(x, y, xtitle, ytitle, xmin, xmax, **args):
    ymin   = getarg(args, 'ymin', None)
    ymax   = getarg(args, 'ymax', None)
    color  = getarg(args, 'color',   kBlack)
    lstyle = getarg(args, 'lstyle',  1)
    lwidth = getarg(args, 'lwidth',  1)
    msize  = getarg(args, 'msize',   0.5)
    mstyle = getarg(args, 'mstyle', 20)
    ndivx  = getarg(args, 'ndivx', 505)
    ndivy  = getarg(args, 'ndivy', 505)
    name   = getarg(args, 'name', None)

    if y == None:
        g = TGraph()
    else:
        n = len(y)
        xx = x
        if type(x) == type([]):
            xx = array('d')
            for i in range(n): xx.append(x[i])
        yy = y	
        if type(y) == type([]):
            yy = array('d')
            for i in range(n): yy.append(y[i])

        g = TGraph(n, xx, yy)

    if name != None: g.SetName(name)

    g.SetLineColor(color)
    g.SetLineStyle(lstyle)
    g.SetLineWidth(lwidth)

    g.SetMarkerColor(color)
    g.SetMarkerSize(msize)
    g.SetMarkerStyle(mstyle);

    g.GetXaxis().SetTitle(xtitle)
    g.GetXaxis().SetTitleOffset(1.2);
    g.GetXaxis().SetLimits(xmin, xmax)
    g.GetHistogram().SetNdivisions(ndivx, "X")

    g.GetYaxis().SetTitle(ytitle)
    g.GetYaxis().SetTitleOffset(1.6)
    if ymin != None and ymax != None:
        g.GetHistogram().SetAxisRange(ymin, ymax, "Y")
    g.GetHistogram().SetNdivisions(ndivy, "Y")
    return g

def mkgraphErrors(x, y, ex, ey, xtitle, ytitle, xmin, xmax, **args):
    ymin   = getarg(args, 'ymin', None)
    ymax   = getarg(args, 'ymax', None)
    color  = getarg(args, 'color',   kBlack)
    lstyle = getarg(args, 'lstyle',  1)
    lwidth = getarg(args, 'lwidth',  1)
    ndivx  = getarg(args, 'ndivx',   505)
    ndivy  = getarg(args, 'ndivy',   510)

    n = len(y)
    xx = x
    if type(x) == type([]):
        xx = array('d')
        for i in range(n): xx.append(x[i])
    yy = y	
    if type(y) == type([]):
        yy = array('d')
        for i in range(n): yy.append(y[i])

    exx = ex
    if type(ex) == type([]):
        exx = array('d')
        for i in range(n): exx.append(ex[i])
    eyy = ey	
    if type(ey) == type([]):
        eyy = array('d')
        for i in range(n): eyy.append(ey[i])

    g = TGraphErrors(n, xx, yy, exx, eyy)

    g.SetLineColor(color)
    g.SetLineStyle(lstyle)
    g.SetLineWidth(lwidth)

    g.SetMarkerSize(0.8)
    g.SetMarkerColor(color)
    g.SetMarkerStyle(20);

    g.GetXaxis().SetTitle(xtitle)
    g.GetXaxis().SetTitleOffset(1.2);
    g.GetXaxis().SetLimits(xmin, xmax)
    g.GetHistogram().SetNdivisions(ndivx, "X")

    g.GetYaxis().SetTitle(ytitle)
    g.GetYaxis().SetTitleOffset(1.6)
    if ymin != None and ymax != None:
        g.GetHistogram().SetAxisRange(ymin, ymax, "Y")
    g.GetHistogram().SetNdivisions(ndivy, "Y")
    return g
#------------------------------------------------------------------------------
def mkroc(name, hsig, hbkg, lcolor=kBlue, lwidth=2, ndivx=505, ndivy=505):
    from array import array
    csig = mkcdf(hsig)
    cbkg = mkcdf(hbkg)
    npts = len(csig)
    esig = array('d')
    ebkg = array('d')
    for i in xrange(npts):
        esig.append(1 - csig[npts-1-i]/csig[-1])
        ebkg.append(1 - cbkg[npts-1-i]/cbkg[-1])
        
    g = TGraph(npts, ebkg, esig)
    g.SetName(name)
    g.SetLineColor(lcolor)
    g.SetLineWidth(lwidth)

    g.GetXaxis().SetTitle("#font[12]{#epsilon_{b}}")
    g.GetXaxis().SetLimits(0,1)

    g.GetYaxis().SetTitle("#font[12]{#epsilon_{s}}")
    g.GetHistogram().SetAxisRange(0,1, "Y");

    g.GetHistogram().SetNdivisions(ndivx, "X")
    g.GetHistogram().SetNdivisions(ndivy, "Y")
    return g

def mklegend(xx, yy, xw, yw):
    lg = TLegend(xx, yy, xx+xw, yy+yw)
    lg.SetFillColor(kWhite)
    lg.SetTextFont(42)
    lg.SetBorderSize(0)
    lg.SetShadowColor(kWhite)
    return lg
