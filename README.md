# HiggsAnalysesRDF

Some analysis scripts based on RDataFrame

## Set up

It is recommended to run this repo with ROOT version 6.22 (available in CMSSW\_12 and later).
```
scram project -n RDF_analyses CMSSW_12_1_0_pre3
cd RDF_analyses/src
cmsenv
git clone git@github.com:zuoxunwu/HiggsAnalysesRDF.git HiggsAnalysesRDF
```

## Run scripts
As python2 is deprecated from CMSSW\_12 and on, and ROOT there is build with python3.
**Remember always to run scripts with python3**, for example
```
python3 scripts/test.py
```

## More about versions

#### ROOT
RDF has been available in ROOT since ROOT 6.14 and has evolved quite a lot.
It is highly recommended to use ROOT versions later than 6.16 because RDF in ROOT 6.14 cannot take RVec\<bool> in expressions RDF.Filter() or RDF.Define(), which is necessary for object selections.
See more details on [ROOT Forum](https://root-forum.cern.ch/t/rdataframe-and-vectors-of-booleans/31882) 

Note that RVec\<bool> is properly handled in RDF.Filter() and RDF.Define() since ROOT 6.16, but only become acceptable to RDF.Histo1D() in ROOT 6.24. (See more at [git issue](https://github.com/root-project/root/issues/6675)). You can easily get around this by 
```
df.Define('vec_int', '1 * vec_bool').Histo1D('vec_int')
```

If you prefer to use ROOT 6.24, you can set up a standalone ROOT with
```
source /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.24.02/x86_64-centos7-gcc48-opt/bin/thisroot.sh
```

#### python3
To convert old python2 scripts to python3, you can run
```
2to3 example.py
```
It tells you what you need to change.
