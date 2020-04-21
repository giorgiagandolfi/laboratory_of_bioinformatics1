# Laboratory of Bioinformatics: lecture April 15
## Build a *blast*-based method to predict the presence of BPTI/Kunitz domain in proteins available in SwissProt using the human proteins as a reference. 
The main steps are:
1. select all proteins in SwissProt with BPTI/KUnitz domain
2. separate human from not human proteins. Use the non human proteins as a positive in the training set
3. generate a random set of negative of the same size of the positive set
4. remove both positives and negatives from SwissProt and perform the prediction based on the results of the *blast* search
-----------------------------------------
### Find human and non-human Kunitz domain proteins in SwissProt
We have to search all human proteins in SwissProt containing the Kunitz domain by using the following query: `reviewed: yes organism:"Homo sapiens (Human) [9606]" database: (type:pfam PF00014)`. We retrieve 18 proteins. Let's download them in fasta format. Then we search in UniProt all the non-human proteins containing the Kunitz domain by using the following query: `database: (type:pfam PF00014) NOT organism:"Homo sapiens (Human) [9606]" AND reviewed: yes`. We retrieve 341 proteins. Let's download them in fasta format too. 

### Find human proteins without Kunitz domain in SwissProt
We have to search all human proteins in SwissProt not containing the Kunitz domain by using the following query:`NOT database: (type:pfam PF00014) AND organism:"Homo sapiens (Human) [9606]" AND reviewed: yes`. We retrieve 20347 proteins. Let's download them in fasta format. 

### Create the human database as reference
We generate the database of human proteins containing Kunitz domain usign this command:
`formatdb -i Human_PF00014.fasta -p`

### Create the training and testing sets for the negatives
We want to split the `Human_NotPF00014.fasta`, which contains 20347 proteins, into two sets, the training and the testing. We decide to split the negative set at the 10000th protein sequence included. We want to find the number of the line referring to the end of the 10000th protein sequence.
`grep ">" Human_NotPF00014.fasta -m 10000 | tail -1
>sp|O95081|AGFG2_HUMAN Arf-GAP domain and FG repeat-containing protein 2 OS=Homo sapiens OX=9606 GN=AGFG2 PE=1 SV=2
grep ">" Human_NotPF00014.fasta -m 10001 -n | tail -1
109075:>sp|P32970|CD70_HUMAN CD70 antigen OS=Homo sapiens OX=9606 GN=CD70 PE=1 SV=2`
The 10000th protein sequence ends at line 10974. Let's split the negative dataset.
`head -n 109074 Human_NotPF00014.fasta  >Human_NotPF00014_Training.fasta
tail -n +109075 Human_NotPF00014.fasta  >Human_NotPF00014_Testing.fasta`

### BLAST the positive training set 
Now we BLAST the positive set against itself as a consistency test: we are interesting in seeing the range of E-value that we get. 
`blastpgp -i Human_PF00014.fasta -d Human_PF00014.fasta -o Human_PF00014.bl8 -m 8`
Then let's sort the output file based on the column containing the e-vale (column 11).  
`sort -grk 11 Human_PF00014.bl8`
The option -g can be used for sorting instead of -n. -g means "general sort". Sometimes we have to modify our ./bashrc file by adding the alias:
`alias sort = 'LC_ALL=C sort `
Save the changes in ./bashrc file and quit/reopen the terminal.

### Negative training set
Now we BLAST the negative training set against the Human_PF00014.fasta database.
`blastpgp -i Human_NotPF00014_Training.fasta -d Human_PF00014.fasta -o Human_NOtPF00014_training.bl8 -m 8`
I can also specify an e-value like `-e 100`. Remember: the default e-value of BLAST is 10. 
Then, we want to sort the output in order to find the sequence with the lowest e-value (the best one). 
`sort -gk 11 Human_NotPF00014_Training.bl8`
It is possible to observe that there are  any non-Kunitz domains proteins that have a really low e-value. 

### Negative testing set
Now we BLAST the negative testing set against the HUman_PF00014.fasta databse. 
`blastpgp -i Human_NotPF00014_Testing.fasta -d Human_PF00014.fasta -o Human_NotPF00014_Testing.bl8 -m 8`

### Positive testing set
Now we BLAST the positive testing set against the HUman_PF00014.fasta databse. 
`blastpgp -i NotHuman_PF00014.fasta -d Human_PF00014.fasta -o NotHuman_PF00014.bl8 -m 8`
We need to rank the output on the positive set. To do so we have to grep based on the identifiers and select the best e-value for each ids.

for i in `awk '{print $1}' NotHuman_PF00014.bl8 |sort -u `
do 
  grep $i NotHuman_PF00014.bl8 |sort -gk 11 |head -n 1
done > NotHuman_PF00014.bl8.best`

Now we have to select the e-value of 0.0001 as a classification thresholf for the Kunitz domain proteins. In this way we can calculate the number of proteins with the maximum e-value below that threshold. 

`awk '{if ($11<0.001) print $1}'  NotHuman_PF00014.bl8.best  |sort -u |wc -l
  340

awk '{if ($11<0.001) print $1}'  Human_NotPF00014_Training.bl8  |sort -u |wc
  290

awk '{if ($11<0.001) print $1}'  Human_NotPF00014_Tresting.bl8  |sort -u |wc -l
  200`
