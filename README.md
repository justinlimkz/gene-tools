# gene-tools

Work in progress for my UROP at the Lage Lab at the Broad Institute of Harvard and MIT / Massachusetts General Hospital.

### map

The main project - automating the assignment of protein IDs / accession numbers to HGNC gene names. Takes in a list of IDs as input, separated by newlines, and returns a list of assigned gene names where possible, and provides information about all other cases. For instance, map reports unassigned protein IDs and returns its Ensembl ID wherever possible.

### match

match takes in two lists of gene names and returns the genes present in both lists, taking into account synonyms and old names. 

## Setup

The tools draw information from [UniProt](http://www.uniprot.org) and [HGNC](http://www.genenames.org), both locally and programmatically through queries. To set up the local databases properly, follow the instructions in the following folders: `./human_data/` and `./hgnc_data`. These are repeated below for completeness.

1. `./human_data`: From the UniProt Downloads [page](http://www.uniprot.org/downloads), go to 'Taxonomic Divisions' and download the `uniprot_sprot_human.dat.gz` and `uniprot_trembl_human.dat.gz` files. Extract them into the `./human_data` folder. Then run `grep.sh` to create the `data.txt` file.

2. `./hgnc_data`: From the HGNC Custom Downloads [page](http://www.genenames.org/cgi-bin/download), download two files:
  1. Download a file with _only_ the 'Approved Symbol' and 'Accession Numbers' checked. Save this as `hgnc_symbol_ac.txt` in the `./hgnc_data` folder.
  2. Download another file with _only_ the 'Approved Symbol, 'Previous Symbols' and 'Synonyms' checked. Save this as `hgnc_symbol_previous_synonym.txt` in the `./hgnc_data` folder.
  
At the end of this setup, your directory should look as so (the map and match directories are not expanded, they should not be modified):

```
gene-tools
- hgnc_data
--- hgnc_symbol_ac.txt
--- hgnc_symbol_previous_synonym.txt
- human_data
--- data.txt
--- grep.sh
--- uniprot_sprot_human.dat
--- uniprot_trembl_human.dat
- map
- match
- README.md
- testing
```

## Usage

### map

__map__ takes input from `./map/in.txt`, which is a list of UniProt IDs or Accession Numbers, and outputs `./map/results.txt`, a tab-spaced list of those IDs with corresponding HGNC gene names. For instance, the ID `Q15465` will be mapped to `SHH`. 

__map__ also identifies problematic cases and resolves them accordingly where possible. For instance, 

1. _Obsolete IDs_: IDs that were once in use, but not any more. e.g. `E9PEB9` is an obsolete ID on UniProt and cannot be found on HGNC - __map__ will tell you that the last existing gene name on UniProt is `DST` and checks if `DST` is the correct HGNC gene name (it is). 

2. _Unassigned IDs_: IDs that exist, but have not been assigned a gene symbol. e.g. `P00761` does not have an assigned gene name - __map__ reports this, and returns its Ensembl ID where possible.

3. _Bad IDs_: IDs that do not exist, possibly as a result of a typo.

### match

__match__ takes input from `in.txt` and is still in progress.