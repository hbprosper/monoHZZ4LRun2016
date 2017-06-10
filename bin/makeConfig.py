#!/usr/bin/env python
#-----------------------------------------------------------------------------
# File:        makeConfig.py
# Description: make the configuration file for use with computeLimits.py
#              Example usage:
#              writeConfig.py signalfilename hname [variatefile=None] [size=200]
#
# Created:     06-Jun-2017 HBP Bari
#-----------------------------------------------------------------------------
import os, sys, re
from string import *
from time import ctime, sleep
from math import *
from ROOT import *
from histutil import nameonly
#-----------------------------------------------------------------------------
def getYield(filename, hname):
    f = TFile(filename)
    if not f.IsOpen():
        sys.exit("** can't open %s" % filename)
    h = f.Get(hname)
    if not h:
        sys.exit("** can't get signal histogram %s" % hname)
    nbins = h.GetNbinsX()
    count = [0]*nbins
    error = [0]*nbins
    for ii in xrange(nbins):
        count[ii] = h.GetBinContent(ii+1)
        error[ii] = h.GetBinError(ii+1)
    f.Close()
    return (count, error)

def createConfigFile(datafilename, sigfilename, bkgfilename, hname,
                     gvfilename=None, ntrials=100):

    data, edata = getYield(datafilename, hname)
    ndata = sum(data)
    nbins = len(data)

    if gvfilename:
        gvariates = map(atof, open(gvfilename).readlines()) 
        nsample   = min(len(gvariates), ntrials)
    else:
        gvariates = [1.0]
        nsample   = 1
    
    os.system('mkdir -p configs')
    cfgfilename = 'configs/%s_%s_%4.4d.cfg' % \
      (nameonly(sigfilename), hname, nsample)
    print '-> config file: %s' % cfgfilename
    
    cfg = open(cfgfilename, 'w')

    record = '#' + '-'*78
    cfg.write('%s\n' % record)

    record = '# file:    %s' % cfgfilename
    cfg.write('%s\n' % record)
    
    record = '# created: %s' % ctime()
    cfg.write('%s\n' % record)

    record = '#' + '-'*78
    cfg.write('%s\n' % record)  

    # get counts and uncertainty in counts
    sig, dsig = getYield(sigfilename, hname)
    bkg, dbkg = getYield(bkgfilename, hname)
    nsig = sum(sig); esig = sqrt(sum(map(lambda x: x*x, dsig)))
    nbkg = sum(bkg); ebkg = sqrt(sum(map(lambda x: x*x, dbkg)))
    
    record = '#nbins:\t%9d'  % nbins
    cfg.write('%s\n' % record)
    
    record = '#data:\t%9d'  % ndata
    cfg.write('%s\n' % record)

    record = '#sig:\t%9.2e' % nsig
    cfg.write('%s\n' % record)
    
    record = '#esig:\t%9.2e' % esig
    cfg.write('%s\n' % record)   
    
    record = '#bkg:\t%9.2e' % nbkg
    cfg.write('%s\n' % record)
    
    record = '#ebkg:\t%9.2e' % ebkg
    cfg.write('%s\n' % record)
    
    record = '#' + '-'*78
    cfg.write('%s\n' % record)  

    record = '# number of bins'
    cfg.write('%s\n' % record)
    
    record = '%10d' % nbins
    cfg.write('%s\n' % record)
    
    record = '# observed counts'
    cfg.write('%s\n' % record)

    record = ''
    for ii in xrange(nbins):
        record += ' %9d' % int(data[ii])
    cfg.write('%s\n' % record)
    
    record = '# number of sampled points'
    cfg.write('%s\n' % record)        
    cfg.write('\t%d\n' % nsample)

    x1 = 0.0
    x2 = 0.0
    for jj in xrange(nsample):
        
        s = [0]*nbins; es = [0]*nbins
        b = [0]*nbins; eb = [0]*nbins
        x = gvariates[jj]
        x1 += x
        x2 += x*x
        for ii in xrange(nbins):
            s[ii]  = x * sig[ii];
            es[ii] = x * dsig[ii]
            b[ii]  = x * bkg[ii];
            eb[ii] = x * dbkg[ii]

        nn = jj + 1
        record = '# signal counts\t%d' % nn
        cfg.write('%s\n' % record)
        record = ''
        for ii in xrange(nbins):
            record += ' %9.2e' % s[ii]
        cfg.write('%s\n' % record)
        record = '# signal uncertainties\t%d' % nn
        cfg.write('%s\n' % record)
        record = ''
        for ii in xrange(nbins):
            record += ' %9.2e' % es[ii]
        cfg.write('%s\n' % record)

        record = '# background counts\t%d' % nn
        cfg.write('%s\n' % record)
        record = ''
        for ii in xrange(nbins):
            record += ' %9.2e' % b[ii]
        cfg.write('%s\n' % record)
        record = '# background uncertainties\t%d' % nn
        cfg.write('%s\n' % record)
        record = ''
        for ii in xrange(nbins):
            record += ' %9.2e' % eb[ii]
        cfg.write('%s\n' % record)          
    cfg.close()
    x1 /= nsample
    x2 /= nsample
    x2 = sqrt(x2-x1*x1)

    print "-> gamma(mean): %5.3f\tgamma(stdev): %5.3f" % (x1, x2)
# ---------------------------------------------------------------------------
def main():
    if len(sys.argv) < 3:
        sys.exit('''
    Usage:
        makeConfig.py signalfilename hname [variatefile=None] [size=100]
        ''')
        
    datafilename = 'histos/histos_data.root'        
    sigfilename  = sys.argv[1]
    bkgfilename  = 'histos/histos_SM.root'

    hname = sys.argv[2]
    
    if len(sys.argv) > 3:
        gvfilename = sys.argv[3]
    else:
        gvfilename = None

    if len(sys.argv) > 4:
        size = atoi(sys.argv[4])
    else:
        size = 100
        
    createConfigFile(datafilename, sigfilename, bkgfilename, hname,
                         gvfilename, size)
#-----------------------------------------------------------------------------
try:
    main()    
except KeyboardInterrupt:
    print "ciao!"
    
