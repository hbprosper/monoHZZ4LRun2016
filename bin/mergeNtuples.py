#!/usr/bin/env python
# ----------------------------------------------------------------------------
#  File:        mergeNtuples.py
#  Description: write out ZZ4L variables (with events shuffled)
#  Created: 21-Oct-2016 HBP
# ----------------------------------------------------------------------------
import os, sys, re
from ROOT import *
from string import *
from math import *
from random import shuffle
from time import ctime
# ----------------------------------------------------------------------------
stripit= re.compile('_2e2mu|_4e|_4mu')
FSTATE = {'_2e2mu': 1, '_4e': 2, '_4mu': 3}
# ----------------------------------------------------------------------------
def nameonly(s):
    import posixpath
    return posixpath.splitext(posixpath.split(s)[1])[0]
# ----------------------------------------------------------------------------
def makeTree(event,
             filename,
             typenames, 
             varnames, 
             records,
             treename='HZZ4LeptonsAnalysisReduced',
             complevel=2):
    
    print "=> writing to file %s" % filename
    
    # open output root file
    tfile = TFile(filename, "recreate")
    tfile.SetCompressionLevel(complevel)
    ttree = TTree(treename, "%s created: %s" % (treename, ctime()))
    
    # ---------------------------------------------------
    # create branches
    # ---------------------------------------------------
    branch = []
    for ii, varname in enumerate(varnames):
        branch.append( ttree.Branch(varname,
                                    AddressOf(event, varname),
                                    "%s/%s" % (varname, typenames[ii][0]) ))

    # fill tree
    for index, record in enumerate(records):
        if index % 10000 == 0: print '\t',index
        for ii, x in enumerate(record):
            # note use of __setattr__(name, value) to set
            # attributes of struct
            event.__setattr__(varnames[ii], x)
        tfile.cd()
        ttree.Fill()
    tfile.Write("", TObject.kOverwrite)
# ----------------------------------------------------------------------------
def main():
    if len(sys.argv) > 1:
        filenames = sys.argv[1:]
    else:
        sys.exit('''
    Usage:
        python mergeNtuples.py root-files

    Example:
        python mergeNtuples.py store/ntuple_*_data.root
        ''')    

    # get branch names

    rfile = TFile(filenames[0])
    if not rfile.IsOpen():
        sys.exit("** can't find %s" % filenames[0])
    # ----------------------------------------------------------
    # get names of variables from root file
    # ----------------------------------------------------------
    treename= "HZZ4LeptonsAnalysisReduced"        
    tree = rfile.Get(treename)
    branches  = tree.GetListOfBranches()
    # get number of variables
    try:
        nbranches = branches.GetEntries()
    except:
        sys.exit("** ====>  problem accessing branches\n")
    fields = []
    typenames = []
    for i in xrange(nbranches):
        leaves = branches[i].GetListOfLeaves()
        if leaves:
            leaf = leaves[0]
        else:
            sys.exit("** can't get name of leaf")
        typename = leaf.GetTypeName()
        field    = leaf.GetName()
        typenames.append(typename)
        fields.append(field)
    rfile.Close()
    typenames.append('Int_t')        
    fields.append('f_finalstate')
    # ----------------------------------------------------------
    # do some PyRoot magic to read from tree
    # ----------------------------------------------------------
    struct = 'struct Event{'
    for i in xrange(len(fields)):
        typename = typenames[i]
        field    = fields[i]
        struct += '%s %s;' % (typename, field)
    struct += '};'
    gROOT.ProcessLine(struct)
    from ROOT import Event
    event = Event()
    event.f_genmet = -1

    # ----------------------------------------------------------    
    # loop over files
    # ----------------------------------------------------------    
    records = []

    t1 = 0.0
    t2 = 0.0        
    w1 = 0.0
    w2 = 0.0
    nt = 0
    nw = 0

    isData = find(filenames[0], 'data') > 0
    
    for jj, filename in enumerate(filenames):
        print "%3d\t%s" % (jj, filename)

        key = stripit.findall(filename)[0]
        ii = FSTATE[key]
        
        # ii = 1: 2e2mu
        #      2: 4e
        #      3: 4mu
        event.f_finalstate = ii
        
        # open root file
        ntuple = TFile(filename)
        if not ntuple.IsOpen():
            sys.exit("can't open file %s" % filename)
            
        # get tree
        tree = ntuple.Get(treename)
        if not tree:
            sys.exit("can't get tree %s" % treename)

        # last variable is not in input files
        for field in fields[:-1]:
            if field == 'f_genmet' and isData: continue
            tree.SetBranchAddress(field, AddressOf(event, field))

        # now loop over events in current file
        nevents = tree.GetEntries()
        nt += nevents
        for index in xrange(nevents):
            tree.GetEntry(index)
            w = event.f_weight

            t1 += w
            t2 += w*w            
            if not event.f_outlier:
                nw += 1
                w1 += w
                w2 += w*w
            else:
                print '\toutlier: %d' % index

            # add to list of records to be shuffled
            record = [0]*len(fields)
            for ii, field in enumerate(fields):
                record[ii] = event.__getattribute__(field)
            records.append(record)
            
            if index % 50000 == 0:
                print "\t%d" % index

    t2 = sqrt(t2)            
    w2 = sqrt(w2)
    print '%10d %10.3f %-10.3f' % (nt, t1, t2)    
    print '%10d %10.3f %-10.3f' % (nw, w1, w2)

    shuffle(records)
    
    # -----
    name = nameonly(filenames[0])
    name = stripit.sub('', name)

    # if filename[1] includes higgs, change name to 
    filename = "%s.root" % name
    makeTree(event,
             filename,
             typenames,
             fields,
             records)
# -------------------------------------------------------------------------
try:     
    main()
except KeyboardInterrupt:
    print '\nciao!\n'
