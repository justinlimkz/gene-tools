# gene-tools

Work in progress for my UROP at the Lage Lab at the Broad Institute of Harvard and MIT / Massachusetts General Hospital.

### map

The main project - automating the assignment of protein IDs / accession numbers to HGNC gene names. Takes in a list of IDs as input, separated by newlines, and returns a list of assigned gene names where possible, and provides information about all other cases. For instance, map reports unassigned protein IDs and returns its Ensembl ID wherever possible.

### match

match takes in two lists of gene names and returns the genes present in both lists, taking into account synonyms and old names. 