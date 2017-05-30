#!/usr/bin/env python
#-----------------------------------------------------------------------------
# File:        computeLimits.py
#
#              Example usage:
#                 computeLimits.py signal-files
#
# Created:     17-Jun-2015 HBP Les Houches
# Updated:     28-May-2017 HBP for real mono-Higgs analysis
#-----------------------------------------------------------------------------
import os, sys, re
from string import *
from time import ctime, sleep
from math import *
from ROOT import *
from histutil import *
import CMS_lumi, tdrstyle
#-----------------------------------------------------------------------------
MUMIN = 0.0
MUMAX = 1000.0
CL    =  0.95
getmass = re.compile('(?<=MZp)[0-9]+(?=_)')
# ---------------------------------------------------------------------------
def getYield(filename, hname):
    f = TFile(filename)
    if not f.IsOpen():
        sys.exit("** can't open %s" % filename)
    h = f.Get(hname)
    if not h:
        sys.exit("** can't get signal histogram %s" % hname)
    nbins = h.GetNbinsX()
    error = Double()
    count = h.IntegralAndError(1, nbins, error)
    f.Close()
    return (nbins, count, error)

def createConfigFile(datafilename, filenames, name, hname):

    nbins, ndata, edata = getYield(datafilename, hname)

    os.system('mkdir -p results')
    cfgfilename = 'results/%s.cfg' % name
    print '-> config file: %s' % cfgfilename
    
    cfg = open(cfgfilename, 'w')

    record = '#' + '-'*78
    cfg.write('%s\n' % record)
    
    record = '# %s' % ctime()
    cfg.write('%s\n' % record)

    record = '#' + '-'*78
    cfg.write('%s\n' % record)  
    
    record = '# number of bins'
    cfg.write('%s\n' % record)
    cfg.write('\t%s\n' % nbins)

    record = '# observed counts'
    cfg.write('%s\n' % record)
    cfg.write('\t%s\t%s\n' % (datafilename, hname))
    
    record = '# number of sampled points'
    cfg.write('%s\n' % record)
    cfg.write('\t%d\n' % len(filenames))
    
    for ii, (sigfilename, bkgfilename) in enumerate(filenames):
        jj = ii+1
        nbins, nsig, esig = getYield(sigfilename, hname)
        nbins, nbkg, ebkg = getYield(bkgfilename, hname)
        
        record = '#%d\tsignal = %9.2e (%9.2e)\tbackground = %9.2e (%9.2e)' % \
          (jj, nsig, esig, nbkg, ebkg)
        cfg.write('%s\n' % record)
        cfg.write('\t%s\t%s\n' % (sigfilename, hname))
        cfg.write('\t%s\t%s\n' % (bkgfilename, hname))
    cfg.close()
    return (cfgfilename, [nbins, ndata, nsig, esig, nbkg, ebkg])
# ---------------------------------------------------------------------------
def plotPosterior(name, bayes, limit, plotdata):
    
    # ---------------------------------------
    # set up some standard graphics style
    # ---------------------------------------
    tdrstyle.setTDRStyle()
    gStyle.SetPadRightMargin(0.12)
    #change the CMS_lumi variables (see CMS_lumi.py)
    iPeriod = 4
    iPos    = 0
    CMS_lumi.relPosX = 0.12
    CMS_lumi.lumi_13TeV = "36 fb^{-1}"
    CMS_lumi.writeExtraText = 1
    CMS_lumi.extraText = "Preliminary"
    
    support = bayes.support()
    mumin, mumax = support.first, support.second

    result = bayes.MAP()
    muhat, muerr = result.first, result.second
    
    # create histogram
    xbins = 200
    xmin  = mumin
    xmax  = mumax
    j     = int(xmax/3)
    xmax  = float(j + 1)*3
    xstep = (xmax-xmin)/xbins

    h = TH1F('h_%s' % name, '', xbins, xmin, xmax)
    h.GetXaxis().SetNdivisions(505)
    h.GetYaxis().SetNdivisions(505)
    h.GetXaxis().SetTitle('#mu')
    h.GetYaxis().SetTitle('p(#mu | D)')
    h.SetLineWidth(2)
    for j in xrange(xbins):
        x = xmin + (j+0.5)*xstep
        p = bayes.posterior(x) * xstep
        h.SetBinContent(j+1, p)
        h.SetBinError(j+1, 0)
    ymax = 1.4 * h.GetMaximum()
    if   ymax > 0.2:
        ystep = 0.03
    elif ymax > 0.02:
        ystep = 0.003
    elif ymax > 0.002:
        ystep = 0.0003
    
    j = int(ymax / ystep)
    ymax = j * ystep
    h.SetMaximum(ymax)

    hclone = h.Clone('hclone_%s' % name)
    hclone.SetAxisRange(xmin, limit)
    hclone.SetFillColor(kAzure+1)
    hclone.SetFillStyle(3002)

    
    hclone2 = h.Clone('hclone2_%s' % name)
    hclone2.SetAxisRange(limit, xmax)
    hclone2.SetFillColor(kRed+1)
    hclone2.SetFillStyle(3002)
    
    #print "\t** LCDF =%8.3f" % hclone.Integral()    
    #print "\t** RCDF =%8.3f" % hclone2.Integral()
    #print "\t** TOTAL=%8.3f" % h.Integral()
    
    arrow = TArrow()
    arrow.SetFillColor(30)
    arrow.SetFillStyle(3001)
    
    cname = 'results/%s' % name
    c = TCanvas(cname, cname, 10, 10, 500, 500)
    c.cd()
    h.Draw('c')
    hclone.Draw('csame')
    hclone2.Draw('csame')
    arrow.DrawArrow(limit, ymax/3, limit, ymax/8, 0.04)
    
    scribe = Scribe(0.33, 0.85)
    scribe.write(name)
    if len(plotdata) == 6:
        ndata, nsig, esig, nbkg, ebkg = plotdata[1:]
        scribe.write("yields", 0.05)
        scribe.write("data:    %5.0f"  % ndata, 0.07)
        scribe.write("bkg:       %5.1f #pm %-5.1f"   % (nbkg, ebkg),  0.07)
        scribe.write("signal:    %5.1e #pm %-5.1e"  % (nsig, esig),  0.07)
    scribe.write("#hat{#mu} = %8.2f #pm %-8.2f" % (muhat, muerr))        
    scribe.write("#mu < %8.2f @ %4.1f%s CL" % (limit, 100*CL, '%'))

    
    CMS_lumi.CMS_lumi(c, iPeriod, iPos)
    c.Update()
    c.SaveAs('.png')
    gSystem.ProcessEvents()
    sleep(1)
# ---------------------------------------------------------------------------
def computeLimit(cfgfilename, plotdata=[], mumin=MUMIN, mumax=MUMAX):

    resultfilename = replace(cfgfilename, '.cfg', '.txt')
    print '-> result file: %s' % resultfilename
    out = open(resultfilename, 'w')

    mass = getmass.findall(cfgfilename)
    if len(mass) > 0:
        mass = atof(mass[0])
    else:
        mass = 10000;
    MUMAX = 8 * mass
    
    # --------------------------------------        
    # create model
    # --------------------------------------
    print "-"*60
    print "config file %s" % cfgfilename        
    model = MultiPoissonGamma(cfgfilename)    
    data  = model.counts()

    # --------------------------------------
    # compute Bayes limit
    # --------------------------------------
    swatch = TStopwatch()
    swatch.Start()

    mumin = MUMIN
    mumax = MUMAX

    record = 'initial support:\t%9.3f\t%9.3f' % (mumin, mumax)
    print record
    
    bayes = Bayes(model, data, mumin, mumax)
    support = bayes.support()
    mumin, mumax = support.first, support.second
    record = 'support:\t%9.3f\t%9.3f' % (mumin, mumax)
    print record
    out.write('%s\n' % record)
    
    blimit = bayes.percentile(CL)
    record = 'limit(Bayes):\t%9.3f\t%9.3fs' % (blimit, swatch.RealTime())
    print record
    out.write('%s\n' % record)

    if len(plotdata) > 0:
        plotPosterior(nameonly(cfgfilename), bayes, blimit, plotdata)

    print '\tcomputing expected limits...'
    
    swatch   = TStopwatch()
    swatch.Start()    
    explimits= ExpectedLimits(bayes)
    prob     = explimits.prob()
    limits   = explimits(0)
    record   = '%9s\t%9s\t%9.3f' % ('prob', 'limit', swatch.RealTime())
    print record
    out.write('%s\n' % record)
    for i, q in enumerate(limits):
        record = '%9.3f\t%9.3f' % (prob[i], q)
        print record
        
    # --------------------------------------
    # compute Wald limit
    # --------------------------------------
    swatch = TStopwatch()
    swatch.Start()
    wald  = Wald(model, data, mumin, mumax)
    wlimit= wald.percentile(CL)

    record= 'limit(Wald):  %9.3f\t%9.3fs' % (wlimit, swatch.RealTime())
    print record
    out.write('%s\n' % record)

    print '\tcomputing expected limits...'
    
    swatch   = TStopwatch()
    swatch.Start()    
    explimits= ExpectedLimits(wald)
    prob     = explimits.prob()
    limits   = explimits(0)
    record   = '%9s\t%9s\t%9.3fs' % ('prob', 'limit', swatch.RealTime())
    print record
    out.write('%s\n' % record)
    for i, q in enumerate(limits):
        record = '%9.3f\t%9.3f' % (prob[i], q)
        print record
    out.close()
# ---------------------------------------------------------------------------
def main():

    signalfiles = 'ZpBary.list'
    
    sigfilenames   = map(lambda y: y[-1],
                          map(split,
                                  filter(lambda x: strip(x) != "",
                                             open(signalfiles).readlines())))
        
    # --------------------------------------
    # load limit codes
    # --------------------------------------
    gSystem.AddDynamicPath("$LIMITS_PATH/lib")
    gSystem.Load('liblimits')

    datafilename = 'histos/histos_data.root'
    bkgfilename  = 'histos/histos_SM.root'
    hname = 'hmet'
    plot  = True
    
    for ii, sigfilename in enumerate(sigfilenames):
        name = replace(nameonly(sigfilename), 'histos_', '')
        filenames = (sigfilename, bkgfilename)
        
        cfgfilename, plotdata = createConfigFile(datafilename,
                                                     [filenames], name, hname)
        
        computeLimit(cfgfilename, plotdata)
#-----------------------------------------------------------------------------
try:
    main()    
except KeyboardInterrupt:
    print "ciao!"
    
