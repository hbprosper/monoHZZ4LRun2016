# monoHZZ4LRun2016
## 13 TeV pp -> H -> ZZ -> 4lepton analysis

## Introduction
Updated:	10 June 2017

This package contains Python programs that implement studies  of pp ->
H -> ZZ -> 4lepton as well as its 
statistical analysis in the context of the mono-Higgs searches by the
CMS
collaboration.
The programs use the reduced ntuples (with Root tree name HZZ4LeptonsAnalysisReduced)
created by
Nicola and Giorgia. For convenience, the events from these ntuples are
consolidated into a smaller set of ntuples in which the order of
events has been randomly shuffled and the provenance of each event is noted.

The reduced ntuples are consolidated into
```
	ntuple_data.root
	ntuple_higgs.root
	ntuple_bkg.root
	ntuple_SM.root
	ntuple_ZpBary_MZpmmmmm_MAmmmmm.root
	ntuple_Zprime_MZpmmmmm_MAmmmmm.root
```
in which the order of events is randomized and
where _mmmmm_ are the masses of the Z' and A. Two new fields are
added to the consolidated ntuples: _f\_sample_ and
_f\_finalstate_. The field
_f\_sample_
identifies the original reduced ntuple from which an event came, while
the field
_f\_finalstate_ identifies one of three final states: 1 = 2e2mu, 2 =
4e, and 3 = 4mu. The value of _f\_sample_ field is the ordinal value
of the reduced ntuple filename in the appropriate filelist (see
below). The procedure for making the consolidated ntuples
is described below. 

### Setup
```
   source setup.sh
   ```
Unpack the reduced ntuples in the  _store_ directory, then
follow the instructions below.
   
#### 1. Create filelists

```
   makeFilelists.py store/histos4mu_25ns/*.root
   makeFilelists.py store/histos4e_25ns/*.root
   makeFilelists.py store/histos2e2mu_25ns/*.root
   ```
This creates in _store_ filelists for each final state and each
   category of event: data, non-Higgs background, Higgs, and
   mono-Higgs signals.

#### 2. Create ntuples
In this step, we use the filelists created in the previous step to
create new ntuples that merge the events from the original reduced ntuples. All
Higgs
events go to _ntuple\_finalstate\_higgs.root_, for example
   _ntuple\_4mu\_higgs.root_. All
non-Higgs standard model events go to
   _ntuple\_finalstate\_bkg.root_, and similarly for real data and
   each mono-Higgs signal model. The provenance of each event is kept in the variable
_f\_sample_ that flags the file from which the event came by giving
   the file's
ordinal
value (starting at zero) in the associated filelist. The ordinal value
   of the file
is in the first column of the  filelist.
```
   find store/filelist_*.txt > filelists.txt
   writeAllNtuples.py
```
For each filelist in _filelists.txt_, this program reads from the listed
files,
randomly shuffles the
events from the files, and writes the randomly shuffled events to another ntuple.

#### 3. Merge ntuples so all final states for a given source are in the same file
In this step, the final states are merged (and again events are
shuffled) so that we arrive at the ntuples _ntuple\_data.root_ ,
_ntuple\_bkg.root_, _ntuple\_higgs.root_, and an ntuple for each
mono-Higgs signal. The final states are flagged with the variable
_f\_finalstate_.
```
   find store/ntuple_4mu_*.root > mergelists.txt
   mergeAllNtuples.py
```
 It is also convenient to create one more ntuple in which all Standard
 Model events are merged using
 
 ```
	makeSMNtuple.py
 ```
If space is an issue, the ntuples in _store_ separated by final state can be deleted.

   
### Fitting Higgs + non-Higgs histograms to Data
   
