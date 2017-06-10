#!/usr/bin/env python
# ----------------------------------------------------------------------------
#  File:        makeAllConfigs.py
#  Created:     07-Jun-2017 HBP    
# ----------------------------------------------------------------------------
import os, sys, re
from string import *
from glob import glob
# ----------------------------------------------------------------------------
HNAME = 'SR_met'
GVNAME= 'gvariate_0.30.txt'
SIZE  = 100
# ----------------------------------------------------------------------------
def main():
    filenames = glob('histos/histos_Zp*.root')
    filenames.sort()
    for filename in filenames:
        cmd = 'makeConfig.py %s %s %s %d' % (filename, HNAME, GVNAME, SIZE)
        print cmd
        os.system(cmd)
# ----------------------------------------------------------------------------
try:     
    main()
except KeyboardInterrupt:
    print '\nciao!\n'
