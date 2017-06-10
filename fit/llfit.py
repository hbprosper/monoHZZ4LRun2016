#!/usr/bin/env python
#------------------------------------------------------------------------------
#  File: chi2fit.py
#  Description: Same as pgammafit.py, except that the QCD strength is left
#               un-scaled so that it is merely the scale factor between
#               the QCD in the signal region and QCD in the control region.
#  Created: 20-Sep-2010 Harrison B. Prosper
#  Updated: 04-Jun-2016 HBP - generalization for Sam
#------------------------------------------------------------------------------
import os, sys
from ROOT import *
from histutil import mklegend, Scribe
from time import sleep
from math import sqrt
from string import capitalize
from array import array
import CMS_lumi, tdrstyle
#------------------------------------------------------------------------------
HNAME = 'hm4l'
PATH  = '70-140'
PATH  = '70-270-BG'
PATH  = '70-270'
#PATH  = '70-190'
FAKEDATA  =  False

MAXITER   = 10000
TOLERANCE = 1.e-6
METHOD    = 'MIGRAD'
#------------------------------------------------------------------------------
def getContents(h):
    c = vector("double")()
    e = vector("double")()
    for i in xrange(h.GetNbinsX()):
        binx = i+1
        c.push_back( h.GetBinContent(binx) )
        e.push_back( h.GetBinError(binx) )
    return (c, e)

def fakeData(hdata, h, f):
    ndata = int(hdata.Integral())
    # create a fake data set
    b = ndata * (1 - f)
    s = ndata * f
    h[0].Scale(b/h[0].Integral())
    h[1].Scale(s/h[1].Integral())

    hdata.Reset()
    hfun = h[0].Clone('hfun')
    hfun.Add(h[1])

    for ii in xrange(ndata):
        hdata.Fill(hfun.GetRandom())
#------------------------------------------------------------------------------
FINALSTATES = {'2e2mu': '2#font[12]{e}2#font[12]{#mu}',
               '4e'   : '4#font[12]{e}',
               '4mu'  : '4#font[12]{#mu}',
               ''     : '2#font[12]{e}2#font[12]{#mu}+4#font[12]{e}+'\
                        '4#font[12]{#mu}'}
#------------------------------------------------------------------------------
def main():
    if len(sys.argv) > 1:
        fstate = sys.argv[1]
    else:
        fstate = ''
    decor = fstate
    if decor != '':
        decor += '_'
        
    sources = [('%s/fig_%sbkg.root'   % (PATH, decor), 'bkg',   kMagenta+1),
               ('%s/fig_%shiggs.root' % (PATH, decor), 'higgs', kAzure+1)]
    
    # ---------------------------------------        
    # get data histogram
    # ---------------------------------------    
    filename = '%s/fig_%sdata.root' % (PATH, decor)
    fdata = TFile(filename)
    if not fdata.IsOpen():
        sys.exit("** can't open file %s" % filename)        
    hdata = fdata.Get(HNAME)
    if not hdata: sys.exit("** can't find hbnn")
    
    # ---------------------------------------        
    # get source histograms
    # ---------------------------------------    
    f = []
    h = []
    for i,(filename,hname,color) in enumerate(sources):
        f.append(TFile(filename))
        if not f[-1].IsOpen():
            sys.exit("** can't open file %s" % f[-1])
        h.append( f[-1].Get(HNAME).Clone(hname) )
        if not h[-1]: sys.exit("** can't find hbnn")
        
    if FAKEDATA: fakeData(hdata, h, 0.1065)
    print '\tcount(%s):\t%8.1f' % ('data', hdata.Integral())
    
    # ---------------------------------------
    # set up some standard graphics style
    # ---------------------------------------
    tdrstyle.setTDRStyle()
    #gStyle.SetCanvasPreferGL(True)    
    gStyle.SetPadRightMargin(0.12)
    #gStyle.SetOptStat('ei')
    gStyle.SetOptStat('i')
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
    CMS_lumi.extraText = "Preliminary"
    vdouble = vector("double")


    # ---------------------------------------    
    # plot data
    # ---------------------------------------
    ymax  = 1.2*hdata.GetMaximum()
    ii    = int(ymax / 20)
    ymax  = (ii+1)*20
                
    hdata.SetMaximum(ymax)
    hdata.SetNdivisions(505, 'X')

    xbins = int(hdata.GetNbinsX())
    width = hdata.GetXaxis().GetBinWidth(1)
    xmin  = int(hdata.GetXaxis().GetBinLowEdge(1))
    xmax  = int(hdata.GetXaxis().GetBinLowEdge(xbins)+width)

    postfix = "_%s_%3.3d_%3.3d" % (HNAME, xmin, xmax)
    
    cname = "fig_%sdata_%s" % (decor, postfix)
    canvas = TCanvas(cname, cname, 10, 10, 500, 500)
    canvas.cd()
    hdata.Draw("ep gl")
    canvas.Update()
    canvas.SaveAs('.png')
    gSystem.ProcessEvents()        
    sleep(0.5)
    del canvas

    # ---------------------------------------
    # plot sources
    # ---------------------------------------    
    for i,(filename,hname,color) in enumerate(sources):        
        cname = "fig_%s%s%s" % (decor, hname, postfix)
        canvas = TCanvas(cname, cname, 10, 10, 500, 500)        
        canvas.cd()
        h[i].SetNdivisions(505, 'X')
        h[i].Draw("hist gl")
        canvas.Update()
        canvas.SaveAs('.png')
        gSystem.ProcessEvents()
        sleep(0.5)
        del canvas

    # create TFractionFitter object
    hsrcs = TObjArray(len(sources))
    hsrcs.Add(h[0])
    hsrcs.Add(h[1])

    fitter = TFractionFitter(hdata, hsrcs)

    status = fitter.Fit()
    
    if status == 0:
        sys.exit("** fit failed: status")

    # Print results
    total = int(hdata.Integral())
    print "-"*80
    print "total observed count: %d" % total    
    print "%-10s\t%10s" %  ('source', "    estimated count")
    x1 = 0.0
    x2 = 0.0
    mode   = [0]*len(sources)
    error  = [0]*len(sources)
    for index, (fname, src, color) in enumerate(sources):
        value  = Double()
        dvalue = Double()            
        fitter.GetResult(index, value, dvalue)
        mode[index] = value * total
        error[index]= dvalue * total
        print "%-10s\t%10.1f +/-%- 10.1f" % \
              (src, mode[index], error[index])
        x1 += mode[index]
        x2 += error[index]**2
    x2 = sqrt(x2)
    print '-'*35
    print "%-10s\t%10.1f +/-%- 10.1f" % ('total', x1, x2)

    t = []
    for index, (fname, src, color) in enumerate(sources):    
        h[index].SetLineColor(color+2)
        h[index].SetFillColor(color)
        t.append(h[index].Integral())
        h[index].Scale(mode[index]/h[index].Integral())
        h[index].SetMaximum(ymax)
        
    hdata.SetMinimum(1.e-3)
    hdata.SetMaximum(ymax)
    
    # compute GOF measure
    chisq = fitter.GetChisquare()
    ndf   = fitter.GetNDF()
    p     = fitter.GetProb()
    print '\nchisq/NDF = %10.1f/%d = %10.2f\t%8.3f\n' % (chisq, ndf,
                                                             chisq/ndf, p)

    ht = h[0].Clone('theory')
    ht.Add(h[1])
    ht.SetMaximum(ymax)
    
    hs = THStack('hs', '')
    hs.Add(h[0])
    hs.Add(h[1])
    hs.SetMaximum(ymax)
    
    lg = mklegend(0.35, 0.72, 0.25, 0.2)
    lg.SetHeader('events(%s)' % FINALSTATES[fstate])
                     
    lg.SetTextSize(0.04)
    lg.AddEntry(hdata, 'data  %4.0f' % hdata.Integral(), 'p')
    for ii, (fname, src, color) in enumerate(sources):
        src = capitalize(src)
        lg.AddEntry(h[ii],  '%-5s   %6.1f #pm %-6.1f (#color[4]{%6.1f})' \
                        % (src, mode[ii], error[ii], t[ii]), 'f')

    scribe = Scribe(0.43, 0.68)

    cname = "fig_%sresult%s" % (decor, postfix)
    cfit = TCanvas(cname, cname, 520, 10, 500, 575)
    cfit.cd()


    pad1  = TPad("pad1", "pad1", 0, 0.3, 1.0, 1.0)
    pad1.SetBottomMargin(0)
    pad1.Draw()
    pad1.cd()

    hdata.SetStats(0)
    hdata.SetMaximum(ymax)
    hdata.Draw('ep')
    hs.Draw('histsame')
    hdata.Draw('epsame')

    lg.Draw()
    scribe.write('#chi^{2}/NDF = %5.1f / %d = %5.2f\n' % \
                     (chisq, ndf, chisq/ndf))

    xbins = int(h[0].GetNbinsX())
    width = h[0].GetXaxis().GetBinWidth(1)
    xmin  = int(h[0].GetXaxis().GetBinLowEdge(1))
    xmax  = int(h[0].GetXaxis().GetBinLowEdge(xbins)+width)
    scribe.write('#font[12]{m}_{4#font[12]{l}} #in [%d, %d] GeV' % (xmin,xmax))
    
    CMS_lumi.CMS_lumi(cfit, iPeriod, iPos)                
    cfit.SaveAs('.png')
    cfit.Update()
    gSystem.ProcessEvents()


    # plot lower pad (within current canvas)    
    cfit.cd()
    pad2  = TPad("pad2", "pad2", 0, 0.0, 1, 0.3)
    pad2.SetTopMargin(0.05)
    pad2.SetBottomMargin(0.28)
    pad2.SetGridy()
    pad2.Draw()

    pad2.cd()
    hdata.SetStats(0)
    hdata.GetXaxis().SetLabelSize(0.12)
    hdata.GetXaxis().SetTitleSize(0.12)

    hdata.GetYaxis().SetLabelSize(0.12)
    hdata.GetYaxis().SetTitleSize(0.12)    
    hdata.SetNdivisions(505, 'Y')
    
    hratio = hdata.Clone("ratio")
    hratio.Divide(ht)
    hratio.SetMinimum(0)
    hratio.SetMaximum(3)
    hratio.Draw('ep')
    x = array('d'); x.append(xmin); x.append(xmax)
    y = array('d'); y.append(1); y.append(1)
    hline = TGraph(2, x, y)
    hline.SetLineColor(kRed+1)
    hline.SetLineWidth(3)
    hline.Draw('lsame')
    cfit.Update()
    gSystem.ProcessEvents()
    cfit.SaveAs('.png')
    sleep(5)
#------------------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "\n\t\tciao!\n"
