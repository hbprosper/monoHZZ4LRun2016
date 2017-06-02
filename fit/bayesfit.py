#!/usr/bin/env python
#------------------------------------------------------------------------------
#  File: bayesfit.py
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
from string import capitalize, find
from array import array
import CMS_lumi, tdrstyle
#------------------------------------------------------------------------------
HNAME = 'CR_m4l'
PATH  = '../histos'

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

def getm4lrange(fdata):
    # get m4l range
    if HNAME[:2] == 'SR':
        hname = 'SR_m4l'
    else:
        hname = 'CR_m4l'        
    hm4l = fdata.Get(hname).Clone('hm4ltmp')
    if not hm4l: sys.exit("** can't find %s" % hname)
        
    xbins = int(hm4l.GetNbinsX())
    width = hm4l.GetXaxis().GetBinWidth(1)
    xmin  = int(hm4l.GetXaxis().GetBinLowEdge(1))
    xmax  = int(hm4l.GetXaxis().GetBinLowEdge(xbins)+width)
    
    return (xbins, xmin, xmax, width)

def drawLine(hr, Y=1):
    from array import array
    xbins = int(hr.GetNbinsX())
    width = hr.GetXaxis().GetBinWidth(1)
    xmin  = int(hr.GetXaxis().GetBinLowEdge(1))
    xmax  = int(hr.GetXaxis().GetBinLowEdge(xbins)+width)    
    x = array('d'); x.append(xmin); x.append(xmax)
    y = array('d'); y.append(Y); y.append(Y)
    hline = TGraph(2, x, y)
    hline.SetLineColor(kRed+1)
    hline.SetLineWidth(2)
    hline.Draw('lsame')
    SetOwnership(hline, 0)
    
def GOF(hdata, hsrcs, cut=8):
    nbins = int(hdata.GetNbinsX())
    npars = len(hsrcs)
    chisq = 0.0
    datum = 0.0
    theory= 0.0    
    ndf   = 0
    ldatum  = -1.0    
    ltheory = -1.0
    for ii in xrange(nbins):
        bn = ii+1
        datum += hdata.GetBinContent(bn)        
        for h in hsrcs:
            theory += h.GetBinContent(bn)

        if theory > cut:
            ndf    += 1
            chisq  += (datum - theory)**2 / datum
            ltheory = theory
            ldatum  = datum
            datum   = 0.0
            theory  = 0.0
            
    if theory > 0:
        theory += ltheory
        datum  += ldatum
        chisq  -= (ldatum-ltheory)**2 / ldatum
        chisq  += (datum - theory)**2 / datum
            
    ndf -= npars
    ht = hsrcs[0].Clone('theory')
    if len(hsrcs) > 1: ht.Add(hsrcs[1])            
    KS = hdata.KolmogorovTest(ht)            
    return (chisq, ndf, KS, ht)
#------------------------------------------------------------------------------
FINALSTATES = {'2e2mu': '2#font[12]{e}2#font[12]{#mu}',
               '4e'   : '4#font[12]{e}',
               '4mu'  : '4#font[12]{#mu}',
               ''     : '2#font[12]{e}2#font[12]{#mu}+4#font[12]{e}+'\
                        '4#font[12]{#mu}'}
#------------------------------------------------------------------------------
def main():

    # Load PoissonGammaFit class
    gSystem.AddDynamicPath('$PGAMMAFIT_PATH/lib')    
    gSystem.Load("libpgammafit")
    
    if len(sys.argv) > 1:
        fstate = sys.argv[1]
    else:
        fstate = ''
    decor = fstate
    if decor != '':
        decor += '_'
        
    sources = [('%s/histos_%sbkg.root'   % (PATH, decor), 'bkg',   kMagenta+1),
               ('%s/histos_%shiggs.root' % (PATH, decor), 'higgs', kAzure+1)]
    
    # ---------------------------------------        
    # get data histogram
    # ---------------------------------------    
    filename = '%s/histos_%sdata.root' % (PATH, decor)
    fdata = TFile(filename)
    if not fdata.IsOpen():
        sys.exit("** can't open file %s" % filename)        
    hdata = fdata.Get(HNAME)
    if not hdata: sys.exit("** can't find histogram")
    hdata.SetMarkerColor(kBlack)
    
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
        if not h[-1]: sys.exit("** can't find %s" % HNAME)
        h[-1].SetFillColor(color)
        h[-1].SetFillStyle(3001)
        
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
    ymax  = 1.5*hdata.GetMaximum()
    ii    = int(ymax / 20)
    ymax  = (ii+1)*20
                
    hdata.SetMaximum(ymax)
    hdata.SetNdivisions(505, 'X')

    xbins, xmin, xmax, width = getm4lrange(fdata)
    
    postfix = "_%s_%3.3d_%3.3d" % (HNAME, xmin, xmax)
    if len(sources) == 1: postfix += "_%s" % sources[0][1]
        
    cname = "fig_%sdata%s" % (decor, postfix)
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

    # get counts
    A = [0]*len(h) # vector<vector<double> > # counts and uncertainties
    t = [0]*len(h) # totals
    for i,(filename,hname,color) in enumerate(sources):
        A[i] = getContents(h[i])
        t[i] = h[i].Integral()
        print '\tcount(%s):\t%8.1f' % (hname, t[i])    
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
    guess = vdouble(len(sources))
    total = sum(D)
    aguess= total / len(sources)
    for i,(filename,hname,color) in enumerate(sources):
        guess[i] = aguess
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

    result= "result_%sdata%s.txt" % (decor, postfix)
    rout = open(result, 'w')
    # Print results
    print "-"*80
    record = "data\t\t     %d" % total
    print record
    rout.write('%s\n' % record)

    record = "%-10s\t%10s" %  ('source', "    estimated count")
    print record
    rout.write('%s\n' % record)
    
    x1 = 0.0
    x2 = 0.0
    for index, (fname, src, color) in enumerate(sources):
        record = "%-10s\t%10.1f +/-%- 10.1f" % \
              (src, mode[index], error[index])
        print record
        rout.write('%s\n' % record)
        x1 += mode[index]
        x2 += error[index]**2
    x2 = sqrt(x2)
    record= '-'*35
    print record
    rout.write('%s\n' % record)
    
    record = "%-10s\t%10.1f +/-%- 10.1f" % ('total', x1, x2)
    print record
    rout.write('%s\n' % record)

    for index, (fname, src, color) in enumerate(sources):    
        h[index].SetLineColor(color+2)
        h[index].SetFillColor(color)
        h[index].Scale(mode[index]/h[index].Integral())
        h[index].SetMaximum(ymax)
        
    hdata.SetMinimum(1.e-3)
    hdata.SetMaximum(ymax)


    # compute GOF measure

    chisq, ndf, KS, ht = GOF(hdata, h)
    print
    rout.write('\n')
    
    record = 'chisq/NDF = %4.1f/%d = %6.2f' % (chisq, ndf, chisq/ndf)
    print record
    rout.write('%s\n' % record)
    
    record = 'KS-prob   = %6.3f' % KS
    print record
    print
    rout.write('%s\n' % record)
    rout.close()
    
    ht.SetMaximum(ymax)
    
    hs = THStack('hs', '')
    hs.Add(h[0])
    if len(sources) > 1: hs.Add(h[1])
    hs.SetMaximum(ymax)

    lg = mklegend(0.35, 0.72, 0.25, 0.2)
    lg.SetHeader('events(%s) %s' % \
                     (FINALSTATES[fstate],
                    '#font[12]{m}_{4#font[12]{l}} #in [%d, %d] GeV' %\
                     (xmin,xmax)))
                     
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

    lg.Draw()
    scribe.write('KS-prob = %6.3f' % KS)
    scribe.write('#chi^{2}/NDF = %5.1f / %d = %5.2f\n' % \
                     (chisq, ndf, chisq/ndf))    
    
    hs.Draw('histsame')
    hdata.Draw('epsame')
    
    CMS_lumi.CMS_lumi(cfit, iPeriod, iPos)                
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
    drawLine(hratio)
    hratio.Draw('epsame')
    
    cfit.Update()
    gSystem.ProcessEvents()
    cfit.SaveAs('.png')
    
    sleep(5)
#------------------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "\n\t\tciao!\n"
