#!/usr/bin/env python
#------------------------------------------------------------------------------
#  File: fitbkg.py
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
PATH  = '70-270-BG'
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
        
    sources = ('%s/fig_%sbkg.root'   % (PATH, decor), 'bkg',   kMagenta+1)
    
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
    # get source histogram
    # ---------------------------------------    
    filename,hname,color = sources
    fsrc = TFile(filename)
    if not fsrc.IsOpen():
        sys.exit("** can't open file %s" % fsrc)
    hsrc = fsrc.Get(HNAME).Clone(hname)
    if not hsrc: sys.exit("** can't find histogram")
    
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
    ii    = int(ymax / 10)
    ymax  = (ii+1)*10
        
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
    sleep(1)
    del canvas

    # ---------------------------------------
    # plot source
    # ---------------------------------------    
    cname = "fig_%s%s%s" % (decor, hname, postfix)
    canvas = TCanvas(cname, cname, 10, 10, 500, 500)        
    canvas.cd()
    hsrc.SetNdivisions(505, 'X')
    hsrc.Draw("hist gl")
    canvas.Update()
    canvas.SaveAs('.png')
    gSystem.ProcessEvents()
    sleep(1)
    del canvas

    # get counts
    datum = 0.0
    bkg   = 0.0

    fb  = []    
    D   = []
    for ii in xrange(xbins):
        bkg   += hsrc.GetBinContent(ii+1)
        datum += hdata.GetBinContent(ii+1)
        
        if bkg > 10:
            fb.append(bkg)
            D.append(datum)

            print '%4d\t%10.2f\t%10.0f' % (len(D), bkg, datum)
            bkg   = 0.0
            datum = 0.0            
    
    # ---------------------------------------
    # fit
    # ---------------------------------------
    t = []
    bguess = sum(fb)
    fb = map(lambda x: x/bguess, fb)
    
    def Func(npar, grad, fval, xval, flag):
        fval[0] = 0.0
        B = xval[0]
        for i in xrange(len(D)):
            theory = B * fb[i]
            x = D[i] - theory
            fval[0] += x*x / theory

    minuit = TMinuit(1)
    minuit.SetPrintLevel(1)
    minuit.SetFCN(Func)
    minuit.SetErrorDef(1)
    
    # Find mode of posterior density
    # make some reasonable guesses for fit
    total  = sum(D)
    status  = Long()

    bstep  = bguess/1000
    bmin   = 0.0
    bmax   = 2*total
    minuit.mnparm(0, "B", bguess, bstep, bmin, bmax, status)
    if status != 0: 
        sys.exit("** mnparam status code: %d" % status)
    
    args = array('d')
    args.append(MAXITER)
    args.append(TOLERANCE)
    minuit.mnexcm(METHOD, args, 2, status)
    if status != 0:
        sys.exit("** mnexcm %s failed" % METHOD)

    # Print results
    print "-"*80
    print "total observed count: %d" % total    
    print "%-10s\t%10s" %  ('source', "    estimated count")
    value  = Double()
    dvalue = Double()    
    minuit.GetParameter(0, value, dvalue)
    mode = value
    error= dvalue
    print "%-10s\t%10.1f +/-%- 10.1f" % \
      ("", mode, error)

    color = sources[-1]
    hsrc.SetLineColor(color+2)
    hsrc.SetFillColor(color)
    hsrc.Scale(mode / hsrc.Integral())
    hsrc.SetMaximum(ymax)
    
    # compute GOF measure
    chisq = 0.0
    for i in xrange(len(D)):
        theory =  mode * fb[i]
        x = D[i] - theory
        chisq += x * x / theory
    ndf = len(D) - 1
    
    print '\nchisq/NDF = %10.1f/%d = %10.2f\n' % (chisq, ndf, chisq/ndf)
    
    lg = mklegend(0.35, 0.72, 0.25, 0.2)
    lg.SetHeader('events(%s)' % FINALSTATES[fstate])
                     
    lg.SetTextSize(0.04)
    lg.AddEntry(hdata, 'data  %4.0f' % hdata.Integral(), 'p')
    fname, src, color = sources
    src = capitalize(src)
    lg.AddEntry(hsrc,  '%-5s   %6.1f #pm %-6.1f (#color[4]{%6.1f})' \
                    % (src, mode, error, bguess), 'f')

    scribe = Scribe(0.43, 0.68)

    cname = "fig_%sresult%s" % (decor, postfix)
    cfit = TCanvas(cname, cname, 520, 10, 500, 500)
    cfit.cd()
    gStyle.SetOptStat('')

    hdata.SetMaximum(ymax)
    hdata.Draw('ep')
    hsrc.Draw('histsame')
    hdata.Draw('epsame')

    lg.Draw()
    scribe.write('#chi^{2}/NDF = %5.1f / %d = %5.2f\n' % \
                     (chisq, ndf, chisq/ndf))
    scribe.write('#font[12]{m}_{4#font[12]{l}} #in [%d, %d] GeV' % (xmin,xmax))
    
    CMS_lumi.CMS_lumi(cfit, iPeriod, iPos)                
    cfit.SaveAs('.png')
    cfit.Update()
    gSystem.ProcessEvents()

    sleep(5)
#------------------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "\n\t\tciao!\n"
