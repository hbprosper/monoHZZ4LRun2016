#!/usr/bin/env python
#------------------------------------------------------------------
# File: kdtreebinBNN.py
# Description: bin using KDTree
# Created: 02-07-2017 HBP
#------------------------------------------------------------------
import os, sys
from hzz4lutil import *
from ROOT import *
from time import sleep
from glob import glob
import CMS_lumi, tdrstyle
#------------------------------------------------------------------
FIELDS = ['f_weight',
          'f_mass4l',
          'f_D_bkg_kin',
          'f_pfmet',
          'f_finalstate']
OFIELDS = FIELDS + ['f_D']

def read(filename, mlp, skip=10000):
    ntuple = NtupleReader(filename, FIELDS)

    records = [0]*ntuple.size()
    total = 0.0
    for row in xrange(ntuple.size()):
        ntuple.read(row)
        f = ntuple('f_finalstate')
        if f < 1: continue
        
        mass4l  = ntuple('f_mass4l')
        Dbkgkin = ntuple('f_D_bkg_kin')
        pfmet   = ntuple('f_pfmet')
        weight  = ntuple('f_weight')
        
        D = mlp(mass4l, Dbkgkin, pfmet)
        
        records[row] = (D, weight)

        total += weight
        
        if row % skip == 0:
            print '.',; sys.stdout.flush()
    
    records.sort()
    data   = [0]*len(records)
    weight = [0]*len(records)
    for ii, (d, w) in enumerate(records):
        data[ii] = d
        weight[ii] = w

    print
    print '=> number of events: %10.2f (%d)' % (total, ntuple.size())       
    return (data, weight)
#------------------------------------------------------------------
def main():
    gSystem.AddDynamicPath('%s/Projects/turtle/lib' % os.environ['HOME'])
    gSystem.Load("libturtle")

    files = vector('string')(1, 'bkg.root')
    names = vector('string')(1, 'f_D')
    nbins = 15 
    turtle= Turtle(files, names, 'HZZ4LeptonsAnalysisReduced', nbins)

    
    MLPname     = 'm4lmelamet'
    datfilename = 'ntuple_data.root'
    bkgfilename = ['ntuple_bkg.root', 'ntuple_higgs.root']
    sigfilename = 'ntuple_ZpBary_MZp00500_MA00150.root'
    
    # compile code
    code = open('%s.cpp' % MLPname).read()
    gROOT.ProcessLine(code)
    mlp  = eval(MLPname)

    data, wdata = read(datfilename, mlp, 10)
    bkg,  wbkg  = read(bkgfilename, mlp)
    sig,  wsig  = read(sigfilename, mlp, 1000)

    dtotal = sum(wdata)
    btotal = sum(wbkg)
    stotal = sum(wsig)
    scale  = dtotal/btotal

    print 'data count: %9.0f' % dtotal
    print 'bkg count:   %10.1f' % btotal
    print 'sig count:   %10.1f' % stotal
    
    print "\nbinning data..."
    point = vector('double')(1)
    for D in data:
        point[0] = D
        turtle.Fill(point)
    dcount = turtle.GetBinContents()
    dvar   = turtle.GetBinVariances()

    print "\nbinning background..."
    turtle.Reset()
    for ii, D in enumerate(bkg):
        point[0] = D
        w = wbkg[ii] * scale
        turtle.Fill(point, w)
    bcount = turtle.GetBinContents()
    bvar   = turtle.GetBinVariances()

    print "\nbinning signal..."
    turtle.Reset()
    for ii, D in enumerate(sig):
        point[0] = D
        w = wsig[ii]# * scale
        turtle.Fill(point, w)
    scount = turtle.GetBinContents()
    svar   = turtle.GetBinVariances()        

    v = []
    for ii in xrange(nbins):
        x = turtle.GetBinCenter(ii)[0]
        w = turtle.GetBinWidth(ii)[0]
        
        b    = bcount[ii]
        berr = sqrt(bvar[ii])
        
        d    = dcount[ii]
        derr = sqrt(dvar[ii])

        s    = scount[ii]
        serr = sqrt(svar[ii])        
        
        v.append((x, w, b, berr, d, derr, s, serr))
    v.sort()

    out = open('data_MC.txt', 'w')
    record = '%3s %10s\t%10s %10s %10s' % ('bin',
                                               'boundary',
                                               'pred', 'data', 'ZpB500-150')
    print record
    out.write('%s\n' % record)
    
    bnd = 0.0
    counts = []
    for ii, (x, w, b, berr, d, derr, s, serr) in enumerate(v):
        bnd += w
        record = '%3d %10.6f\t%10.2f %10.1f %10.6f' % (ii, bnd, b, d, s)
        print record
        out.write('%s\n' % record)

        counts.append((ii+1, bnd, b, berr, d, derr, s, serr))
    out.close()

    #------------------------------------------------------------------
    # plot
    #------------------------------------------------------------------
    xtitle = \
      '#font[12]{D}(#font[12]{m}_{4l}, '\
      '#font[12]{D}^{bkg}_{kin}, ' \
      '#font[12]{E}_{T}^{miss})'
    
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
    CMS_lumi.lumi_13TeV = "30.0 fb^{-1}"
    CMS_lumi.writeExtraText = 1
    CMS_lumi.extraText = "Simulation"

    # DATA
    mcolor  = kBlack
    hd = TH1F('hd', '', nbins, 0, 1)
    hd.GetXaxis().SetTitle(xtitle)
    hd.GetXaxis().SetNdivisions(505)
    hd.GetYaxis().SetNdivisions(505)
    hd.SetMarkerColor(mcolor)
    hd.SetMarkerStyle(20)
    hd.SetLineColor(mcolor)
    hd.SetLineWidth(2)
    
    # BACKGROUND
    mcolor  = kMagenta+1
    hb  = TH1F('hb', '', nbins, 0, 1)
    hb.GetXaxis().SetTitle(xtitle)
    hb.Sumw2()     # needed to handle weights correctly
    hb.GetXaxis().SetNdivisions(505)
    hb.GetYaxis().SetNdivisions(505)
    hb.SetFillColor(mcolor)
    hb.SetFillStyle(3003)
    hb.SetLineWidth(2)

    # SIGNAL
    mcolor  = kCyan+1
    hs  = TH1F('hs', '', nbins, 0, 1)
    hs.GetXaxis().SetTitle(xtitle)
    hs.Sumw2()     # needed to handle weights correctly
    hs.GetXaxis().SetNdivisions(505)
    hs.GetYaxis().SetNdivisions(505)
    hs.SetFillColor(mcolor)
    hs.SetFillStyle(3003)
    hs.SetLineWidth(2)    
    
    print "\nfill histograms..."
    for jj, bnd, b, berr, d, derr, s, serr in counts:
        hb.SetBinContent(jj, b)
        hb.SetBinError(jj, berr)
        
        hd.SetBinContent(jj, d)
        hd.SetBinError(jj, derr)

        hs.SetBinContent(jj, s)
        hs.SetBinError(jj, serr)        

    c1 = TCanvas("figures/f_data_MC", 'data vs MC', 10, 10, 500, 500)
    c1.cd()
    hb.SetMinimum(0)
    hb.SetMaximum(1.3*hd.GetMaximum())
    hb.Draw("hist")
    hs.Draw("histsame")
    hd.Draw("epsame")
    CMS_lumi.CMS_lumi(c1, iPeriod, iPos)
    c1.Update()
    gSystem.ProcessEvents()    
    c1.SaveAs('.png')

    clog = TCanvas("figures/f_data_MC_log", 'data vs MC', 520, 10, 500, 500)
    clog.cd()
    clog.SetLogy()
    hbc = hb.Clone('hbc')
    hbc.SetMinimum(1e-4)
    hbc.SetMaximum(1e2*hd.GetMaximum())
    hbc.Draw("hist")
    hs.Draw("histsame")
    hd.Draw("epsame")
    CMS_lumi.CMS_lumi(c1, iPeriod, iPos)
    clog.Update()
    gSystem.ProcessEvents()    
    clog.SaveAs('.png')    
    sleep(10)
#----------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "\nciao!"
