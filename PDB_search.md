# Project workflow - PDB search part
First of all, we select from PDB the structures containging the Kunitz domain using the advanced search. In the query of the search we insert:
* containing Pfam BPTI-Kunitz identifier: PF00014;
* number of polymer residues less then 100;
* resolution less than or equal to 3.5 A.

The search retrieve 39 results. Now we have to check if they effectively contain the Kunitz domain. Before checking, let's download the 39 PDB entries in `.cvs` format, specifing sequence. The downloaded file must be modified in order to have more readble results.
Indeed, we want to have a `fasta` format of the protein sequences retrieved from PDB.

`>1BTI:A`

`RPDFCLEPPYTGPCKARIIRYAYNAKAGLCQTFVYGGCRAKRNNFKSAEDCMRTCGGA`

