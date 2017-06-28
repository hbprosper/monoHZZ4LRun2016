#!/usr/bin/env python
#-----------------------------------------------------------------------------
# File:        computeLimit.py
#
#              Example usage:
#                 computeLimit.py signal-file
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
getSig= re.compile('Z[a-zA-Z]+')
getMZp= re.compile('(?<=MZp)[0-9]+(?=_)')
getMA = re.compile('(?<=MA)[0-9]+(?=_)')
# ----------------------------------------------------------------------------
def lerror(message):
    sys.exit('** computeLimit.py ** %s' % message)
    
def lwarn(message):
    print '** computeLimit.py ** %s' % message

def getNbins(filename, hname):
    hfile = TFile(filename)
    if not hfile.IsOpen():
        lerror("can't open file %s" % filename)
    h = hfile.Get(hname)
    if h == None:
        lerror("can't find histogram %s" % hname)
    nbins = int(h.GetNbinsX())
    return nbins

def getCount(filename, hname, nbins):
    hfile = TFile(filename)
    if not hfile.IsOpen():
        lerror("can't open file %s" % filename)
    h = hfile.Get(hname)
    if h == None:
        lerror("can't find histogram %s" % hname)
    error = Double()
    count = h.IntegralAndError(1, nbins, error)
    error = float(error)
    return (count, error)
# ----------------------------------------------------------------------------    
def getPlotData(cfgfilename):
    if not os.path.exists(cfgfilename):
        lerror("can't read configuration file %s" % cfgfilename)

    # get first 50 or so records
    records = []
    inp = open(cfgfilename)
    for ii in xrange(50):
        try:
            record = strip(inp.readline())
        except:
            break
        if record == '': continue
        records.append(record)        
    filteredRecords = filter(lambda x: x[0] != '#', records)

    # decode records
    index = 0
    nbins = atoi(filteredRecords[index])
    
    # counts
    data  = None
    sig   = None
    esig  = None
    bkg   = None
    ebkg  = None
    
    # check if root files have been specified
    # format:
    #   numberOfBins
    #   data-histogram-filename         data-histogram-name
    #   numberOfSamples    #   signal-histogram-filename       signal-histogram-name
    #   background-histogram-filename   background-histogram-name

    index += 1
    t = split(filteredRecords[index])
    datfilename = t[0]
    histogramInput = datfilename[-5:] == '.root'
    
    if histogramInput:
        # the histogram name is needed
        try:
            datname = t[1]
        except:
            lerror('no histogram name has been specified on line\n=> %s\n' % \
                      filteredRecords[index])
                      
        nbins = min(nbins, getNbins(datfilename, datname))
        
        # get signal filename
        index += 2 # skip number os samples
        t = split(filteredRecords[index])
        sigfilename = t[0]
        if sigfilename[-5:] != '.root':
            lerror('expected a signal histogram file on line\n=> %s\n' % \
                      filteredRecords[index])

        # get signal histogram
        try:
            signame = t[1]
        except:
            # none specified, assume signal histogram name is
            # same as the data histogram name
            signame = datname
            lwarn('assuming signal histogram name is %s' % signame)

        # get background filename
        index += 1
        t = split(filteredRecords[index])
        bkgfilename = t[0]
        if bkgfilename[-5:] != '.root':
            lerror('expected a background histogram file on line\n=> %s\n' % \
                      filteredRecords[index])

        # get background histogram
        try:
            bkgname = t[1]
        except:
            # none specified, assume background histogram name is
            # same as the data histogram name
            bkgname = datname
            lwarn('assuming background histogram name is %s' % bkgname)

        # okay, now get data we need
        ndata, edata = getCount(datfilename, datname, nbins); ndata = int(ndata)
        sig,   esig  = getCount(sigfilename, signame, nbins)
        bkg,   ebkg  = getCount(bkgfilename, bkgname, nbins)
    else:
        for record in xrange(records):
            t = split(record)
            token = t[0]
            if   token == '#nbins:':
                nbins = atoi(t[1])
            elif token == '#data:':
                ndata = atoi(t[1])
            elif token == '#sig:':
                sig   = atof(t[1])
            elif token == '#esig:':
                esig  = atof(t[1])
            elif token == '#bkg:':
                bkg   = atof(t[1])
            elif token == '#ebkg:':
                ebkg  = atof(t[1])
                break
    if ndata == None:
        lerror("check format of file %s " % cfgfilename)
    plotdata = [nbins, ndata, sig, esig, bkg, ebkg]
    return plotdata
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

    ndata, nsig, esig, nbkg, ebkg, prob, limits = plotdata[1:]
    
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
    h.SetFillColor(kAzure+1)
    h.SetFillStyle(1001)
    h.SetMinimum(0)
    
    for j in xrange(xbins):
        x = xmin + (j+0.5)*xstep
        p = bayes.posterior(x) * xstep
        h.SetBinContent(j+1, p)
        h.SetBinError(j+1, 0)
    ymax = 2 * h.GetMaximum()
    ystep= 0.02
    j = int(ymax / ystep)
    ymax = j * ystep
    h.SetMaximum(ymax)

    h97 = h.Clone('h95_%s' % name)
    h97.SetAxisRange(limits[0], limits[-1])
    h97.SetFillColor(kGreen+1)
    h97.SetFillStyle(1001)

    h68 = h.Clone('h68_%s' % name)
    h68.SetAxisRange(limits[1], limits[-2])
    h68.SetFillColor(kYellow)
    h68.SetFillStyle(1001)    

    ypos = bayes.posterior(limit)
    x = array('d');  y = array('d')
    x.append(limit); x.append(limit)
    y.append(0); y.append(ypos*xstep)
    glimit = TGraph(2, x, y)
    glimit.SetLineWidth(3)
    glimit.SetLineColor(kRed)
    
    cname = 'results/%s' % name
    c = TCanvas(cname, cname, 10, 10, 500, 500)
    c.cd()
    h.Draw('c')
    h97.Draw('csame')
    h68.Draw('csame')
    glimit.Draw('lsame')
    
    scribe = Scribe(0.34, 0.88)
    signame = getSig.findall(name)
    if len(signame) > 0:
        signame = signame[0]
        if signame == 'ZpBary':
            signame = "Z'_{baryonic}"
        else:
            signame = "Z'"
    else:
        signame = ''
            
    MZp = getMZp.findall(name)
    if len(MZp) > 0:
        MZp = "m_{Z'}(%4d)" % atoi(MZp[0])
    else:
        MZp = ''
        
    MA = getMA.findall(name)
    if len(MA) > 0:
        MA = 'm_{A}(%4d) (GeV)' % atoi(MA[0])
    else:
        MA = ''
    title = '%s %s %s' % (signame, MZp, MA)
    
    scribe.write(title)
    offset = 0.04
    scribe.write("#font[62]{yields}")
    indent = 0.02
    scribe.write("data:    %5.0f"  % ndata, indent)
    scribe.write("bkg:       %5.1f #pm %-5.1f" % (nbkg, ebkg),   indent)
    scribe.write("signal:    %5.1e #pm %-5.1e" % (nsig, esig),   indent)
    scribe.write("#hat{#mu}: %8.2f #pm %-8.2f" % (muhat, muerr), indent)
    
    scribe.write("#font[62]{observed limit} (%4.1f%s CL)" % (100*CL, '%'),
                     offset + indent)
    obslimit = strip("%10.2f" % limit)
    scribe.write("#mu  < %s" % obslimit, offset + 2*indent)
    scribe.write("#font[62]{expected limit} (%4.1f%s CL)" % (100*CL, '%'),
                     offset + 3*indent)

    lowlimit = strip("%10.2f" % limits[0])
    medlimit = strip("%10.2f" % limits[2])
    hihlimit = strip("%10.2f" % limits[-1])
    
    scribe.write("med[#mu] < %s" % medlimit, offset + 4*indent)
    scribe.write("2#sigma (%s, %s)" % (lowlimit, hihlimit),
                     offset + 7*indent)

    CMS_lumi.CMS_lumi(c, iPeriod, iPos)
    c.Update()
    c.SaveAs('.png')
    gSystem.ProcessEvents()
    sleep(1)
# ---------------------------------------------------------------------------
def computeLimit(cfgfilename, mumin=MUMIN, mumax=MUMAX):

    plotdata = getPlotData(cfgfilename)
    ndata, nsig, esig, nbkg, ebkg = plotdata[1:]
    
    print '''
%s
    data:        %8d
    signal:      %15.6f\t+/- %15.6f
    background:  %11.2f     \t+/- %11.2f
''' % tuple([cfgfilename]+plotdata[1:])

    os.system('mkdir -p results')
    name = nameonly(cfgfilename)
    resultfilename = 'results/%s.txt' % name

    print '-> results will be written to file: %s' % resultfilename
    out = open(resultfilename, 'w')

    mass = getMZp.findall(cfgfilename)
    if len(mass) > 0:
        mass = atof(mass[0])
    else:
        mass = 1000
    print "\n\tmass(Zprime) = %10.0f GeV\n" % mass
    if nsig < 1.e-3:
        sys.exit('\n\t** the predicted signal %e events '\
                     'is absurdly small, so ciao!\n' % nsig)

    y = max(5*mass, min(2.e5, 3 * abs(ndata - nbkg)/nsig))
    MUMAX = y
    
    # --------------------------------------        
    # create model
    # --------------------------------------
    print "-"*60
    print "config file %s" % cfgfilename        
    model = MultiPoissonGamma(cfgfilename)    
    data  = model.counts()

    mumin = MUMIN
    mumax = MUMAX

    record = 'support(guess):\t%9.3f\t%9.3f' % (mumin, mumax)    
    print record

    # --------------------------------------
    # compute Bayes limit
    # --------------------------------------

    # sample size for expected limit calculation
    size = 100
        
    swatch = TStopwatch()
    swatch.Start()

    bayes = Bayes(model, data, mumin, mumax)
    support = bayes.support()
    mumin, mumax = support.first, support.second
    record = 'support:\t%9.3f\t%9.3f' % (mumin, mumax)
    print record
    out.write('%s\n' % record)
    
    blimit = bayes.percentile(CL)
    print
    record = 'limit(Bayes):\t%9.3f time: %9.3fs' % (blimit, swatch.RealTime())
    print record, '\tcomputing expected limits...'
    out.write('%s\n' % record)
    
    swatch   = TStopwatch()
    swatch.Start()    
    explimits= ExpectedLimits(bayes, size)
    prob     = explimits.prob()
    limits   = explimits(0)
    record   = '%9s\t%9s time: %9.3fs' % ('prob', 'limit', swatch.RealTime())
    print record
    out.write('%s\n' % record)
    for i, q in enumerate(limits):
        record = '%9.3f\t%9.3f' % (prob[i], q)
        print record
        out.write('%s\n' % record)

    # plot posterior density
    plotdata.append(prob)
    plotdata.append(limits)
    bayes.setData(data)
    plotPosterior(nameonly(cfgfilename), bayes, blimit, plotdata)
    
    # --------------------------------------
    # compute Wald limit
    # --------------------------------------
    swatch = TStopwatch()
    swatch.Start()
    wald  = Wald(model, data, mumin, mumax)
    wlimit= wald.percentile(CL)

    print
    record= 'limit(Wald):\t%9.3f time: %9.3fs' % (wlimit, swatch.RealTime())
    print record, '\tcomputing expected limits...'
    out.write('%s\n' % record)

    swatch   = TStopwatch()
    swatch.Start()

    explimits= ExpectedLimits(wald, size)
    prob     = explimits.prob()
    limits   = explimits(0)
    record   = '%9s\t%9s time: %9.3fs' % ('prob', 'limit', swatch.RealTime())
    print record
    out.write('%s\n' % record)
    for i, q in enumerate(limits):
        record = '%9.3f\t%9.3f' % (prob[i], q)
        print record
        out.write('%s\n' % record)
    out.close()
    sleep(5)
# ---------------------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        sys.exit('''
    Usage:
        computeLimit.py configfilename
        ''')
    cfgfilename  = sys.argv[1]

    # --------------------------------------
    # load limit codes
    # --------------------------------------
    gSystem.AddDynamicPath("$LIMITS_PATH/lib")
    gSystem.Load('liblimits')

    computeLimit(cfgfilename)
#-----------------------------------------------------------------------------
try:
    main()    
except KeyboardInterrupt:
    print "ciao!"
    
