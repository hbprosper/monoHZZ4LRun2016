# ----------------------------------------------------------------------------
#  File:        hzz4lutil.py
#  Description: Some simple utilities
#  Created:     26-Oct-2016 HBP    
# ----------------------------------------------------------------------------
import os, sys, re
from ROOT import *
from string import *
from math import *
from time import sleep, ctime
from array import array
# ----------------------------------------------------------------------------
def nameonly(s):
    import posixpath
    return posixpath.splitext(posixpath.split(s)[1])[0]
# ----------------------------------------------------------------------------
# Note: "self" is like the "this" pointer in C++
NtupleReaderCount = 1
class NtupleReader:
    def __init__(self,
                 filenames,
                 variables,
                 treename="HZZ4LeptonsAnalysisReduced"):
        # ---------------------------------------        
        # create a chain of root files
        # ---------------------------------------
        global NtupleReaderCount
        NtupleReaderCount += 1
        chain = TChain(treename)
        if type(filenames) == type([]):
            for filename in filenames:
                print filename
                chain.Add(filename)
        else:
            chain.Add(filenames)

        # ---------------------------------------
        # set up which variables to read from ntuples
        # ---------------------------------------
        tree   = chain
        # create struct to cache data from ntuple
        struct = 'struct Event%d{' % NtupleReaderCount
        fields = []
        for field in variables:
            branch = tree.GetBranch(field)
            if branch:
                leaf = branch.GetLeaf(field)
                if leaf:
                    typename = leaf.GetTypeName()
                    struct += '%s %s;' % (typename, field)
                    fields.append(field)
                else:
                    print "** leaf not found %s" % field
            else:
                print "** branch not found %s" % field
        struct += '};'
        # compile struct and 
        gROOT.ProcessLine(struct)
        exec('from ROOT import Event%s as Event' % NtupleReaderCount)
        event = Event()

        # ---------------------------------------
        # now give the addresses of the fields
        # within the struct to ROOT so that ROOT
        # knows where to put the data read from
        # the ntuple.
        # ---------------------------------------
        print "variables:"
        for field in fields:
            print "\t%s" % field
            tree.SetBranchAddress(field, AddressOf(event, field))

        # cache some variables
        self.event = event
        self.chain = chain
        self.tree  = chain.GetTree()
        self.variables = variables
        self.currentTreeNumber = -1
        
    def __del__(self):
        gROOT.Reset()
        pass

    def __call__(self, field):
        return self.event.__getattribute__(field)
    
    def size(self):
        return self.chain.GetEntries()
    
    def read(self, index):
        chain = self.chain
        # load data into memory
        localindex = chain.LoadTree(index)
        if chain.GetTreeNumber() != self.currentTreeNumber:
            self.currentTreeNumber = chain.GetTreeNumber()
        tree = chain.GetTree()
        tree.GetEntry(localindex)        
# ----------------------------------------------------------------------------
