#!/usr/bin/env python
# ----------------------------------------------------------------------------
#  File:        makeHists.py
#  Description: mono-H->ZZ->4lepton analysis using reduced ntuples from Bari
#               make summary histograms for further analysis.
#  Created:     15-Oct-2016 HBP    
# ----------------------------------------------------------------------------
import os, sys, re
from string import *
FILES='''
ntuple_SM.root
ntuple_ZpBary_MZp00010_MA00001.root
ntuple_ZpBary_MZp00010_MA00010.root
ntuple_ZpBary_MZp00010_MA00050.root
ntuple_ZpBary_MZp00010_MA00150.root
ntuple_ZpBary_MZp00010_MA00500.root
ntuple_ZpBary_MZp00010_MA01000.root
ntuple_ZpBary_MZp00015_MA00010.root
ntuple_ZpBary_MZp00020_MA00001.root
ntuple_ZpBary_MZp00050_MA00001.root
ntuple_ZpBary_MZp00050_MA00010.root
ntuple_ZpBary_MZp00050_MA00050.root
ntuple_ZpBary_MZp00095_MA00050.root
ntuple_ZpBary_MZp00100_MA00001.root
ntuple_ZpBary_MZp00100_MA00010.root
ntuple_ZpBary_MZp00200_MA00001.root
ntuple_ZpBary_MZp00200_MA00050.root
ntuple_ZpBary_MZp00200_MA00150.root
ntuple_ZpBary_MZp00295_MA00150.root
ntuple_ZpBary_MZp00300_MA00001.root
ntuple_ZpBary_MZp00300_MA00050.root
ntuple_ZpBary_MZp00500_MA00001.root
ntuple_ZpBary_MZp00500_MA00150.root
ntuple_ZpBary_MZp00500_MA00500.root
ntuple_ZpBary_MZp00995_MA00500.root
ntuple_ZpBary_MZp01000_MA00001.root
ntuple_ZpBary_MZp01000_MA00150.root
ntuple_ZpBary_MZp01000_MA01000.root
ntuple_ZpBary_MZp01995_MA01000.root
ntuple_ZpBary_MZp02000_MA00001.root
ntuple_ZpBary_MZp02000_MA00500.root
ntuple_ZpBary_MZp10000_MA00001.root
ntuple_ZpBary_MZp10000_MA00010.root
ntuple_ZpBary_MZp10000_MA00050.root
ntuple_ZpBary_MZp10000_MA00150.root
ntuple_ZpBary_MZp10000_MA00500.root
ntuple_ZpBary_MZp10000_MA01000.root
ntuple_Zprime_MZp00600_MA00300.root
ntuple_Zprime_MZp00800_MA00300.root
ntuple_Zprime_MZp01000_MA00300.root
ntuple_Zprime_MZp01200_MA00300.root
ntuple_Zprime_MZp01400_MA00300.root
ntuple_Zprime_MZp01700_MA00300.root
ntuple_Zprime_MZp02000_MA00300.root
ntuple_Zprime_MZp02500_MA00300.root
ntuple_bkg.root
ntuple_data.root
ntuple_higgs.root
'''
FILENAMES = split(strip(FILES), '\n')
def main():
    for filename in FILENAMES:
        cmd = './makeHists.py %s' % filename
        print cmd
        os.system(cmd)
# -------------------------------------------------------------------------
try:     
    main()
except KeyboardInterrupt:
    print '\nciao!\n'
    
