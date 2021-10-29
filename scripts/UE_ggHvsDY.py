import os
import sys
import timeit
import numpy as np
import math

import ROOT
ROOT.ROOT.EnableImplicitMT()

from CMS_style import setTDRStyle

print (os.getcwd())
ROOT.gInterpreter.Declare('#include "%s/helpers/func_RDF.h"'%os.getcwd())

TREE  = 'Events'

DY_files  = ["samples/DY2018_evt50k.root", "samples/DY2018_evt40k_01522709.root", "samples/DY2018_evt10k.root"]
ggH_files = ["samples/ggH2018_evt50k.root", "samples/ggH2018_evt50k_12A22FB3.root"]

colors = {'ggH':ROOT.kBlue+2, 'DY':ROOT.kRed}

def DrawCanv(key, h_H, h_Z):
    setTDRStyle()
    ROOT.gStyle.SetOptFit(0)
    ROOT.gStyle.SetLegendBorderSize(0)
    ROOT.gStyle.SetLegendFont(42)
    ROOT.gStyle.SetLegendTextSize(0.035)
    ROOT.gStyle.SetErrorX(0.0)

    canv = ROOT.TCanvas(key, key, 600, 600)
    canv.SetLeftMargin(0.15)
    canv.SetTopMargin(0.08)
    canv.cd()

    print (h_H.GetEntries())
    print (key)
    print (type(key))
    print (type(h_H))
    print (type(h_Z))

    Xname = key
    if key == 'N_ch': Xname = 'N_{ch}'
    elif key == 'ptS_sum':  Xname = '#sum#||{p^{T}_{ch}}'
    elif key == 'ptS_ave': Xname = '#bar{#||{p^{T}_{ch}}}'
    elif key == 'pzS_sum':  Xname = '#sum#||{p^{z}_{ch}}'
    elif key == 'pzS_ave': Xname = '#bar{#||{p^{z}_{ch}}}'
    elif key == 'ptV_sum':  Xname = '#sum#vec{p^{T}_{ch}}'
    elif key == 'pzV_sum':  Xname = '#sum#vec{p^{z}_{ch}}'
    elif key == 'recoil_pt': Xname = 'p^{T}_{recoil}'

    h_Z.GetXaxis().SetTitle(Xname)
    h_Z.GetXaxis().SetTitleSize(0.035)
    h_Z.GetXaxis().SetTitleOffset(1.2)
    h_Z.GetXaxis().SetLabelSize(0.03)
    h_Z.GetYaxis().SetTitle("a.u.")
    h_Z.GetYaxis().SetRangeUser(0, h_Z.GetMaximum() * 1.4)
    h_Z.GetYaxis().SetTitleSize(0.035)
    h_Z.GetYaxis().SetTitleOffset(1.9)
    h_Z.GetYaxis().SetLabelSize(0.03)

    leg = ROOT.TLegend(0.6, 0.6, 0.8, 0.8)
    leg.AddEntry(h_Z, 'DY', 'L')
    leg.AddEntry(h_H, 'ggH')

    h_Z.Draw("histC")
    h_H.Draw("histCSAME")
    leg.Draw("SAME")

    cms_latex = ROOT.TLatex()
    cms_latex.SetTextAlign(11)
    cms_latex.SetTextSize(0.025)
    cms_latex.DrawLatexNDC(0.2, 0.82, '#scale[2.0]{CMS #bf{#it{Simulation Preliminary}}}')
    cms_latex.DrawLatexNDC(0.8, 0.94,'#font[42]{#scale[1.5]{2018}}')

    canv.SaveAs( 'outputs/UE_HvsZ/%s'%key+'.pdf')


def UE_vars(samp_name, file_list, out_file, hists):
    df = ROOT.RDataFrame(TREE, file_list)
    print (df.Count().GetValue())

    out_file.cd()

    df_mu   = df.Define("Mu_pass", "(Muon_pt>20) * (abs(Muon_eta)<2.4) * Muon_mediumId * (Muon_pfIsoId>1) * (abs(Muon_dxy)<0.05) * (abs(Muon_dz)<0.1) >0")
    df_dimu = df_mu.Filter("nMuon == 2 && Muon_charge[Mu_pass==1][0]+Muon_charge[Mu_pass==1][1]==0", "Select good dimuon events")
    df_evtsel = df_dimu.Define("dimu_mass", "InvariantMass(Muon_pt, Muon_eta, Muon_phi, Muon_mass)").Filter("dimu_mass > 70", "mass > 70")
    
    # All neutral hadrons are pdgId 130 (K_L), all charged hadrons are +/-211 (pi)
    df_jet = df_evtsel.Define("jet_sel", "(Jet_jetId==6) * (Jet_puId==7 || Jet_pt>50)").Define("nSelJets", "Sum(jet_sel)")
    df_ch  = df_jet.Define("ch_sel", "(pfCands_pt>0.9) * (abs(pfCands_eta)<2.4) * (pfCands_fromPV > 1) * (abs(pfCands_pdgId)==211)")\
                   .Define("N_ch", "Sum(ch_sel)")\
                   .Define("ptS_sum", "Sum(pfCands_pt[ch_sel==1])")\
                   .Define("ptS_ave", "ptS_sum/N_ch")\
                   .Define("pzS_sum", "abs(Sum(vec4_pz(pfCands_pt[ch_sel==1], pfCands_eta[ch_sel==1], pfCands_phi[ch_sel==1], pfCands_mass[ch_sel==1])))")\
                   .Define("pzS_ave", "pzS_sum/N_ch")\
                   .Define("ptV_sum", "sum_vec4_pt(pfCands_pt[ch_sel==1], pfCands_eta[ch_sel==1], pfCands_phi[ch_sel==1], pfCands_mass[ch_sel==1])")\
                   .Define("pzV_sum", "sum_vec4_pz(pfCands_pt[ch_sel==1], pfCands_eta[ch_sel==1], pfCands_phi[ch_sel==1], pfCands_mass[ch_sel==1])")\
                   .Define("dimu_phi", "sum_vec4_phi(Muon_pt, Muon_eta, Muon_phi, Muon_mass)")\
                   .Define("recoil_sel", "ch_sel * (abs(DeltaPhi(pfCands_phi, dimu_phi))>M_PI*2.0/3.0)")\
                   .Define("recoil_pt", "sum_vec4_pt(pfCands_pt[recoil_sel==1], pfCands_eta[recoil_sel==1], pfCands_phi[recoil_sel==1], pfCands_mass[recoil_sel==1])")
    # pz and vector sum
    hists["N_ch_"+samp_name]    = df_ch.Histo1D(("N_ch_"+samp_name, "", 100, 0, 100), "N_ch")
    hists["ptS_sum_"+samp_name] = df_ch.Histo1D(("ptS_sum_"+samp_name, "", 100, 0, 500), "ptS_sum")
    hists["ptS_ave_"+samp_name] = df_ch.Histo1D(("ptS_ave_"+samp_name, "", 100, 0, 10),  "ptS_ave")
    hists["pzS_sum_"+samp_name] = df_ch.Histo1D(("pzS_sum_"+samp_name, "", 100, 0, 500), "pzS_sum")
    hists["pzS_ave_"+samp_name] = df_ch.Histo1D(("pzS_ave_"+samp_name, "", 100, 0, 10),  "pzS_ave")
    hists["ptV_sum_"+samp_name] = df_ch.Histo1D(("ptV_sum_"+samp_name, "", 100, 0, 100), "ptV_sum")
    hists["pzV_sum_"+samp_name] = df_ch.Histo1D(("pzV_sum_"+samp_name, "", 100, 0, 200), "pzV_sum")
    hists["recoil_pt_"+samp_name] = df_ch.Histo1D(("recoil_pt_"+samp_name, "", 100, 0, 100), "recoil_pt")

    for key in hists:
        if samp_name not in key: continue
        hists[key] = hists[key].GetValue()
        hists[key].SetDirectory(0)
        hists[key].Scale(1/hists[key].Integral())
        hists[key].SetLineColor(colors[samp_name])
        hists[key].SetLineWidth(2)
        hists[key].Write()

    return hists


def main():
    if not os.path.exists('outputs/UE_HvsZ'):
        os.makedirs('outputs/UE_HvsZ')
    out_file = ROOT.TFile("outputs/UE_HvsZ/vars.root", "RECREATE")

    start = timeit.default_timer()
    print (start)

    hists = {}
    UE_vars('ggH', ggH_files, out_file, hists)
    UE_vars('DY', DY_files, out_file, hists)

    for key in hists:
        print (key)
        if 'DY' in key: continue
        key = key.replace('_ggH', '')
        DrawCanv(key, hists[key+'_ggH'], hists[key+'_DY'])

    stop  = timeit.default_timer()
    print (("Time: ", stop - start))
if __name__ == '__main__':
    main()

