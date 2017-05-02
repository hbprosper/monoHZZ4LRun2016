#!/usr/bin/env python
#------------------------------------------------------------------
# File: plotVars.py
# Description: plot specified variables
# Created: 09-Feb-2017 HBP
# Happy Birthday to Olivia (33)
#------------------------------------------------------------------
import os, sys
from histutil import *
from ROOT import *
from time import sleep
from glob import glob
import CMS_lumi, tdrstyle
#------------------------------------------------------------------
VARIABLES = '''
f_lept1_pt    100  0 300
f_lept2_pt    100  0 300
f_lept3_pt    100  0 300
f_lept4_pt    100  0 300
f_mass4l      100 70 170
f_pt4l        100  0 300
f_pfmet       100  0 300
f_mT          100  0 300
f_Z1mass      100  0 200
f_Z2mass      100  0 200
f_D_bkg_kin   100  0   1
f_D_bkg       100  0   1
'''
VARIABLES = map(lambda x: (x[0], atoi(x[1]), atof(x[2]), atof(x[3])),
                               map(split, split(strip(VARIABLES),'\n')))
FIELDS = map(lambda x: x[0], VARIABLES)
#------------------------------------------------------------------
def readAndFill(filename, c, h, 
                    option='hist',
                    treename='HZZ4LeptonsAnalysisReduced'):
    ntuple = Ntuple(filename, treename)

    ii = 0
    total1 = 0.0
    total2 = 0.0
    etotal2= 0.0
    for row, event in enumerate(ntuple):
        
        weight = event.f_weight
        total1 += weight
        if event.f_outlier:
            continue
        total2  += weight         
        etotal2 += weight*weight
        
        for jj, v in enumerate(FIELDS):
            h[jj].Fill(event.__getattr__(v), weight)

        if ii % 10000 == 0:
            for jj in xrange(len(FIELDS)):
                c.cd(jj+1)
                h[jj].Draw(option)
            c.Update()
            gSystem.ProcessEvents()
        ii += 1
        
    c.cd()
    for jj in xrange(len(FIELDS)):
        c.cd(jj+1)
        h[jj].Draw(option)
        c.Update()
    gSystem.ProcessEvents()    
    c.SaveAs('.png')
    sleep(3)    
#------------------------------------------------------------------
def main():
    argv = sys.argv[1:]
    argc = len(argv)
    if argc < 1:
        sys.exit('''
    Usage:
        ./plotVars.py file1 [file2...]
    ''')
    filenames = argv
    
    # ---------------------------------------
    # set up some standard graphics style
    # ---------------------------------------
    tdrstyle.setTDRStyle()
    gStyle.SetPadRightMargin(0.12)
    gStyle.SetOptStat('eimr')
    gStyle.SetStatFont(42)
    gStyle.SetStatFontSize(0.03)
    gStyle.SetStatBorderSize(1)
    gStyle.SetStatH(0.2)
    gStyle.SetStatW(0.3)
    gStyle.SetStatX(0.83)
    gStyle.SetStatY(0.93)    
    
    # change the CMS_lumi variables (see CMS_lumi.py)
    iPeriod = 4
    iPos    = 0
    CMS_lumi.relPosX = 0.12
    CMS_lumi.lumi_13TeV = "36.0 fb^{-1}"
    CMS_lumi.writeExtraText = 1
    CMS_lumi.extraText = "Simulation"

    os.system('mkdir -p histos')
    
    canvas= []
    hist  = []
    hfile = []
    color = 2
    for ii, filename in enumerate(filenames):
        name    = replace(nameonly(filename), 'ntuple_', '')
        outfile = 'histos/histos_%s.root' % name
        cname   = 'histos/fig_%s' % name
        if name == 'data':
            option = 'ep'
        else:
            option = 'hist'

        canvas.append(TCanvas(cname, cname, 10, 10, 1200, 900))
        canvas[-1].Divide(4, 3)

        hfile.append(TFile(outfile, 'recreate'))
        color = 20+ii
        h = []
        for field, xbins, xmin, xmax in VARIABLES:
            hname = '%s_%s' % (name, field)
            h.append(mkhist1(hname, field, 'count', xbins, xmin, xmax))
            h[-1].SetFillColor(color)
            h[-1].SetFillStyle(3002)
        hist.append(h)
        
        readAndFill(filename, canvas[-1], h, option)
        canvas[-1].cd()
        CMS_lumi.CMS_lumi(canvas[-1], iPeriod, iPos)
        
        hfile[-1].cd()
        for c in canvas:
            c.Write()
        hfile[-1].Write()
        sleep(5)
#----------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "\nciao!"
