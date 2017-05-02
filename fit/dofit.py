#!/usr/bin/env python
#------------------------------------------------------------------------------
#  File: fit.py
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
import CMS_lumi, tdrstyle
#------------------------------------------------------------------------------
def getContents(h):
    c = vector("double")()
    e = vector("double")()
    for i in xrange(h.GetNbinsX()):
        binx = i+1
        c.push_back( h.GetBinContent(binx) )
        e.push_back( h.GetBinError(binx) )
    return (c, e)

def fakeData(hdata, h, nbkg, nsig):
    ndata = int(hdata.Integral())
    # create a fake data set
    hfun = h[0].Clone('hfun')
    hfun.Reset()
    hfun.Add(h[0], h[1], nbkg, nsig)        
    hdata.Reset()
    print 'INTEGRAL: %f' % hdata.Integral()
    for ii in xrange(ndata):
        hdata.Fill(hfun.GetRandom())
#------------------------------------------------------------------------------
def main():

    # Load PoissonGammaFit class
    gSystem.AddDynamicPath('%s/lib' % os.environ['PGAMMAFIT_PATH'])    
    gSystem.Load("libpgammafit")

    if len(sys.argv) > 1:
        fstate = sys.argv[1]
    else:
        fstate = '_all'

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


    # Get distribution of sources and unfold into 1-d vectors, A[j]
    f = []
    h = []
    A = [] # vector<vector<double> > # counts and uncertainties
    t = [] # totals
    for i,(filename,hname,c) in \
      enumerate([('../fig_bkg.root', 'bkg', 225.60),
                 ('../fig_higgs.root', 'higgs',27.0)]):
        f.append(TFile(filename))
        h.append( f[-1].Get('hbnn').Clone(hname) )
        if not h[-1]: sys.exit("** can't find hbnn")
        h[-1].SetNdivisions(505, 'X')
        t.append(c)
        
        # plot
        canvas = TCanvas("fig%s_%s" % (fstate, hname),
                             hname, 10, 10, 500, 500)        
        canvas.cd()
        h[-1].Draw("hist gl")
        canvas.Update()
        canvas.SaveAs('.png')
        gSystem.ProcessEvents()
        sleep(3)
        del canvas
        
        # get counts and associated uncertainties and normalize
        A.append(getContents(h[-1]))


    # get data
        
    # Get histogram of observed counts
    filename = '../fig_data.root'
    f.append(TFile(filename))
    hdata = f[-1].Get('hbnn')
    if not hdata: sys.exit("** can't find hbnn")
    ymax = 60
    hdata.SetMaximum(ymax)
    hdata.SetNdivisions(505, 'X')
            
    canvas = TCanvas("fig%s_data" % fstate, "bnn", 10, 10, 500, 500)        
    canvas.cd()
    hdata.Draw("ep gl")
    canvas.Update()
    canvas.SaveAs('.png')
    gSystem.ProcessEvents()        
    sleep(3)
    del canvas
    
    # Construct a PoissonGamma object
    D, dD = getContents(hdata)
    pgfit = PoissonGammaFit(D)
        
    # Add sources
    for a, da in A:
        pgfit.add(a, da)

    # Find mode of posterior density
    # make some reasonable guesses for fit
    total = sum(D)
    guess = vdouble(2, total/3)
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
    for index, src in enumerate(['bkg', 'higgs']):
        print "%-10s\t%10.1f +/-%- 10.1f" % \
              (src, mode[index], error[index])
        x1 += mode[index]
        x2 += error[index]**2
    x2 = sqrt(x2)
    print '-'*35
    print "%-10s\t%10.1f +/-%- 10.1f" % ('total', x1, x2)

    h[0].SetLineColor(kMagenta+1)
    h[0].SetFillColor(kMagenta+1)
    h[0].Scale(mode[0]/h[0].Integral())
    h[0].SetMaximum(ymax)
    hdata.SetMaximum(ymax)
    
    h[1].SetLineColor(kCyan+1)
    h[1].SetFillColor(kCyan+1)
    h[1].Scale(mode[1]/h[1].Integral())

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
        if theory > 8:
            chisq += (theory - datum)**2/variance
            ndf += 1
            print '%4d\t%10.1f\t%10.0f' % (ndf, theory, datum)
            datum   = 0.0
            theory  = 0.0
            variance= 0.0
    ndf -= 2
    print '\nchisq/NDF = %10.1f/%d = %10.2f\n' % (chisq, ndf, chisq/ndf)
    
    hs = THStack('hs', '')
    hs.SetMaximum(ymax)
    hs.Add(h[0])
    hs.Add(h[1])
    
    lg = mklegend(0.25, 0.65, 0.25, 0.2)
    lg.SetHeader('events 4#mu + 2e2#mu, '\
                     '#font[12]{m}_{4#font[12]{l}} #in [70,170] GeV')
    lg.SetTextSize(0.04)
    lg.AddEntry(hdata, 'data  %4.0f' % hdata.Integral(), 'p')
    lg.AddEntry(h[0],  'bkg   %6.1f #pm %-6.1f (#color[4]{%6.1f})' \
                    % (mode[0], error[0], t[0]), 'l')
    lg.AddEntry(h[1],  'Higgs %6.1f #pm %-6.1f (#color[4]{%6.1f})'  \
                    % (mode[1], error[1], t[1]), 'l')

    scribe = Scribe(0.31, 0.60)
    
    cfit = TCanvas("fig%s_result" % fstate, "", 520, 10, 500, 500)
    cfit.cd()
    gStyle.SetOptStat('')    
    hdata.SetMaximum(ymax)
    hdata.Draw('ep')
    hs.Draw('histsame')
    hdata.Draw('epsame')
    lg.Draw()
    scribe.write('#chi^{2}/NDF = %5.1f/%d = %5.2f\n' % \
                     (chisq, ndf, chisq/ndf))
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
