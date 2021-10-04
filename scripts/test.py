import ROOT

ROOT.gROOT.SetBatch(True)

ROOT.ROOT.EnableImplicitMT()

#rdf = ROOT.ROOT.RDataFrame("Events", "root://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/GluGluToHToTauTau.root")
rdf = ROOT.ROOT.RDataFrame("Events", "/eos/cms/store/user/xzuo/H2XXNanoPost/2018/v0p0-5-g86fd7f9/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/DY/210921_001323/0000/tree_1.root")

rdf = rdf.Define("Muon_passSelection", "Muon_tightId && Muon_pfRelIso03_all<0.15") \
         .Define("Muon_pt_selected", "Muon_pt[Muon_passSelection]")

h = rdf.Histo1D(("htest", "htest", 100, 0, 100), "Muon_pt_selected")

c1 = ROOT.TCanvas("c1", "c1", 800, 600)
h.Draw()
c1.Print("test.png")
