#!/usr/bin/env python
#------------------------------------------------------------------
# File: plotROC.py
# Description: plot ROCs
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
def mkhist(hname, xtitle, nbins, xmin, xmax, color=kBlack):
    h  = TH1F(hname, '', nbins, xmin, xmax)
    h.GetXaxis().SetTitle(xtitle)
    h.Sumw2()
    h.GetXaxis().SetNdivisions(505)
    h.GetYaxis().SetNdivisions(505)
    h.SetLineWidth(2)
    h.SetLineColor(color)
    #h.SetFillColor(color)
    #h.SetFillStyle(3001)
    return h
            
def readAndFill(filename, bnn, c1, h1, c2, h2, option='hist'):
    ntuple = NtupleReader(filename, ['f_weight',
                                     'f_mass4l',
                                     'f_D_bkg_kin',
                                     'f_pfmet'])
    exec('h1Fill=h1.Fill')
    exec('h2Fill=h2.Fill')
    for row in xrange(ntuple.size()):
        ntuple.read(row)

        weight= ntuple('f_weight')
        mass4l= ntuple('f_mass4l')
        Dbkg  = ntuple('f_D_bkg_kin')
        met   = ntuple('f_pfmet')
        D     = bnn(mass4l, Dbkg, met) 
        h1.Fill(D, weight)
        h2.Fill(met, weight)

        if row % 10000 == 0:
            c1.cd()
            c1.SetLogy()
            h1.Draw(option)
            c1.Update()
            
            c2.cd()
            c2.SetLogy()
            h2.Draw(option)
            c2.Update()            
            gSystem.ProcessEvents()
            
    c1.cd()
    c1.SetLogy()    
    h1.Draw(option)
    c1.Update()
    
    c2.cd()
    c2.SetLogy()
    h2.Draw(option)
    c2.Update()               
    gSystem.ProcessEvents()    
    exec('del h1Fill; del h2Fill')
    sleep(3)    
#------------------------------------------------------------------
def main():

    gROOT.ProcessLine(open('m4lmelamet.cpp').read())
    net = m4lmelamet
    
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
    c1 = TCanvas("figures/f_bnn", 'bnn', 10, 10, 500, 500)
    c2 = TCanvas("figures/f_met", 'met',520, 10, 500, 500)

    czprime = TCanvas("figures/f_MET_Zprime", 'MET',
                           10, 530, 500, 500)
    czpbary = TCanvas("figures/f_MET_ZpBary", 'MET',
                           520, 530, 500, 500)    

    
    fsignals= glob('ntuple_Z*.root')
    fsignals.sort()

    FILES = [('ntuple_bkg.root', '_b', kMagenta+1)]
    for filename in fsignals:
        name = nameonly(filename)
        name = replace(name, 'ntuple_', '')
        FILES.append((filename, name, kCyan+1))

    colorbase = 50
    option = 'hist'        
    h = {}
    for ii, (filename, postfix, color) in enumerate(FILES):
        bnn = 'bnn%s' % postfix
        met = 'met%s' % postfix
        print bnn, met
        
        h[bnn] = mkhist(bnn, '#font[12]{D}_{3D}', 10000, 0, 1, color)
        
        h[met] = mkhist(met, '#font[12]{E}_{T}^{miss} (GeV)',
                             200, 0, 1000, color)

        readAndFill(filename, net, c1, h[bnn], c2, h[met])

        jj = ii - 1
        jj = jj % 10
        if color == 0:
            colorbase -= 10
        color = colorbase + jj
        if find(postfix, 'ZpBary') > -1:
            h[met].SetLineColor(color)
            h[met].SetLineWidth(2)
            czpbary.cd()
            czpbary.SetLogy()
            h[met].Draw(option)
            czpbary.Update()
        elif find(postfix, 'Zprime') > -1:
            h[met].SetLineColor(color)
            h[met].SetLineWidth(2)
            czprime.cd()
            czprime.SetLogy()
            h[met].Draw(option)
            czprime.Update()
        option = 'histsame'
        gSystem.ProcessEvents()

        # plot ROCs
        if ii < 1:
            h['bnn_b'].Smooth()
            h['met_b'].Smooth()
            continue
        h[bnn].Smooth()
        h[met].Smooth()
    
        hroc1 = mkroc('hroc1', h[bnn], h['bnn_b'], kRed)
        hroc2 = mkroc('hroc2', h[met], h['met_b'], kBlue)
        
        croc = TCanvas("figures/f_ROC_%s" % postfix, 'ROC %s' % postfix,
                           10, 10, 500, 500)
        croc.SetLogx()
        hroc1.Draw('ac')
        hroc2.Draw('csame')

        legend = mklegend(0.4, 0.3, 0.25, 0.25)
        legend.SetTextSize(0.04)
        legend.SetHeader(postfix)
        legend.AddEntry(hroc1,
                        '#font[12]{D}(#font[12]{m}_{4l},'\
                        '#font[12]{D}_{bkg}^{kin},#font[12]{E}_{T}^{miss})','l')
        legend.AddEntry(hroc2,
                        '#font[12]{E}_{T}^{miss}','l')
        legend.Draw()
        croc.Update()
        gSystem.ProcessEvents()    
        croc.SaveAs('.png')
        del hroc1
        del hroc2
        sleep(1)
        
    czpbary.SaveAs('.png')
    czprime.SaveAs('.png')
#----------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "\nciao!"
