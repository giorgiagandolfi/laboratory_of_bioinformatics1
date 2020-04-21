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

If you want to check type this command:

`head Human_NotPF00014_Training.fasta`

and see the output. My output is the following:

`>sp|Q8N8B7|TEANC_HUMAN Transcription elongation factor A N-terminal and central domain-containing protein OS=Homo sapiens OX=9606 GN=TCEANC PE=1 SV=2
MSDKNQIAARASLIEQLMSKRNFEDLGNHLTELETIYVTKEHLQETDVVRAVYRVLKNCP
SVALKKKAKCLLSKWKAVYKQTHSKARNSPKLFPVRGNKEENSGPSHDPSQNETLGICSS
NSLSSQDVAKLSEMIVPENRAIQLKPKEEHFGDGDPESTGKRSSELLDPTTPMRTKCIEL
LYAALTSSSTDQPKADLWQNFAREIEEHVFTLYSKNIKKYKTCIRSKVANLKNPRNSHLQ
QNLLSGTTSPREFAEMTVMEMANKELKQLRASYTESCIQEHYLPQVIDGTQTNKIKCRRC
EKYNCKVTVIDRGTLFLPSWVRNSNPDEQMMTYVICNECGEQWYHSKWVCW
>sp|O75494|SRS10_HUMAN Serine/arginine-rich splicing factor 10 OS=Homo sapiens OX=9606 GN=SRSF10 PE=1 SV=1
MSRYLRPPNTSLFVRNVADDTRSEDLRREFGRYGPIVDVYVPLDFYTRRPRGFAYVQFED
VRDAEDALHNLDRKWICGRQIEIQFAQGDRKTPNQMKAKEGRNVYSSSRYDDYDRYRRSR`

