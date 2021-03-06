# Project workflow - training on real data (professor version)
* select proteins with Kunitz domain in UniProtKB using the advanced search (`database:(type:pfam pf00014) AND reviewed:yes`): retreived 359 proteins. These proteins represent the **positive set**. Modify the file in order to have in the header only the sequence ID: `awk '{if (substr($0,1,1)==">") {split($0,a,"|"); print ">"a[2]} else {print $0}}' bpti_Kunitz.fasta > clean_all_bpti_Kunitz.fasta`
* select proteins without Kunitz domain. In the project we must use alll proteins not containing the Kuntiz domain, but in this case, we are going to use the set of non-Kunitz human proteins (20347). These proteins represent the **negative set**;
* as already done, split the negative set into **training** and **testing**. Modify the files in order to have only in the header only the sequence ID: `awk '{if (substr($0,1,1)==">") {split($0,a,"|"); print ">"a[2]} else {print $0}}' Human_NotPF00014_Training.fasta > negative_set1.txt` and `awk '{if (substr($0,1,1)==">") {split($0,a,"|"); print ">"a[2]} else {print $0}}' Human_NotPF00014_Testing.fasta > negative_set2.txt`
* **two-fold cross validation** : _setting k = 2 results in 2-fold cross-validation. In 2-fold cross-validation, we randomly shuffle the dataset into two sets d0 and d1, so that both sets are equal size (this is usually implemented by shuffling the data array and then splitting it in two). We then train on d0 and validate on d1, followed by training on d1 and validating on d0._ 
* remove from the positive set the sequences prevoiusly used to create the HMM: (1) create the database of the sequences used for the HMM: `formatdb -i clean_setmine.fasta -p` (2) BLAST the positive set against the such created databse: `blastpgp -i clean_all_bpti_Kunitz.fasta -d clean_setmine.fasta -m 8 -e 0.001 -o clean_all_bpti_Kunitz.bl8` (3) create a list containing the IDs of the sequence having 100% sequence similariry (`awk '{if ($3==100) print $1}' clean_all_bpti_Kunitz.bl8 | sort -u > redundant_set.txt`) (4) using the `extract_seq.py` python program, create a file containing all sequences containg Kunitz domain from UniProt, except the ones in the `reduntant.txt` file (`./extract_seq.py redundant_set.txt clean_all_bpti_Kunitz.fasta > nr_all_bpti_Kunitz.fasta`)
* obtain true positives and false negatives: (1) from the positive set extract all ID and sort them randomly (`grep ">" nr_all_bpti_Kunitz.fasta | sed 's/>//' | sort -R > random1.txt`) (2) divide the non-redundant set of 354 proteins in two set of 177 proteins (`head -n 177 random1.txt > set_r1_id1.txt` and `tail -n +178 random1.txt > set_r1_id2.txt`) (3) extract the sequences using the prevoius python program for both the files (`./extract_seq.py set_r1_id1.txt nr_all_bpti_Kunitz.fasta > positive_set1.txt` and `./extract_seq.py set_r1_id2.txt nr_all_bpti_Kunitz.fasta > positive_set2.txt`) (4) compare the two set of positives with the HMM to see the probability of association of each sequence to the model (`hmmsearch -Z 1 --noali --max --tblout positive_set1.hits bpti-kunitz.hmm positive_set1.txt`) (5) create the file with three columns referring to the ID, the e-valu of the best domain and the class value 1(`grep -v "^#" positive_set1.hits | awk '{print $1,$8,1}' > positive_set1.out`)
* obtain flase posiitves and true negatives: (1) compare the two set of positives with the HMM to see the probability of association of each sequence to the model (`hmmsearch -Z 1 --noali --max --tblout negative_set1.hits bpti-kunitz.hmm negative_set1.txt`) (2) reate the file with three columns referring to the ID, the e-valu of the best domain and the class value 0 (`grep -v "^#" negative_set1.hits | awk '{print $1,$8,0}' > negative_set1.out`) (3) pick from the file with 10000 sequences the 9982 sequences that have been ignored by hmmsearch and give them a e-value of 10 and 0 in the third column (`comm <(grep "^>" negative_set1.txt | sed 's/>//' | sort) <(awk '{print $1}' negative_set1.out | sort) | awk -F '\t' '{if ($1!="") print $1,10,0}' > restore_set1.out`) (4) put together the 18 sequences taken from hmmsearch and the 9882 sequences ignored (`cat negative_set1.out restore_set1.out > ok_negative_set1.out`) 
* calculate the **confusion matrix** with the `performance.py` python script (`./performance.py <(cat positive_set1.out ok_negative_set1.out)`). 
true positives: the fraction of 177 sequences in `positive_set1.out` with an E-value lower than the threshold
false negatives: the fraction of 177 sequences in `positive_set1.out` with an E-value higher than the threshold
false positives: the fraction of the 10000 sequences of the `ok_negative_set1.out` with an E-values lower than the threshold
true negatives: the fraction of the 10000 sequences of the `ok_negative_set1.out` with an E-values higher than the threshold

|               | Set of positives | Set of negatives  |
| ------------- |:---------------: |------------------:|
| positives     | true positives   | false positives   |
| negatives     | false negatives  | true negatives    |
|               | 177              |     10000         |

READ_ME: -Z 1 options allow to normalize the E-value in the hmmsearch.

* run the `perfomrance.py` script with the postive_set1 and the ok_negative_set1:

`TH: 1e-05 ACC:  1.0 MCC:  1.0 [[177.0, 0.0], [0.0, 10000.0]]
TH: 1e-06 ACC:  1.0 MCC:  1.0 [[177.0, 0.0], [0.0, 10000.0]]
TH: 1e-07 ACC:  1.0 MCC:  1.0 [[177.0, 0.0], [0.0, 10000.0]]
TH: 1e-08 ACC:  1.0 MCC:  1.0 [[177.0, 0.0], [0.0, 10000.0]]
TH: 1e-09 ACC:  1.0 MCC:  1.0 [[177.0, 0.0], [0.0, 10000.0]]
TH: 1e-10 ACC:  1.0 MCC:  1.0 [[177.0, 0.0], [0.0, 10000.0]]
`

