#!/usr/bin/env python
# ----------------------------------------------------------------------------
#  File:        countEvents.py
#  Description: count events
#  Created:     26-Oct-2016 HBP    
# ----------------------------------------------------------------------------
import os, sys, re
from ROOT import *
from string import *
from math import *
from time import sleep, ctime
from array import array
import tdrstyle
# ----------------------------------------------------------------------------
# fields to be read from ntuples 
FIELDS = ['f_weight',
          'f_sample',
          'f_finalstate',
          'f_mass4l']
    
SKIP   = 50000
k2E2MU = 1
k4E    = 2
k4MU   = 3
FINALSTATE  = {'2e2mu': k2E2MU,
               '4e':    k4E,
               '4mu':   k4MU,
               'all':  -1}
getname = re.compile('(?<=ntuple\_)[a-zA-Z0-9]+')
def getName(record):
    t = getname.findall(record)
    if len(t) == 1:
        return t[0]
    else:
        return None
# ----------------------------------------------------------------------------
def nameonly(s):
    import posixpath
    return posixpath.splitext(posixpath.split(s)[1])[0]
# ----------------------------------------------------------------------------
def main():

    if len(sys.argv) > 1:
        filenames = sys.argv[1:]
    else:
        sys.exit('''
    Usage:
        countEvents.py ntuple-file1 ntuple-file2...
        ''')
    
    name = getName(filenames[0])
    outname = 'count_%s.txt' % name
    
    # ---------------------------------------
    # Loop over events
    # ---------------------------------------
    # create struct to cache data from ntuple
    struct = 'struct Event {'
    for field in FIELDS:
        struct += 'float %s;' % field
    struct += '};'
    # compile struct and 
    gROOT.ProcessLine(struct)
    from ROOT import Event
    event = Event()
    
    # ---------------------------------------
    # now give the addresses of the fields
    # within the struct to ROOT
    # ---------------------------------------
    records = []
    for filename in filenames:
        rfile = TFile(filename)
        tree  = rfile.Get("HZZ4LeptonsAnalysisReduced")
        for field in FIELDS:
            tree.SetBranchAddress(field, AddressOf(event, field))

        nevents = tree.GetEntries()            
        t1 = 0.0
        t2 = 0.0
        for index in xrange(nevents):
            # load variables into memory
            tree.GetEntry(index)
            w = event.f_weight
            t1 += w
            t2 += w*w
        if t1 < 1.e-4: continue
        t2 = sqrt(t2)
        record = '%10.4f %10.4f\t%s' % (t1, t2, nameonly(filename))
        print record
        records.append('%s\n' % record)
    records.sort()
    records.reverse()

    print 'output: %s' % outname
    open(outname, 'w').writelines(records)
# -------------------------------------------------------------------------
try:     
    main()
except KeyboardInterrupt:
    print '\nciao!\n'
