#!/usr/bin/env python
#------------------------------------------------------------------------------
# File: plotErrorRate.py
# Description: plot AdaBoost error rate
# Created: 31-May-2013 INFN SOS 2013, Salerno, Italy, HBP
#          07-Apr-2017 HBP Adapt for Meena
#------------------------------------------------------------------------------
import os, sys
from ROOT import *
from math import *
from string import *
from time import sleep
from array import array
from histutil import *
#------------------------------------------------------------------------------
def main():
    treename  = 'Analysis'
    #--------------------------------------------------------------------------
    # load BDT (C++ wrapped version)
    gSystem.Load("libmelaBDT.so")
    MVD = melaBDT()
    print "number of trees: %6d" % MVD.size()
    print "summed weights:  %10.3f" % MVD.summedWeights()
    print "variables"
    vs = MVD.variables()
    for ii in xrange(vs.size()):
        print "\t%5d\t%s" % (ii, vs[ii])

    print
    MVD.printTree(1)
    
    print
    print 'variable importance'
    R = MVD.ranking()
    for ii in xrange(R.size()):
        print '%5d\t%10.3f\t%s' % \
          (ii, R[ii].first, R[ii].second)
    
    # load BDT (Python wrapped version)
    filename = 'results/weights/higgszz_BDT.class.C'
    mvd = BDT(filename)

    print
    print 'variable importance'
    R = MVD.ranking()
    ranking = mvd.ranking()
    for ii, (value, name) in enumerate(ranking):
        print '%5d\t%10.3f\t%s' % (ii, value, name)

    #--------------------------------------------------------------------------
    # get data
    #--------------------------------------------------------------------------
    variables = mvd.variables()

    maxrows= 10000
    ntrain = 2000 # number of training events/sample
    ntest  = 8000 # start of testing events/sample
    
    treename= 'HZZ4LeptonsAnalysisReduced'

    # load background
    
    btuple = Ntuple('ntuple_bkg.root', treename)
    print 'reading bkg data...'
    bdata  = []
    vdata  = vector('double')(len(variables))
    count  = 0
    for event in btuple:
        if event.f_pt4l  < 0:   continue
        if event.f_eta4l < -10: continue

        data  = [0]*len(variables)            
        for ii, name in enumerate(variables):
            data[ii] = event.__getattr__(name)
            vdata[ii]= data[ii]
        bdata.append(data)
        if count % 2000 == 0:
            print '%5d\t%10.3f\t%10.3f' % (count, mvd(data), MVD(vdata))
        count += 1
        if count >= maxrows: break

    # load signal
    
    stuple = Ntuple('ntuple_higgs.root', treename)
    print
    print 'reading sig data...'
    sdata = []
    count = 0
    for event in stuple:
        if event.f_pt4l  < 0:   continue
        if event.f_eta4l < -10: continue

        data  = [0]*len(variables)
        for ii, name in enumerate(variables):
            data[ii] = event.__getattr__(name)
            vdata[ii]= data[ii]
        if count % 2000 == 0:
            print '%5d\t%10.3f\t%10.3f' % (count, mvd(data), MVD(vdata))            
        sdata.append(data)
        count += 1
        if count >= maxrows: break
            
    print "maximum number of rows: %d" % maxrows
    
    #--------------------------------------------------------------------------
    setStyle()
    
    xmin = 0
    xmax = min(1000, MVD.size())
    ymin = 99.0
    ymax =-99.0

    print 'number of trees: %d' % xmax
    
    x = array('d')
    ytrain = array('d')
    ytest  = array('d')

    nstep  = xmax/100
    numTrees = range(0, xmax+nstep, nstep)
    numTrees[0] = 1

    # loop over different numbers of trees
    
    for nt in numTrees:
        trainError = 0.0; trainCount = 0
        testError  = 0.0; testCount  = 0

        # test background classification
        for index, data in enumerate(bdata):
            for i in xrange(len(data)): vdata[i] = data[i]
                
            D  = MVD(vdata, nt)
            if index < ntrain:
                trainCount += 1
                if D > 0: trainError += 1.0
            elif index > ntest-1:
                testCount += 1
                if D > 0: testError  += 1.0
                    
        # test signal classification                    
        for index, data in enumerate(sdata):
            for i in xrange(len(data)): vdata[i] = data[i]
                
            D  = MVD(vdata, nt)
            if index < ntrain:
                trainCount += 1
                if D < 0: trainError += 1.0
            elif index > ntest-1:
                testCount += 1                    
                if D < 0: testError  += 1.0
                    
        trainError = float(trainError)/trainCount
        testError  = float(testError)/testCount
        
        if min(trainError, testError) < ymin:
            ymin = 0.95*min(trainError, testError)
        if max(trainError, testError) > ymax:
            ymax = 1.05*max(trainError, testError)            
        
        print "%5d\t%10.3f\t%10.3f" % (nt, trainError, testError)
        x.append(nt)
        ytrain.append(trainError)
        ytest.append(testError)
    #--------------------------------------------------------------------------     
    c1 = TCanvas('fig_errorRate', 'error rate', 10, 10, 500, 500)
    gtrain = mkgraph(x, ytrain, 'number of trees', 'error rate', xmin, xmax,
                      ymin=ymin, ymax=ymax, color=kRed, lwidth=2)

    gtest = mkgraph(x, ytest, 'number of trees', 'error rate', xmin, xmax,
                     ymin=ymin, ymax=ymax, color=kBlue, lwidth=2)

    gtrain.Draw('al')
    gtest.Draw('l same')
    addTitle(' error rate vs number of trees')
    c1.Update()
    gSystem.ProcessEvents()
    c1.SaveAs(".png")
    
    sleep(5)
#------------------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "\nciao"
