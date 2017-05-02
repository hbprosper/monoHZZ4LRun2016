#!/usr/bin/env python
#------------------------------------------------------------------
# File: write3D.py
# Description: write result of 3D discriminant to a root file
# Created: 02-07-2017 HBP
#------------------------------------------------------------------
import os, sys
from math import *
from hzz4lutil import *
from ROOT import *
from time import sleep
from glob import glob
import CMS_lumi, tdrstyle
#------------------------------------------------------------------
FIELDS = ['f_weight',
          'f_mass4l',
          'f_D_bkg_kin',
          'f_pfmet']
OFIELDS = FIELDS + ['f_D']
#------------------------------------------------------------------
def write(filename, mlp, outfilename,
              treename='HZZ4LeptonsAnalysisReduced'):
    ntuple = NtupleReader(filename, FIELDS)
    
    rfile = TFile(outfilename, 'recreate')
    tree  = TTree(treename, treename)
    cmd  = 'struct Row {'
    for field in OFIELDS:
        cmd += 'double %s;' % field
    cmd += '};'
    gROOT.ProcessLine(cmd)
    from ROOT import Row
    row = Row()
    for field in OFIELDS:
        tree.Branch(field, AddressOf(row, field), '%s/D' % field)

    cmd = ''
    for field in OFIELDS:
        cmd += 'row.%s = %s;' % (field, field)
        
    total1 = 0.0
    total2 = 0.0
    for ii in xrange(ntuple.size()):
        ntuple.read(ii)
        f_weight   = ntuple('f_weight')        
        f_mass4l   = ntuple('f_mass4l')
        f_D_bkg_kin= ntuple('f_D_bkg_kin')
        f_pfmet    = ntuple('f_pfmet')
        f_D = mlp(f_mass4l, f_D_bkg_kin, f_pfmet)

        total1 += f_weight
        total2 += f_weight*f_weight
        
        exec(cmd)
        tree.Fill()
        
        if ii % 10000 == 0:
            print '.',; sys.stdout.flush()
            
    rfile.Write()
    rfile.Close()

    total2 = sqrt(total2)
    print
    print '=> number of events: %10.2f %10.2f' % (total1, total2)       
#------------------------------------------------------------------
def main():
      
    MLPname     = 'm4lmelamet'
    bkgfilename = ['ntuple_bkg.root', 'ntuple_higgs.root']
    
    # compile code
    code = open('%s.cpp' % MLPname).read()
    gROOT.ProcessLine(code)
    mlp  = eval(MLPname)
    write(bkgfilename, mlp, 'bkg.root')
#----------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "\nciao!"
