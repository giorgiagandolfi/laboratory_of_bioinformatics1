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
`formatdb -i Human_PF00014.fasta -p T`

### Create the training and testing sets for the negatives
We want to split the `Human_NotPF00014.fasta`, which contains 20347 proteins, into two sets, the training and the testing. We decide to split the negative set at the 10000th protein sequence included. We want to find the number of the line referring to the end of the 10000th protein sequence.
`grep ">" Human_NotPF00014.fasta -m 10000 | tail -1
>sp|O95081|AGFG2_HUMAN Arf-GAP domain and FG repeat-containing protein 2 OS=Homo sapiens OX=9606 GN=AGFG2 PE=1 SV=2
grep ">" Human_NotPF00014.fasta -m 10001 -n | tail -1
109075:>sp|P32970|CD70_HUMAN CD70 antigen OS=Homo sapiens OX=9606 GN=CD70 PE=1 SV=2`
The 10000th protein sequence ends at line 10974. Let's split the negative dataset.
`head -n 109074 Human_NotPF00014.fasta  >Human_NotPF00014_Training.fasta
tail -n +109075 Human_NotPF00014.fasta  >Human_NotPF00014_Testing.fasta`
The training test contains 10000 proteins while the testing set contains 10347 proteins. To check the number of proteins in the file:
`grep ">" Human_NotPF00014_Training.fasta | wc -l`

### BLAST the positive training set 
Now we BLAST the positive set against itself as a consistency test: we are interesting in seeing the range of E-value that we get. The command `-m 8` is needed for the tabular format.
`blastpgp -i Human_PF00014.fasta -d Human_PF00014.fasta -o Human_PF00014.bl8 -m 8`
Then let's sort the output file based on the column containing the e-vale (column 11). The worst e-value will be at the top of the list. The worts e-value is 9.9: this beacuse the default e-value of BLAST is 10. 
`sort -gk 11 Human_PF00014.bl8`
If we want, we can increase the evalue:
`blastpgp -i Human_PF00014.fasta -d Human_PF00014.fasta -o Human_PF00014.bl8 -m 8 -e 1000`
The option -g can be used for sorting instead of -n. -g means "general sort". Sometimes we have to modify our ./bashrc file by adding the alias:
`alias sort = 'LC_ALL=C sort `
Save the changes in ./bashrc file and quit/reopen the terminal.
We can extract all the complete matches of the sequence against itself, we have to run this command:
`awk '{if($1==$2) print $0}' HUman_PF00014.bl8}' | wc`
In this way we get 18, as espected.

### Negative training set
Now we BLAST the negative training set against the Human_PF00014.fasta database.
`blastpgp -i Human_NotPF00014_Training.fasta -d Human_PF00014.fasta -o Human_NOtPF00014_training.bl8 -m 8 -e 100`. Remember: the default e-value of BLAST is 10. Now we want to know the best hit between the negative non_Kunitz and the human Kunitz. We want to sort the output in order to find the sequence with the lowest e-value (the best one). 
`sort -gk 11 Human_NotPF00014_Training.bl8`
There are two sequences that are not classified as human KUnitz, but have an e-value of 0.0. Probably these two sequence have a similar domain to Kunitz, but not annotaed as Kunitz domain. We see that the e-value is around 0.001. This threshold can be used as a value for classify as negatives the sequences of the training set.  

### Negative testing set
Now we BLAST the negative testing set against the HUman_PF00014.fasta databse. 
`blastpgp -i Human_NotPF00014_Testing.fasta -d Human_PF00014.fasta -o Human_NotPF00014_Testing.bl8 -m 8`
If we sort against the 11th, we have very low number of e-value.

### Positive testing set
Now we BLAST the positive testing set against the HUman_PF00014.fasta databse. 
`blastpgp -i NotHuman_PF00014.fasta -d Human_PF00014.fasta -o NotHuman_PF00014.bl8 -m 8 -e 1000`.
We have multiple hits: we need to provide only the higher score of each sequence. We need to rank the output on the positive set. To do so we have to grep based on the identifiers and select the best e-value for each ids.

`for i in ``awk '{print $1}' NotHuman_PF00014.bl8 |sort -u`
`do 
  grep $i NotHuman_PF00014.bl8 |sort -gk 11 |head -n 1
done > NotHuman_PF00014.bl8.best``

` If we sort against the 11th column in reverse mode, we get the worst e-value between human and non-human proteins with Kunitz domain, that can be used as a selection threshold. The worst e-value is 0.054.

So far we have:
1. for the .best we have very low e-values
2. the best e-value of the negative training is lower than the best e-value of the negative testing set.

Now we have to select the e-value of 0.0001 as a classification thresholf for the Kunitz domain proteins. In this way we can calculate the number of proteins with the maximum e-value below that threshold. 

`awk '{if ($11<0.001) print $1}'  NotHuman_PF00014.bl8.best  |sort -u |wc -l
  340` #true positive
`awk '{if ($11>=0.001) print $1}'  NotHuman_PF00014.bl8.best  |sort -u |wc -l
  1` #false negative
  `awk '{if ($11<0.001) print $1}'  Human_NotPF00014_Training.bl8  |sort -u |wc
  290`#false positive
true positive=10000-290
`awk '{if ($11<0.001) print $1}'  Human_NotPF00014_Testing.bl8  |sort -u |wc -l
  200` #false positive
 true positive=10347-200
 
Now we can calculate the performance of the method selecting an e-value=0.0001 in terms of accurancy adn MCC (Matthews Correlation Coeffcient). This program takes in inuput the protein ID, the lowest e-value of the protein and the class (0: false positive/false negatives and 1: treu positive/true negative),

```pyhton
#!/usr/bin/env python
import sys, math

def get_blast(filename):
    f_list=[]
    d={}
    f=open(filename)
    for line in f:
        v=line.rstrip().split()
        d[v[0]]=d.get(v[0],[])
        d[v[0]].append([float(v[1]),int(v[2])])
    for k in d.keys():
        d[k].sort()
        f_list.append(d[k][0]) #lowest e-value
    return f_list

def get_cm(data,th):
    #CM=[[TP, FP],[FN,TN]]
    #0 = Negatives 1=Positives
    cm=[[0.0,0.0],[0.0,0.0]]
    for i in data:
        #true positive
        if i[0]<th and i[1]==1:
            cm[0][0]=cm[0][0]+1
        #false positve
        if i[0]>=th and i[1]==1:
            cm[1][0]=cm[1][0]+1
        #false negative
        if i[0]<th and i[1]==0:
            cm[0][1]=cm[0][1]+1
        #true negative
        if i[0]>=th and i[1]==0:
            cm[1][1]=cm[1][1]+1
    return cm

#acc=(TP+TN)/(TP+TN+FN+FP)
#it is not so informative
def get_acc(cm):
  return float(cm[0][0]+cm[1][1])/(sum(cm[0])+sum(cm[1]))


#MCC=(TP*TN)-(FP*FN)/sqrt((TP+FP)*(TN+FN)*(TN+FP)*(TN+FN))
#is is more infomrative beacuse not affected by dataset unbalance
def mcc(cm):
  d=(cm[0][0]+cm[1][0])*(cm[0][0]+cm[0][1])*(cm[1][1]+cm[1][0])*(cm[1][1]+cm[0][1])
  return (cm[0][0]*cm[1][1]-cm[0][1]*cm[1][0])/math.sqrt(d)

if __name__=="__main__":
    filename=sys.argv[1]
    #th=float(sys.argv[2])
    data=get_blast(filename)
    for i in range(20):
        th=10**-i
        cm=get_cm(data,th)
        print("TH:", th,"ACC: ",get_acc(cm),"MCC: ",mcc(cm), cm)
```
