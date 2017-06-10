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
import CMS_lumi, tdrstyle
#------------------------------------------------------------------------------
HNAME = 'hm4l'
PATH  = '70-140'
PATH  = '70-190'
#PATH  = '70-270-BG'
FAKEDATA =  True
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

    # Load PoissonGammaFit class
    gSystem.AddDynamicPath('%s/lib' % os.environ['PGAMMAFIT_PATH'])    
    gSystem.Load("libpgammafit")

    if len(sys.argv) > 1:
        fstate = sys.argv[1]
    else:
        fstate = ''
    decor = fstate
    if decor != '':
        decor += '_'
        
    sources = [('%s/fig_%sbkg.root' % (PATH, decor), 'bkg', kMagenta+1),
               ('%s/fig_%shiggs.root' % (PATH, decor), 'higgs', kAzure+1)]

    # get data histogram
    filename = '%s/fig_%sdata.root' % (PATH, decor)
    fdata = TFile(filename)
    if not fdata.IsOpen():
        sys.exit("** can't open file %s" % filename)        
    hdata = fdata.Get(HNAME)
    if not hdata: sys.exit("** can't find hbnn")
        
    # get source histograms
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
    
    # get counts
    A = [0]*len(h) # vector<vector<double> > # counts and uncertainties
    t = [0]*len(h) # totals
    for i,(filename,hname,color) in enumerate(sources):
        A[i] = getContents(h[i])
        t[i] = h[i].Integral()
        print '\tcount(%s):\t%8.1f' % (hname, t[i])

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
        
    # plot data

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
    sleep(3)
    del canvas
    

    for i,(filename,hname,color) in enumerate(sources):        
        cname = "fig_%s%s%s" % (decor, hname, postfix)
        canvas = TCanvas(cname, cname, 10, 10, 500, 500)        
        canvas.cd()
        h[i].SetNdivisions(505, 'X')
        h[i].Draw("hist gl")
        canvas.Update()
        canvas.SaveAs('.png')
        gSystem.ProcessEvents()
        sleep(3)
        del canvas
 
    # ---------------------------------------                         
    # Construct a PoissonGamma object
    # ---------------------------------------    
    D, dD = getContents(hdata)
    pgfit = PoissonGammaFit(D)
        
    # Add sources
    for a, da in A:
        pgfit.add(a, da)

    # Find mode of posterior density
    # make some reasonable guesses for fit
    total = sum(D)
    guess = vdouble(len(sources), total/len(sources))
    pgfit.execute(guess)

    if not pgfit.good():
      sys.exit('''
        ** :( boo hoo - fit failed!
        ** check histograms. If ok, try better starting guesses for
        ** the source counts in the signal region and/or try rebinning.
        ''')

    # Get mode and width of posterior density, which, because PoissonGammaFit
    # uses a flat prior for the yields, are the same as those of the
    # Poisson/gamma marginal density. 

    mode  = pgfit.mode()
    error = pgfit.width()
    logevidence = pgfit.logEvidence()

    # Print results
    print "-"*80
    print "total observed count: %d" % total    
    print "%-10s\t%10s" %  ('source', "    estimated count")
    x1 = 0.0
    x2 = 0.0
    for index, (fname, src, color) in enumerate(sources):
        print "%-10s\t%10.1f +/-%- 10.1f" % \
              (src, mode[index], error[index])
        x1 += mode[index]
        x2 += error[index]**2
    x2 = sqrt(x2)
    print '-'*35
    print "%-10s\t%10.1f +/-%- 10.1f" % ('total', x1, x2)

    for index, (fname, src, color) in enumerate(sources):    
        h[index].SetLineColor(color+2)
        h[index].SetFillColor(color)
        h[index].Scale(mode[index]/h[index].Integral())
        h[index].SetMaximum(ymax)
    hdata.SetMaximum(ymax)

    
    # compute GOF measure
    nbin  = h[0].GetNbinsX()
    chisq = 0.0
    datum = 0.0
    theory = 0.0
    variance = 0.0
    ndf   = 0
    for ii in xrange(nbin):
        d  = hdata.GetBinContent(ii+1)
        e0 = h[0].GetBinError(ii+1)
        c0 = h[0].GetBinContent(ii+1)
        e0 = h[0].GetBinError(ii+1)
        c1 = h[1].GetBinContent(ii+1)
        e1 = h[1].GetBinError(ii+1)

        datum   += d
        theory  += c0 + c1
        variance+= c0 + c1 + e0**2 + e1**2
        if datum > 8:
            chisq += (theory - datum)**2/variance
            ndf += 1
            print '%4d\t%10.1f\t%10.0f' % (ndf, theory, datum)
            datum   = 0.0
            theory  = 0.0
            variance= 0.0
    ndf -= 2
    print '\nchisq/NDF = %10.1f/%d = %10.2f\n' % (chisq, ndf, chisq/ndf)
    
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
    cfit = TCanvas(cname, cname, 520, 10, 500, 500)
    cfit.cd()
    gStyle.SetOptStat('')

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

    sleep(5)
#------------------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "\n\t\tciao!\n"
