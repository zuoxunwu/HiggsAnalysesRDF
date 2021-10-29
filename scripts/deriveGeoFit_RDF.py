import os
import sys
import timeit
import numpy as np
import math

import ROOT
ROOT.ROOT.EnableImplicitMT()

from CMS_style import setTDRStyle


FILE_LOC = "/eos/cms/store/user/xzuo/H2XXNanoPost/2018/v0p0-5-g86fd7f9/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/DY/210921_001323/0000"
#FILE_LOC = "/eos/cms/store/user/xzuo/H2XXNanoPost/2017/v0p0-8-g58bf5e1/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/DY_17_mg/211004_182536/0000"    #2017mg
#FILE_LOC = "/eos/cms/store/user/xzuo/H2XXNanoPost/2017/v0p0-8-g58bf5e1/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/DY_17_amc/211004_182431/0000"  #2017amc
#FILE_LOC = "/eos/cms/store/user/xzuo/H2XXNanoPost/2016/v0p0-9-g71fe22f/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/DY_16a_amc/211005_140301/0000/" #2016a amc
#FILE_LOC = "/eos/cms/store/user/xzuo/H2XXNanoPost/2016/v0p0-9-g71fe22f/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/DY_16b_amc/211005_140427/0000/" #2016b amc  24files
FILES = []
for i in range(1,38):
  FILES.append('tree_%d.root'%i)
print (FILES)
YEAR  = '2018'
TREE  = 'Events'


def findCenterRange(hist, window = 0, VERBOSE = False):
    xmax = 0
    ymax = 0
    # integrate a small window to mitigate fluctuations in fine-binned hists
    if window == 0:
        window = min(1, hist.GetNbinsX() // 40)

    if hist.GetEntries() < 50:
      print ('Looking for FWHM in %s, too few entries (%d). Return X axis range as FWHM.' %(hist.GetName(), hist.GetEntries()))
      return (hist.GetNbinsX()//2, 1, hist.GetNbinsX())

    for i in range(window + 1, hist.GetNbinsX() - window + 1):
      if ymax < hist.Integral(i-window, i+window):
        ymax = hist.Integral(i-window, i+window)
        xmax = i
    if ymax == 0:
      print ('Weird case: no max found in hist. Return X axis range as FWHM')
      return (hist.GetNbinsX()//2, 1, hist.GetNbinsX())

    lo_bin = hist.GetNbinsX()
    hi_bin = 1
    for i in range(window + 1, hist.GetNbinsX() -  window + 1):
      if i < lo_bin and hist.Integral(i-window, i+window) > ymax - 2 * math.sqrt(ymax): lo_bin = i
      if i > hi_bin and hist.Integral(i-window, i+window) > ymax - 2 * math.sqrt(ymax): hi_bin = i

    if VERBOSE: print ("FWHM is %f to %f" %(hist.GetBinCenter(lo_bin), hist.GetBinCenter(hi_bin)))
    return (xmax, lo_bin, hi_bin)



def DrawCanv(out_file, graph):
    setTDRStyle()
    ROOT.gStyle.SetOptFit(0)
    ROOT.gStyle.SetLegendBorderSize(0)
    ROOT.gStyle.SetLegendFont(42)
    ROOT.gStyle.SetLegendTextSize(0.035) 
    ROOT.gStyle.SetErrorX(0.0)

    out_file.cd()

    graph_name = graph.GetName()
    canv = ROOT.TCanvas(graph_name, graph_name, 600, 600)
    canv.SetLeftMargin(0.15)
    canv.SetTopMargin(0.08)
    canv.cd()

    graph.GetXaxis().SetTitle("d0_{BS} * charge (\mu^{}m)")
    graph.GetXaxis().SetTitleSize(0.035)
    graph.GetXaxis().SetTitleOffset(1.2)
    graph.GetXaxis().SetLabelSize(0.03)
    graph.GetXaxis().SetLimits(-120,120)
    graph.GetYaxis().SetTitle("(p_{T}^{Roch} - p_{T}^{gen})/(p_{T}^{gen})^{2}")
    graph.GetYaxis().SetTitleSize(0.035)
    graph.GetYaxis().SetTitleOffset(1.9)
    graph.GetYaxis().SetLabelSize(0.03)

    graph.SetMaximum(0.005)
    graph.SetMinimum(-0.003)
    graph.SetMarkerStyle(8)
    graph.SetMarkerSize(0.8)

    eta_min = graph_name.split('_')[1].replace('p', '.')
    eta_max = graph_name.split('_')[2].replace('p', '.')
    eta_label = eta_min + ' < |\eta| < ' + eta_max

    leg = ROOT.TLegend(0.2, 0.65, 0.7, 0.78)
    leg.SetHeader(eta_label, "C")
    leg_str = 'y = %.2e + (%.2e \pm %.1e) * d0' %(graph.GetFunction('line').GetParameter(1), graph.GetFunction('line').GetParameter(0), graph.GetFunction('line').GetParError(0))
    leg.AddEntry( graph.GetFunction('line'), leg_str)

    graph.Draw("APZ")
    leg.Draw("SAME")

    cms_latex = ROOT.TLatex()
    cms_latex.SetTextAlign(11)
    cms_latex.SetTextSize(0.025)
    cms_latex.DrawLatexNDC(0.2, 0.82, '#scale[2.0]{CMS #bf{#it{Preliminary}}}')
    cms_latex.DrawLatexNDC(0.8, 0.94,'#font[42]{#scale[1.5]{%sDY}}'%YEAR)
    

    canv.SaveAs( ('outputs/geofit/%s/'%YEAR) +graph_name+'.pdf')


def PlotGeoFit(out_file, samp_files, tree_name):
    d0_bins = np.linspace(-100, 100, 81)
    eta_bins = np.array([0, 0.9, 1.7, 2.4])
    print (d0_bins)    
    hists = {}
    hist_ptrs = {}
    graphs = {}

    df = ROOT.RDataFrame(tree_name, samp_files)
    print (df.Count().GetValue())
    out_file.cd()

    df_mu = df.Define("mu_pass", "(Muon_corrected_pt>20) * (abs(Muon_eta)<2.4) * Muon_mediumId * (Muon_pfIsoId>1) * (abs(Muon_dxy)<0.05) * (abs(Muon_dz)<0.1) >0")
    df_dimu = df_mu.Filter("nMuon == 2 && Muon_charge[mu_pass==1][0]+Muon_charge[mu_pass==1][1]==0", "Select good dimuon events")
    df_z = df_dimu.Define("dimu_mass", "InvariantMass(Muon_corrected_pt, Muon_eta, Muon_phi, Muon_mass)").Filter("dimu_mass > 70", "on shell Z")
#    df_delPt = df.Filter("nMuon==2 && muon_pass[0]==1 && muon_pass[1]==1 && muon_charge[0]+muon_charge[1]==0", "good muons")\
#                 .Define("delPt", " muon_charge * (Muon_corrected_pt[muon_pass==1] - muon_pt_gen) / (muon_pt_gen * muon_pt_gen)") # All vecs need to have exact same size
    df_delPt = df_z.Define("delPt", " muon_charge * (Muon_corrected_pt[mu_pass==1] - muon_pt_gen) / (muon_pt_gen * muon_pt_gen)")
    report = df_delPt.Report()
    report.Print()

    for ieta in range( len(eta_bins) - 1 ):
        eta_str = "(%.1f <= abs(muon_eta) && abs(muon_eta) < %.1f)" %(eta_bins[ieta], eta_bins[ieta+1])
        for id0 in range( len(d0_bins) - 1 ):
            d0_str = "(%.0f < muon_d0bs_micron && muon_d0bs_micron < %.0f)"%(d0_bins[id0], d0_bins[id0+1])
            df_delsel = df_delPt.Define("pt_pass", "%s && %s"%(eta_str, d0_str))\
                                .Define("delPt_sel", "delPt[pt_pass]")
            hists["eta%d_d0%d"%(ieta+1, id0+1)] = df_delsel.Histo1D(("eta%d_d0%d"%(ieta+1, id0+1), "", 1000, -0.005, 0.005), "delPt_sel")

    print ("Start running graphs")
    for ieta in range( len(eta_bins) - 1 ):
        graph_name = ("eta_%.1f_%.1f"%(eta_bins[ieta], eta_bins[ieta+1])).replace('.', 'p')
        graphs[graph_name] = ROOT.TGraphAsymmErrors()
        graphs[graph_name].SetName(graph_name)
        ipoint = 0
        for id0 in range( len(d0_bins) - 1 ):
            d0_center = (d0_bins[id0] + d0_bins[id0+1]) / 2 
            d0_err    = (d0_bins[id0+1] - d0_bins[id0]) / 2
            cent_bin, lo_bin, hi_bin = findCenterRange(hists["eta%d_d0%d"%(ieta+1, id0+1)], 20) 
            pt_center = hists["eta%d_d0%d"%(ieta+1, id0+1)].GetBinCenter(cent_bin)
            pt_lo_err = pt_center - hists["eta%d_d0%d"%(ieta+1, id0+1)].GetBinCenter(lo_bin)
            pt_hi_err = hists["eta%d_d0%d"%(ieta+1, id0+1)].GetBinCenter(hi_bin) - pt_center
            if pt_lo_err < 0 or pt_hi_err < 0:
                print ("Weird case for eta bin %d, d0 bin %d" %(ieta, id0))
                print ("pt_lo_err = %f, pt_hi_err = %f" %(pt_lo_err, pt_hi_err))
                pt_lo_err = 1
                pt_hi_err = 1           

            if cent_bin == hists["eta%d_d0%d"%(ieta+1, id0+1)].GetNbinsX()//2 and lo_bin == 1 and hi_bin == hists["eta%d_d0%d"%(ieta+1, id0+1)].GetNbinsX(): continue 
            graphs[graph_name].SetPoint(ipoint, d0_center, pt_center)
            graphs[graph_name].SetPointError(ipoint, d0_err, d0_err, pt_lo_err, pt_hi_err)
            ipoint += 1
            hists["eta%d_d0%d"%(ieta+1, id0+1)].Write()

        F_line = ROOT.TF1("line", "[0]*x+[1]", -100, 100)
        F_line.SetParNames("Slope", "Intercept")
        F_line.SetParameters( 1e-2, 0)

        for i in range(10):
            graphs[graph_name].Fit("line", "QR")
            F_line.SetParameters( F_line.GetParameter(0), F_line.GetParameter(1) )

        ROOT.gStyle.SetOptFit(111)
        graphs[graph_name].GetFunction("line").SetLineColor(ROOT.kBlue)
        graphs[graph_name].GetFunction("line").SetLineWidth(2)
        graphs[graph_name].Write()
        DrawCanv(out_file, graphs[graph_name])

    print ("GeoFit parameters derived.")
    return 0


def main():
    samp_files = []
    for f in FILES:
        samp_files.append(FILE_LOC + '/' + f)
    if not os.path.exists('outputs/geofit/%s'%YEAR):
        os.makedirs('outputs/geofit/%s'%YEAR)
    out_file = ROOT.TFile("outputs/geofit/%s/GeoFitParams.root"%YEAR, "RECREATE")

    start = timeit.default_timer()
    print (start)
    PlotGeoFit(out_file, samp_files, TREE)
    stop  = timeit.default_timer()
    print (("Time: ", stop - start))
if __name__ == '__main__':
    main()

