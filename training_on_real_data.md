# Project workflow - training on real data (professor version)
* select proteins with Kunitz domain in UniProtKB using the advanced search (`database:(type:pfam pf00014) AND reviewed:yes`): retreived 359 proteins. These proteins represent the **positive set**;
* select proteins without Kunitz domain. In the project we must use alll proteins not containing the Kuntiz domain, but in this case, we are going to use the set of non-Kunitz human proteins (20347). These proteins represent the **negative set**;
* as already done, split the negative set into **training** and **testing**;
* **two-fold cross validation** : setting k = 2 results in 2-fold cross-validation. In 2-fold cross-validation, we randomly shuffle the dataset into two sets d0 and d1, so that both sets are equal size (this is usually implemented by shuffling the data array and then splitting it in two). We then train on d0 and validate on d1, followed by training on d1 and validating on d0. 
