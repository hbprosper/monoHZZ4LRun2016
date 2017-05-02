#!/usr/bin/env python
# ---------------------------------------------------------------------
#  File:        write.py
#  Description: write out training data
#  Created:     28-Apr-2017 Harrison B. Prosper
# ---------------------------------------------------------------------
import os, sys, re
# ---------------------------------------------------------------------
BNNNAME = 'm4lmelapt4l'
def main():

    # unweight and mix
    fields = ['f_mass4l\n', 'f_D_bkg_kin\n', 'f_pt4l\n']
    open('vars.txt', 'w').writelines(fields)

    # unweight and mix
    cmd = '''
    unweight.py bkg_weighted.txt         bkg.dat         5000
    unweight.py ZpBary_weighted.txt      ZpBary.txt      2500
    unweight.py Zprime1_weighted.txt     Zprime1.txt     2500
    unweight.py Zprime2_weighted.txt     Zprime2.txt     2500

    ./cat.py  ZpBary.txt Zprime1.txt Zprime2.txt sig.dat
    mixsigbkg.py -v vars.txt %(bnn)s
    mktrain.py -H10 %(bnn)s
''' % {'bnn': BNNNAME}
    print cmd
    os.system(cmd)

main()

    
