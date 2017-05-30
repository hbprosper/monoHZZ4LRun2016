#!/usr/bin/env python
# ----------------------------------------------------------------------------
#  File:        plotSignals.py
#  Description: mono-H->ZZ->4lepton analysis using reduced ntuples from Bari
#               plot histograms created with makeHists.py
#  Created:     25-Oct-2016 HBP    
# ----------------------------------------------------------------------------
import os, sys, re
from ROOT import *
from string import *
from math import *
from time import sleep
import CMS_lumi, tdrstyle
# ---------------------------------------------------------------------------

PREFIX = 'Zprime'
FILES  = '''
  187.23	fig_Zprime_MZp00600_MA00300.root
  296.35	fig_Zprime_MZp00800_MA00300.root
  390.11	fig_Zprime_MZp01000_MA00300.root
  480.69	fig_Zprime_MZp01200_MA00300.root
  573.08	fig_Zprime_MZp01400_MA00300.root
  709.83	fig_Zprime_MZp01700_MA00300.root
  763.39	fig_Zprime_MZp02500_MA00300.root
  813.28	fig_Zprime_MZp02000_MA00300.root
'''

PREFIX = 'ZpBary'
FILES  = '''
4.7987	fig_ZpBary_MZp00500_MA00150.root
2.1852	fig_ZpBary_MZp00020_MA00001.root
1.8340	fig_ZpBary_MZp00100_MA00001.root
1.7909	fig_ZpBary_MZp00050_MA00010.root
1.7860	fig_ZpBary_MZp00050_MA00001.root
1.7648	fig_ZpBary_MZp00100_MA00010.root
1.6179	fig_ZpBary_MZp00010_MA00001.root
1.5363	fig_ZpBary_MZp00200_MA00001.root
1.4342	fig_ZpBary_MZp00300_MA00001.root
1.2838	fig_ZpBary_MZp00200_MA00050.root
1.2260	fig_ZpBary_MZp00300_MA00050.root
0.7663	fig_ZpBary_MZp00500_MA00001.root
0.1599	fig_ZpBary_MZp01000_MA00001.root
0.1557	fig_ZpBary_MZp01000_MA00150.root
0.1082	fig_ZpBary_MZp00095_MA00050.root
0.0952	fig_ZpBary_MZp00295_MA00150.root
0.0224	fig_ZpBary_MZp00015_MA00010.root
0.0110	fig_ZpBary_MZp02000_MA00001.root
0.0106	fig_ZpBary_MZp02000_MA00500.root
0.0088	fig_ZpBary_MZp00995_MA00500.root
0.0066	fig_ZpBary_MZp00010_MA00010.root
0.0042	fig_ZpBary_MZp00050_MA00050.root
0.0023	fig_ZpBary_MZp00200_MA00150.root
0.0006	fig_ZpBary_MZp01995_MA01000.root
0.0002	fig_ZpBary_MZp00010_MA00050.root
0.0000	fig_ZpBary_MZp10000_MA01000.root
0.0000	fig_ZpBary_MZp10000_MA00500.root
0.0000	fig_ZpBary_MZp10000_MA00150.root
0.0000	fig_ZpBary_MZp10000_MA00050.root
0.0000	fig_ZpBary_MZp10000_MA00010.root
0.0000	fig_ZpBary_MZp10000_MA00001.root
0.0000	fig_ZpBary_MZp01000_MA01000.root
0.0000	fig_ZpBary_MZp00500_MA00500.root
0.0000	fig_ZpBary_MZp00010_MA01000.root
0.0000	fig_ZpBary_MZp00010_MA00500.root
0.0000	fig_ZpBary_MZp00010_MA00150.root
'''



FILES = replace(FILES, 'fig_', 'histos/histos_')
FILES = map(lambda x: split(x)[-1], split(strip(FILES), '\n'))
getmass = re.compile('(?<=MZp)[0-9]+(?=_)')
# ---------------------------------------------------------------------------
def main():

    # ---------------------------------------
    # set up some standard graphics style
    # ---------------------------------------
    tdrstyle.setTDRStyle()
    gStyle.SetPadRightMargin(0.12)
    #change the CMS_lumi variables (see CMS_lumi.py)
    iPeriod = 4
    iPos    = 0
    CMS_lumi.relPosX = 0.12
    CMS_lumi.lumi_13TeV = "30 fb^{-1}"
    CMS_lumi.writeExtraText = 1
    CMS_lumi.extraText = "Simulation"

    tfile = []
    hbnn  = []
    hmet  = []
    hpt4l = []
    recmet = []
    recpt4l= []
    for filename in FILES:
        mass = atof(getmass.findall(filename)[0])
        print mass
        f = TFile(filename); 
        if not f.IsOpen(): sys.exit("can't open %s" % filename)
        # get BNN histogram
        hbnn.append(f.Get('hbnn').Clone('hbnn_%4.4d' % mass))
        # get signal region (SR) missing-ET (MET)
        hmet.append(f.Get('hpfmets').Clone('hmet_%4.4d' % mass))
        hpt4l.append(f.Get('hpt4ls').Clone('hpt4l_%4.4d' % mass))
        meanmet  = hmet[-1].GetMean()
        meanpt4l = hpt4l[-1].GetMean()
        tfile.append(f)
        record = '%8.2f\t%s\n' % (meanpt4l, filename)
        recpt4l.append(record)
        record = '%8.2f\t%s\n' % (meanmet, filename)
        recmet.append(record)
    recmet.sort()
    recpt4l.sort()
    open('%s_met.txt' %   PREFIX, 'w').writelines(recmet)
    open('%s_pt4l.txt' %  PREFIX, 'w').writelines(recpt4l)
     
    colorbase = 40
    plotname = 'fig_%s_met' % PREFIX
    cmet = TCanvas(plotname, plotname, 10, 10, 500, 500)
    cmet.cd()
    hmet[0].SetFillColor(colorbase)
    hmet[0].SetFillStyle(3001)
    hmet[0].Draw('hist')
    for i, h in enumerate(hmet[1:]):
        h.SetFillColor(colorbase+1+i)
        h.SetFillStyle(3001)        
        h.Draw('histsame')
    CMS_lumi.CMS_lumi(cmet, iPeriod, iPos)            
    cmet.Update()
    gSystem.ProcessEvents()
    cmet.SaveAs('.png')


    plotname = 'fig_%s_pt4l' % PREFIX
    cpt4l = TCanvas(plotname, plotname, 520, 10, 500, 500)
    cpt4l.cd()
    hpt4l[0].SetFillColor(colorbase)
    hpt4l[0].SetFillStyle(3001)
    hpt4l[0].Draw('hist')
    for i, h in enumerate(hpt4l[1:]):
        h.SetFillColor(colorbase+1+i)
        h.SetFillStyle(3001)        
        h.Draw('histsame')
    CMS_lumi.CMS_lumi(cpt4l, iPeriod, iPos)            
    cpt4l.Update()
    gSystem.ProcessEvents()
    cpt4l.SaveAs('.png')


    plotname = 'fig_%s_bnn' % PREFIX
    cbnn = TCanvas(plotname, plotname, 520, 510, 500, 500)
    cbnn.cd()
    hbnn[0].SetFillColor(colorbase)
    hbnn[0].SetFillStyle(3001)
    hbnn[0].Draw('hist')
    for i, h in enumerate(hbnn[1:]):
        h.SetFillColor(colorbase+1+i)
        h.SetFillStyle(3001)        
        h.Draw('histsame')
    CMS_lumi.CMS_lumi(cbnn, iPeriod, iPos)            
    cbnn.Update()
    gSystem.ProcessEvents()
    cbnn.SaveAs('.png')
        
    sleep(10)
# -------------------------------------------------------------------------
try:     
    main()
except KeyboardInterrupt:
    print '\nciao!\n'
