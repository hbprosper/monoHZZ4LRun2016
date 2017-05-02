#!/usr/bin/env python
#----------------------------------------------------------------------
# File: train.py
# Description: example of classification with TMVA
# Created: 01-Jun-2013 INFN SOS 2013, Vietri sul Mare, Italy, HBP
#          01-Mar-2017 DESY 2017 Statistics School, Hamburg, Germany
#                      Now compatible with root_v6.08.06
#          01-May-2017 adapt to monoHZZ4L 2016 analysis HBP
#----------------------------------------------------------------------
import os, sys, re
from ROOT import TFile, TMVA, TCut
#----------------------------------------------------------------------
def getTree(filename, treename='HZZ4LeptonsAnalysisReduced'):
    hfile = TFile(filename)
    if not hfile.IsOpen():
        sys.exit("** can't open file %s" % filename)

    tree = hfile.Get(treename)
    if tree == None:
        sys.exit("** can't find tree %s" % treename)
    return (hfile, tree)
#----------------------------------------------------------------------
# simple routine to concatenate options
def formatOptions(options):
    from string import joinfields, strip, split
    options = joinfields(map(strip, split(strip(options), '\n')), ':')
    return options
#----------------------------------------------------------------------
def main():
    print "\n", "="*80
    print "\tmonoHZZ4L - classification with TMVA"
    print "="*80

    # summary root file
    summaryFilename = 'TMVA.root'

    # results directory
    resultsDir = 'results'
    os.system('mkdir -p %s' % resultsDir)
    
    #------------------------------------------------------------------
    # get signal file and associated Root tree
    weightname  = "f_weight"  # name of event weight variable
    sigFilename = '../../ntuple_higgs.root'
    sigFile, sigTree = getTree(sigFilename)

    # get background file and associated Root tree
    bkgFilename = '../../ntuple_SM.root'    
    bkgFile, bkgTree = getTree(bkgFilename)

    #------------------------------------------------------------------
    # create a factory for booking machine learning methods
    #------------------------------------------------------------------
    outputFile = TFile("TMVA.root", "recreate")
    options = '''
    !V
    Color
    !Silent
    DrawProgressBar
    AnalysisType=Classification
    Transformations=I;D
    '''
    factory = TMVA.Factory("HZZ4L", outputFile, formatOptions(options))

    #------------------------------------------------------------------    
    # set up data set for training and testing
    #------------------------------------------------------------------
    dataLoader  = TMVA.DataLoader(resultsDir)
    
    # define all MELA variables here
    dataLoader.AddVariable("f_mass4l", 'D')
    dataLoader.AddVariable("f_D_bkg_kin", 'D')

    # define from which trees data are to be taken
    # and the global weights and event-by-event weights
    # to be assigned to the training data
    sigWeight = 1.0
    dataLoader.AddSignalTree(sigTree, sigWeight)
    dataLoader.SetSignalWeightExpression("f_weight")
    
    bkgWeight = 1.0
    dataLoader.AddBackgroundTree(bkgTree, bkgWeight)
    dataLoader.SetBackgroundWeightExpression("f_weight")
    
    # you can apply cuts, if needed
    cut = TCut('!f_outlier')
    
    options = '''
    SplitMode=Block
    NormMode=EqualNumEvents
    nTrain_Signal=5000
    nTest_Signal=5000
    nTrain_Background=5000
    nTest_Background=5000
    !V 
    '''
    dataLoader.PrepareTrainingAndTestTree(cut, # signal cut
                                          cut, # background cut
                                          formatOptions(options))

    #------------------------------------------------------------------    
    # ok, almost done, define machine learning methods to be run
    #------------------------------------------------------------------
        
    options = '''
    !H
    !V
    BoostType=AdaBoost
    NTrees=5000
    nEventsMin=100
    nCuts=50
    '''
    factory.BookMethod( dataLoader,
                        TMVA.Types.kBDT,
                        "BDT",
                        formatOptions(options))


    options = '''
    !H
    !V
    NCycles=400
    VarTransform=N
    HiddenLayers=10
    TrainingMethod=BFGS
    '''
    factory.BookMethod( dataLoader,
                        TMVA.Types.kMLP,
                        "MLP",
                        formatOptions(options))    

    #------------------------------------------------------------------
    # ok, let's go!
    #------------------------------------------------------------------    
    factory.TrainAllMethods()  
    factory.TestAllMethods()
    factory.EvaluateAllMethods()
    
    outputFile.Close()
#----------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "\nciao"
