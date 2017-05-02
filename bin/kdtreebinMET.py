#!/usr/bin/env python
#------------------------------------------------------------------
# File: kdtreebinMET.py
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
              'f_finalstate',
              'f_pfmet']
#------------------------------------------------------------------
def read(filename, skip=10000):
    ntuple = NtupleReader(filename, FIELDS)

    total = 0.0
    records = []
    for row in xrange(ntuple.size()):
        ntuple.read(row)
        if row % skip == 0:
            print '.',; sys.stdout.flush()
        
        f = ntuple('f_finalstate')
        if f < 1: continue
            
        x = ntuple('f_pfmet')
        w = ntuple('f_weight')
        records.append((x, w))
        total += w
    print
    
    records.sort()
    nrecs  = len(records)
    data   = [0]*nrecs
    weight = [0]*nrecs
    for ii, (x, w) in enumerate(records):
        data[ii]   = x
        weight[ii] = w

    print '=> number of events: %10.2f (%d)' % (total, ntuple.size())       
    return (data, weight)
#------------------------------------------------------------------
def main():

    argv = sys.argv[1:]
    argc = len(argv)
    if argc > 0:
        nbins = atoi(argv[0])
    else:
        nbins = 20
        
    gSystem.AddDynamicPath('%s/Projects/turtle/lib' % os.environ['HOME'])
    gSystem.Load("libturtle")

    files = vector('string')(1, 'bkg.root')
    names = vector('string')(1, 'f_pfmet')

    turtle= Turtle(files, names, 'HZZ4LeptonsAnalysisReduced', nbins)
    
    datfilename = 'ntuple_data.root'
    bkgfilename = ['ntuple_bkg.root', 'ntuple_higgs.root']
    sigfilename = 'ntuple_ZpBary_MZp00500_MA00150.root'

    data, wdata = read(datfilename, 50)
    bkg,  wbkg  = read(bkgfilename)
    sig,  wsig  = read(sigfilename, 1000)

    dtotal = sum(wdata)
    btotal = sum(wbkg)
    stotal = sum(wsig)
    scale  = dtotal/btotal

    
    print 'data count:     %8.0f'   % dtotal
    print 'bkg count:       %10.2f' % btotal
    print 'sig count:       %10.2f' % stotal
    print 'number of bins: %8d' % nbins
    
    print "\nbin data..."
    point = vector('double')(1)
    for D in data:
        point[0] = D
        turtle.Fill(point)
    dcount = turtle.GetBinContents()
    dvar   = turtle.GetBinVariances()

    print "bin background..."
    turtle.Reset()
    for ii, D in enumerate(bkg):
        point[0] = D
        w = wbkg[ii] * scale
        turtle.Fill(point, w)
    bcount = turtle.GetBinContents()
    bvar   = turtle.GetBinVariances()

    print "bin signal..."
    turtle.Reset()
    for ii, D in enumerate(sig):
        point[0] = D
        w = wsig[ii] # * scale
        turtle.Fill(point, w)
    scount = turtle.GetBinContents()
    svar   = turtle.GetBinVariances()        

    gof = 0.0
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

        gof += (d - b)**2/dvar[ii]
        
        v.append((x, w, b, berr, d, derr, s, serr))
    v.sort()

    gof /= nbins


    
    out = open('data_MC_MET_%3.3d.txt' % nbins, 'w')
    record = '%3s %10s\t%10s %10s %10s' % ('bin',
                                               'boundary',
                                               'pred', 'data', 'signal')
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

    print 'chi2 / nbins = %10.3f' % gof
    #------------------------------------------------------------------
    # plot
    #------------------------------------------------------------------
    xtitle = '#font[12]{f}(#font[12]{E}_{T}^{miss})'
    
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

    c1 = TCanvas("figures/f_data_MC_MET", 'data vs MC', 10, 10, 500, 500)
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

    clog = TCanvas("figures/f_data_MC_MET_log", 'data vs MC', 520, 10, 500, 500)
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
