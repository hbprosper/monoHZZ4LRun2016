#!/usr/bin/env python
#------------------------------------------------------------------
# File: plotm4l.py
# Description: plot m4l
# Created: 09-Feb-2017 HBP
# Happy Birthday to Olivia (33)
#------------------------------------------------------------------
import os, sys
from hzz4lutil import *
from ROOT import *
from time import sleep
from glob import glob
import CMS_lumi, tdrstyle
#------------------------------------------------------------------
getsample = re.compile('(?<=_).*(?=[].]root)')

def mkhist(hname, xtitle, nbins, xmin, xmax, fcolor=20, lcolor=kBlack):
    h  = TH1F(hname, '', nbins, xmin, xmax)
    h.GetXaxis().SetTitle(xtitle)
    h.Sumw2()
    h.GetXaxis().SetNdivisions(505)
    h.GetYaxis().SetNdivisions(505)
    h.SetLineWidth(2)
    h.SetLineColor(lcolor)
    if fcolor > 0:
        h.SetFillColor(fcolor)
        h.SetFillStyle(3001)
    return h
            
def readAndFill(filename, c, h, option='hist'):
    ntuple = NtupleReader(filename, ['f_weight',
                                     'f_mass4l',
                                     'f_outlier'])
    exec('hFill=h.Fill')
    ii = 0
    for row in xrange(ntuple.size()):
        ntuple.read(row)
        if ntuple('f_outlier'): continue
                 
        weight= ntuple('f_weight')
        mass  = ntuple('f_mass4l')
        h.Fill(mass, weight)

        if ii % 10000 == 0:
            c.cd()
            h.Draw(option)
            c.Update()
            gSystem.ProcessEvents()
        ii += 1
        
    c.cd()
    h.Draw(option)
    c.Update()
    gSystem.ProcessEvents()
    c.SaveAs('.png')
    exec('del hFill')
    sleep(3)    
#------------------------------------------------------------------
def main():
    if len(sys.argv) > 1:
        fstate = sys.argv[1]
    else:
        fstate = '4mu'
        
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
    
    # change the CMS_lumi variables (see CMS_lumi.py)
    iPeriod = 4
    iPos    = 0
    CMS_lumi.relPosX = 0.12
    CMS_lumi.lumi_13TeV = "30.0 fb^{-1}"
    CMS_lumi.writeExtraText = 1
    CMS_lumi.extraText = "Simulation"

    os.system('mkdir -p figures')
    cd = TCanvas("figures/f_mass4l_%s_data" % fstate, 'm4l',   10, 10, 500, 500)
    cb = TCanvas("figures/f_mass4l_%s_bkg"  % fstate, 'm4l',  520, 10, 500, 500)
    ch = TCanvas("figures/f_mass4l_%s_higgs"% fstate, 'm4l', 1040, 10, 500, 500)

    FILES = [(cd, 'ntuple_%s_data.root' % fstate, 'ep',   20),
             (cb, 'ntuple_%s_bkg.root'  % fstate, 'hist', kMagenta+1),
             (ch, 'ntuple_%s_higgs.root'% fstate, 'hist', kCyan+1)]

    hfile = TFile('m4lfit/h_%s.root' % fstate, 'recreate')
    h = {}
    for ii, (c, filename, option, color) in enumerate(FILES):
        sample = getsample.findall(filename)[0]
        hname = 'hm4l_%s' % sample
        print hname
        h[sample] = mkhist(hname, '#font[12]{m}_{4l}', 25, 80, 180, color)
        readAndFill(filename, c, h[sample])        
    hfile.Write()
#----------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "\nciao!"
