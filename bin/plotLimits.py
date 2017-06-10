#!/usr/bin/env python
#-----------------------------------------------------------------
# File:        plotLimits.py
# Description: plot mono-Higgs limits
# Created:     15-Aug-2014 HBP @ 10,000 meters...this is becoming
#              a habit
#              08-Jun-2017 HBP, Bari, Italy, 61 today and prime!
#-----------------------------------------------------------------
import os,sys,re
import CMS_lumi, tdrstyle
from time import sleep
from histutil import *
from string import *
from math import *
from ROOT import *
#-----------------------------------------------------------------
YMIN  = 1.0e-1
YMAX  = 1.0e+3
POSTFIX = 'SR_met_0100' # postfix at end of results file

getSig= re.compile('Zp[a-zA-Z]+')
def modelName(record):
    t = getSig.findall(record)
    if len(t) > 0:
        name = t[0]
    else:
        name = None
    return name

getMZp= re.compile('(?<=MZp)[0-9]+(?=_)')
def massMZp(record):
    t = getMZp.findall(record)
    if len(t) > 0:
        mass = atoi(t[0])
    else:
        mass = None
    return mass

getMA = re.compile('(?<=MA)[0-9]+')
def massMA(record):
    t = getMA.findall(record)
    if len(t) > 0:
        mass = atoi(t[0])
    else:
        mass = None
    return mass
#-----------------------------------------------------------------
class TexWriter:
    def __init__(self, filename):
        self.out = open(filename, 'w')
    def __del__(self):
        pass
    def close(self):
        self.out.close()
    def __call__(self, record):
        record = replace(record, '\\percent', '\\%')
        self.out.write('%s\n' % record)
#-----------------------------------------------------------------        
def main():
    postfix = POSTFIX
    argv = sys.argv[1:]
    if len(argv) > 0:
        countfile = argv[0]
        if len(argv) > 1:
            postfix = argv[1]
    else:
        sys.exit('''
    Usage:
        plotLimits.py count-file [postfix=SR_met_0100]

    Example:
        plotLimits.py count_ZpBary.txt
        ''')

    # get counts and signals
    signals = map(split, open(countfile).readlines())

    modelname = nameonly(replace(countfile, 'count_', ''))
    if   modelname == 'ZpBary': 
        title = 'Z$^\prime$ baryonic models.'
    elif modelname == 'Zprime': 
        title = 'Z$^\prime$ models.'
    else:
        title = ''
    # ---------------------------------------
    # set up some standard graphics style
    # ---------------------------------------
    tdrstyle.setTDRStyle()
    if modelname == 'Zprime':
        gStyle.SetPadLeftMargin(0.15)
        gStyle.SetPadRightMargin(0.08)
        gStyle.SetPadBottomMargin(0.15)
        xwid = 500
        ywid = 500
        yoff = 1.0
    else:
        gStyle.SetPadLeftMargin(0.08)
        gStyle.SetPadRightMargin(0.04)
        gStyle.SetPadBottomMargin(0.15)
        xwid =1000
        ywid = 500
        yoff = 0.58
        
    iPeriod = 4
    iPos    = 0
    CMS_lumi.relPosX = 0.12
    CMS_lumi.lumi_13TeV = "36 fb^{-1}"
    CMS_lumi.writeExtraText = 1
    CMS_lumi.extraText = "Preliminary"

    # consolidate all limits into a single latex file
    x  = array('d')
    y  = array('d')
    yo = array('d')
    exl= array('d')
    exh= array('d')    
    eyl= array('d')
    eyh= array('d')
    yxc= array('d')
    
    labels = []
    limits = []

    for index, (sig, esig, signal) in enumerate(signals):
        sig  = atof(sig)
        esig = atof(esig)
        filename = 'results/%s_%s.txt' % (replace(signal, 'ntuple', 'histos'),
                                              postfix)
        if not os.path.exists(filename):
            sys.exit("** can't find results file %s" % filename)
            
        records = map(split, open(filename).readlines())
        limit   = atof(records[1][1])
        elimit  = map(lambda x: atof(x[1]), records[3:8])
        name    = modelName(filename)
        MZp     = massMZp(filename)
        MA      = massMA(filename)
        label   = "%6s %4.0f %4.0f" % (name, MZp, MA)
        labels.append(label)

        median = elimit[2]
        yo.append(limit)
        y.append(median)
        exl.append(0)
        exh.append(0)
        eyl.append(median-elimit[0])
        eyh.append(elimit[-1]-median)
        yxc.append(1)

        print name, MZp, MA
        limits.append(tuple([MZp, MA, sig, esig, limit] + elimit))

    # write latex tables
    write = TexWriter('tables/limits_%s.tex' % modelname)            
    write(r"\begin{table}[htbp]")
    write(r"\caption{%s models. "\
              "95\percent CL upper limits on $\mu$.}" % title)
    write(r"\begin{center}")
    write(r"\begin{tabular}{|c|c|c|c|c|c|c|c|c|}")
    write(r"\hline")
    write(r'$m_{\textrm{Z}^\prime}$ (GeV)'\
    ' & $m_A$ (GeV)'\
    ' & Yield'\
    ' & Limit'\
    ' & 2.3\,\percent'\
    ' & 15.8\,\percent'\
    ' & 50.0\,\percent'\
    ' & 84.2\,\percent'\
    ' & 97.7\,\percent')
    write(r"\\")
    write(r"\hline")    
    for index, t in enumerate(limits):
        write(r'%d & %d & $%7.4f \pm %7.4f$'\
                  '& %7.2f & %7.2f & %7.2f & %7.2f & %7.2f & %7.2f' % t)
        write(r"\\")
    write(r"\hline")            
    write(r"\end{tabular}")        
    write(r"\end{center}")
    write(r"\label{tab:limits%s}" % modelname)
    write(r"\end{table}")
    write("")
    write.close()
 
    count = len(signals)
    for ii in xrange(count): x.append(ii+1)

    # make histogram for the labels
    hl = TH1F('hl', '', count+1, 0, count+1)
    hl.GetYaxis().SetTitle('#font[12]{#mu}^{95}')
    hl.SetMinimum(YMIN)
    hl.SetMaximum(YMAX)
    xaxis = hl.GetXaxis()
    xaxis.SetLabelSize(0.045)
    xaxis.SetTitleOffset(1.6)
    for ii in xrange(count):
        xaxis.SetBinLabel(ii+1, labels[ii])
    yaxis = hl.GetYaxis()
    yaxis.SetTitleOffset(yoff)    
    
    go = mkgraph(x, yo, 'signal', '#mu^{95}', 0, count,
                 ymin=YMIN, ymax=YMAX)
    go.SetMarkerSize(1.5)
    go.SetMarkerColor(kBlack)

    gx = mkgraph(x, yxc, 'signal', '#mu^{95}', 0, count,
                 ymin=YMIN, ymax=YMAX)
    gx.SetLineColor(kBlue)    
        
    g1 = TGraphAsymmErrors(count, x, y, exl, exh, eyl, eyh)
    g1.SetMarkerSize(1.2)
    g1.SetMarkerStyle(24)
    g1.SetMarkerColor(kGreen+1)
    g1.SetLineWidth(3)
    g1.SetLineColor(kGreen+1)

    
    filename = 'fig_limits%s' % modelname
    c1 = TCanvas(filename, filename, 10, 10, xwid, ywid)
    c1.cd()
    c1.SetLogy()
    c1.SetGridy()
    hl.Draw()
    g1.Draw('epsame')
    go.Draw('epsame')
    gx.Draw('lsame')
    CMS_lumi.CMS_lumi(c1, iPeriod, iPos)
    c1.Update()
    gSystem.ProcessEvents()
    c1.SaveAs('.pdf')
    c1.SaveAs('.png')
    sleep(2)
    #gApplication.Run()
#----------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print
    print "ciao!"
