# Laboratory of Bioinformatics: lecture April 15
## Build a *blast*-based method to predict the presence of BPTI/Kunitz domain in proteins available in SwissProt using the human proteins as a reference. 
The main steps are:
1. select all proteins in SwissProt with BPTI/KUnitz domain
2. separate human from not human proteins. Use the non human proteins as a positive in the training set
3. generate a random set of negative of the same size of the positive set
4. remove both positives and negatives from SwissProt and perform the prediction based on the results of the *blast* search
-----------------------------------------
### Find human and non-human Kunitz domain proteins in SwissProt
<p align="justify">
We have to search all human proteins in SwissProt containing the Kunitz domain by using the following query: `reviewed: yes organism:"Homo sapiens (Human) [9606]" database: (type:pfam PF00014)`. We retrieve 18 proteins. Let's download them in fasta format. Then we search in UniProt all the non-human proteins containing the Kunitz domain by using the following query: `database: (type:pfam PF00014) NOT organism:"Homo sapiens (Human) [9606]" AND reviewed: yes`. We retrieve 341 proteins. Let's download them in fasta format too. 
</p>
### Find human proteins without Kunitz domain in SwissProt
We have to search all human proteins in SwissProt not containing the Kunitz domain by using the following query:`NOT database: (type:pfam PF00014) AND organism:"Homo sapiens (Human) [9606]" AND reviewed: yes`. We retrieve 20347 proteins. Let's download them in fasta format. 

