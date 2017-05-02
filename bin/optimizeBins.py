#!/usr/bin/env python
#------------------------------------------------------------------
# File: optimizeBins.py
# Description: try to bin data in an optimal way
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
          'f_pfmet']
OFIELDS = FIELDS + ['f_D']

def read(filename, mlp):
    ntuple = NtupleReader(filename, FIELDS)

    records = [0]*ntuple.size()
    total = 0.0
    for row in xrange(ntuple.size()):
        ntuple.read(row)
        
        mass4l  = ntuple('f_mass4l')
        Dbkgkin = ntuple('f_D_bkg_kin')
        pfmet   = ntuple('f_pfmet')
        D = mlp(mass4l, Dbkgkin, pfmet)
        w = ntuple('f_weight')
        records[row] = (D, w)

        total += w
        
        if row % 10000 == 0:
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
    nbins = 25 
    turtle= Turtle(files, names, 'HZZ4LeptonsAnalysisReduced', nbins)

    
    MLPname     = 'm4lmelamet'
    datfilename = 'ntuple_data.root'
    bkgfilename = ['ntuple_bkg.root', 'ntuple_higgs.root']
    
    # compile code
    code = open('%s.cpp' % MLPname).read()
    gROOT.ProcessLine(code)
    mlp  = eval(MLPname)

    data, wdata = read(datfilename, mlp)
    print
    bkg,  wbkg  = read(bkgfilename, mlp)

    total  = sum(wdata)
    btotal = sum(wbkg)
    scale  = total/btotal

    print 'data count: %9.0f' % total
    print 'bkg count:   %10.1f' % btotal
    
    print "\nbinning data..."
    point = vector('double')(1)
    for D in data:
        point[0] = D
        turtle.Fill(point)
    count = turtle.GetBinContents()

    print "\nbinning background..."
    turtle.Reset()
    for ii, D in enumerate(bkg):
        point[0] = D
        w = wbkg[ii] * scale
        turtle.Fill(point, w)
    bcount = turtle.GetBinContents()    

    v = []
    for ii, c in enumerate(count):
        x = turtle.GetBinCenter(ii)[0]
        w = turtle.GetBinWidth(ii)[0]
        b = bcount[ii]
        v.append((x, w, b, c))
    v.sort()

    out = open('data_MC.txt', 'w')
    record = '%3s %10s\t%10s %10s' % ('bin', 'boundary', 'pred', 'data')
    print record
    out.write('%s\n' % record)
    
    from array import array
    ibins = array('d')
    jj = 0
    bnd = 0.0
    ibins.append(0)
    for ii, (x, w, b, c) in enumerate(v):
        bnd += w
        record = '%3d %10.6f\t%10.2f %10.1f' % (ii, bnd, b, c)
        print record
        out.write('%s\n' % record)
        ibins.append(bnd)
    out.close()

    #------------------------------------------------------------------
    # plot
    #------------------------------------------------------------------
    xtitle = \
      '#font[12]{D}(#font[12]{m}_{4l}, '\
      '#font[12]{D}^{bkg}_{kin}, ' \
      '#font[12]{E}_{T}^{miss})'
      
    MLPname     = 'm4lmelamet'
    bkgfilename = ['ntuple_bkg.root', 'ntuple_higgs.root']
    datfilename = 'ntuple_data.root'
    
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

    nbins = len(ibins)-1

    # DATA
    mcolor  = kBlack
    hd = TH1F('hd', '', nbins, ibins)
    hd.GetXaxis().SetTitle(xtitle)
    hd.Sumw2()     # needed to handle weights correctly
    hd.GetXaxis().SetNdivisions(505)
    hd.GetYaxis().SetNdivisions(505)
    hd.SetMarkerColor(mcolor)
    hd.SetMarkerStyle(20)
    hd.SetLineColor(mcolor)
    hd.SetLineWidth(2)
    
    # BACKGROUND
    mcolor  = kMagenta+1
    hb  = TH1F('hb', '', nbins, ibins)
    hb.GetXaxis().SetTitle(xtitle)
    hb.Sumw2()     # needed to handle weights correctly
    hb.GetXaxis().SetNdivisions(505)
    hb.GetYaxis().SetNdivisions(505)
    hb.SetFillColor(mcolor)
    hb.SetFillStyle(3003)
    hb.SetLineWidth(2)
    
    print "\nbinning data..."
    point = vector('double')(1)
    for D in data:
        hd.Fill(D)

    print "binning background..."
    for ii, D in enumerate(bkg):
        hb.Fill(D, wbkg[ii])

    c1 = TCanvas("figures/f_data_MC", 'data vs MC', 10, 10, 500, 500)
    c1.cd()
    c1.SetLogx()
    hb.Scale(hd.Integral()/hb.Integral())
    hb.SetMaximum(1.3*hd.GetMaximum())
    hb.Draw("hist")
    hd.Draw("ep same")
    CMS_lumi.CMS_lumi(c1, iPeriod, iPos)
    c1.Update()
    gSystem.ProcessEvents()    
    c1.SaveAs('.png')
    sleep(10)
#----------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "\nciao!"
