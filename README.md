# MariaClust

### Validation results

#### Jain
* python mariaClust.py jain.txt 2 3 0.8 2
	* ('Purity:  ', 0.0)
	* ('Entropy: ', 0.0)
	* ('RI       ', 1.0)
	* ('ARI      ', 1.0)


### Run parameters:
* filename of the dataset
* no_clusters
* no_bins
* expand_factor - given a center, how much a cluster can expand based on the number of neighbours
* how to compute the inter cluster dinstances:
	* 1 = centroid linkage
	* 2 = average linkage
	* 3 = single linkage
	* 4 = average linkage ponderat

Run example: python3 mariaClust.py aggregation.txt 7 8 1 1

-------------------------------------------------------------------------------------------------

## Datasets:

### Aggregation
* Aggregation details: 
	* No. Elements: 788
	* No. Dimensions: 2
	* No. Clusters: 7
	* No. Bins: 8
	* Expand Factor: 1 
	* Dinstance Type: 1 (centroid)
* run:
	* python3 src/mariaClust.py datasets/aggregation.txt 7 8 1 1
* article:
	* A. Gionis, H. Mannila, and P. Tsaparas, Clustering aggregation. ACM Transactions on Knowledge Discovery from Data (TKDD), 2007. 1(1): p. 1-30.

### Spiral
* Spiral details: 
	* No. Elements: 312
	* No. Dimensions: 2
	* No. Clusters: 3
	* No. Bins: 3
	* Expand Factor: 1.8 
	* Dinstance Type: 3 (single linkage)
* run:
	* python3 src/mariaClust.py datasets/spiral.txt 3 3 1.8 3
* article:
	* H. Chang and D.Y. Yeung, Robust path-based spectral clustering. Pattern Recognition, 2008. 41(1): p. 191-203. 

### R15
* R15 details: 
	* No. Elements: 600
	* No. Dimensions: 2
	* No. Clusters: 15
	* No. Bins: 8
	* Expand Factor: 1
	* Dinstance Type: 1 (centroid)
* run:
	* python3 src/mariaClust.py datasets/r15.txt 15 8 1 1
* article:
	* C.J. Veenman, M.J.T. Reinders, and E. Backer, A maximum variance cluster algorithm. IEEE Trans. Pattern Analysis and Machine Intelligence, 2002. 24(9): p. 1273-1280. 

### Jain
* Jain details: 
	* No. Elements: 373
	* No. Dimensions: 2
	* No. Clusters: 2
	* No. Bins: 3
	* Expand Factor: 0.8
	* Dinstance Type: 2 (average linkage)
* run:
	* python3 src/mariaClust.py datasets/jain.txt 2 3 0.8 2
* article:
	* A. Jain and M. Law, Data clustering: A user's dilemma. Lecture Notes in Computer Science, 2005. 3776: p. 1-10. 

### Pathbased
* Pathbased details: 
	* No. Elements: 300
	* No. Dimensions: 2
	* No. Clusters: 3
	* No. Bins: 2
	* Expand Factor: 1.8
	* Dinstance Type: 2 (average linkage)
* run:
	* python3 src/mariaClust.py datasets/pathbased.txt 3 2 1.8 2
* article:
	* H. Chang and D.Y. Yeung, Robust path-based spectral clustering. Pattern Recognition, 2008. 41(1): p. 191-203. 

### Flame
* Flame details:
	* No. Elements: 240
	* No. Dimensions: 2
	* No. Clusters: 2
* article:
	* L. Fu and E. Medico, FLAME, a novel fuzzy clustering method for the analysis of DNA microarray data. BMC bioinformatics, 2007. 8(1): p. 3. 

### D31
* D31 details:
	* No. Elements: 3100
	* No. Dimensions: 2
	* No. Clusters: 31
* article:
	* C.J. Veenman, M.J.T. Reinders, and E. Backer, A maximum variance cluster algorithm. IEEE Trans. Pattern Analysis and Machine Intelligence 2002. 24(9): p. 1273-1280. 

### Compound
* Compound details:
	* No. Elements: 399
	* No. Dimensions: 6
	* No. Clusters: 2
* article:
	* C.T. Zahn, Graph-theoretical methods for detecting and describing gestalt clusters. IEEE Transactions on Computers, 1971. 100(1): p. 68-86. 

