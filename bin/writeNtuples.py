#!/usr/bin/env python
# ----------------------------------------------------------------------------
#  File:        writeNtuples.py
#  Description: read filelist, shuffle events, flag events with weights >
#               4*sigma away from the mean, and write events to an ntuple
#  Created:     22-Oct-2016 HBP    
# ----------------------------------------------------------------------------
import os, sys, re
from ROOT import *
from string import *
from math import *
from time import sleep, ctime
from random import shuffle
import CMS_lumi, tdrstyle
# ----------------------------------------------------------------------------
NSIGMA = 4
SKIP   = 50000
stripit1 = re.compile('.*ntuple_')
stripit2 = re.compile('.*ntuple_[2-4].*_')
#-----------------------------------------------------------------------------
def nameonly(s):
    import posixpath
    return posixpath.splitext(posixpath.split(s)[1])[0]

def openNtupleFile(filenames, treename):
    # ---------------------------------------        
    # create a chain of root files
    # ---------------------------------------
    filenames = map(strip, filenames)
    chain = TChain(treename)
    for index, filename in enumerate(filenames):
        #print filename
        chain.Add(filename)

    # ---------------------------------------
    # set up which variables to read from ntuples
    # ---------------------------------------
    tree   = chain
    # create struct to cache data from ntuple

    # get names of variables from root file
    branches  = tree.GetListOfBranches()
    # get number of variables
    try:
        nbranches = branches.GetEntries()
    except:
        sys.exit("** ====>  problem accessing branches\n")

    fields = []
    typenames = []
    struct = 'struct Event{'
    for i in xrange(nbranches):
        leaves = branches[i].GetListOfLeaves()
        if leaves:
            leaf = leaves[0]
        else:
            sys.exit("** can't get name of leaf")
        
        typename = leaf.GetTypeName()
        typenames.append(typename)
        field    = leaf.GetName()
        fields.append(field)
        struct += '%s %s;' % (typename, field)
        
    typename = 'Int_t'
    field    = 'f_sample'
    fields.append(field);  typenames.append(typename)        
    struct += '%s %s;' % (typename, field)
    
    field    = 'f_outlier'
    fields.append(field);  typenames.append(typename)            
    struct += '%s %s;' % (typename, field)

    struct += '};'
    
    # compile struct 
    gROOT.ProcessLine(struct)
    from ROOT import Event
    event = Event()

    # ---------------------------------------
    # now give the addresses of the fields
    # within the struct to ROOT so that ROOT
    # knows where to put the data read from
    # the ntuple.
    # ---------------------------------------
    print "variables:"
    for field in fields[:-2]:
        #print "\t%s" % field
        tree.SetBranchAddress(field, AddressOf(event, field))
    
    return (chain, event, fields, typenames)
# ----------------------------------------------------------------------------
def main():
    if len(sys.argv) > 1:
        filelist = sys.argv[1]
    else:
        sys.exit('''
    Usage:
        writeNtuples.py filelist
        ''')
        
    # get list of files
    filenames = map(lambda x: split(x)[-1], open(filelist).readlines())
    outfilename = 'store/%s.root' % \
      replace(nameonly(filelist), 'filelist_', 'ntuple_')

    wgtfilename = 'store/%s.txt' % \
      replace(nameonly(filelist), 'filelist_', 'weight_')

    treename = "HZZ4LeptonsAnalysisReduced"
        
    # ---------------------------------------
    # Loop over events
    # ---------------------------------------
    chain, event, fields, typenames = openNtupleFile(filenames, treename)

    nevents = chain.GetEntries()
    print
    print '='*80    
    print 'number of entries: %d' % nevents
    
    print 'computing mean weight and standard deviation of events'    
    w1 = 0.0
    w2 = 0.0
    currentTreeNumber=-1
    jindex = 0
    kindex = 0
    for index in xrange(nevents):
        # load data into memory
        localindex = chain.LoadTree(index)
        if chain.GetTreeNumber() != currentTreeNumber:
            tree = chain.GetTree()
            currentTreeNumber = chain.GetTreeNumber()            
        tree.GetEntry(localindex)
        w = event.f_weight
        w1 += w
        w2 += w*w
        if index % SKIP == 0:
            print '%10d' % index

    w1 /= nevents
    w2 /= nevents
    w2  = sqrt(abs(w2 - w1*w1))
    meanw = w1
    stdvw = w2
    print "<weight>: %10.2e +/- %-5.2e" % (meanw, stdvw)
 
    # ---------------------------------------    
    # open output root file
    # ---------------------------------------
    tfile = TFile(outfilename, "recreate")
    tfile.SetCompressionLevel(2)
    ttree = TTree(treename, "%s created: %s" % (treename, ctime()))

    # create branches
    for ii, field in enumerate(fields):
        ttree.Branch(field, AddressOf(event, field), "%s/%s" % \
                     (field, typenames[ii][0]))

    # ---------------------------------------
    # loop over events
    # ---------------------------------------
    t1 = 0.0
    t2 = 0.0
          
    w1 = 0.0
    w2 = 0.0
    neventsw = 0
    currentTreeNumber=-1
    for index in xrange(nevents):
        # load data into memory
        localindex = chain.LoadTree(index)
        if chain.GetTreeNumber() != currentTreeNumber:
            tree = chain.GetTree()
            currentTreeNumber = chain.GetTreeNumber()
            print "%3d %s" % (currentTreeNumber, chain.GetFile().GetName())
            
        tree.GetEntry(localindex)
        
        w = event.f_weight
        if w > meanw + NSIGMA * stdvw:
            outlier = 1
        else:
            outlier = 0

        # fill output tree
        event.f_sample  = currentTreeNumber
        event.f_outlier = outlier
        
        tfile.cd()
        ttree.Fill()

        t1 += w
        t2 += w*w
        if not outlier:
            w1 += w
            w2 += w*w
            neventsw += 1
            
        if index % SKIP == 0:
            print '%10d' % index
            
    tfile.Write("", TObject.kOverwrite)

    w2 = sqrt(w2)
    t2 = sqrt(t2)

    out = open(wgtfilename, 'w')
    out.write("mean(weight): %10.2e\n" % meanw)
    out.write("stdv(weight): %10.2e\n\n" % stdvw)
    out.write("number of events (unweighted):    %8d\n" % nevents)   
    out.write("number of events (with outliers):    %10.4f +/- %-10.4f\n\n" % \
              (t1, t2))
    out.write("number of events (unweighted):    %8d\n" % neventsw)
    out.write("number of events (without outliers): %10.4f +/- %-10.4f\n" % \
              (w1, w2))
    out.close()
    print '='*80
    print "\tdone!\n"
# -------------------------------------------------------------------------
try:     
    main()
except KeyboardInterrupt:
    print '\nciao!\n'
