fMRIQA_v2_0_1
=============

* **What does it do?**
For each fMRI series, the brain is identified by thresholding the mean image—averaged over all volumes—at its antimode (Luo 2003, http://www-personal.umich.edu/~nichols/PCT/). Voxel values are then converted to percent of the in-brain global mean. All quality metrics are computed on in-brain voxels, using the raw images prior to any other processing. Specifically, rigid body registration is not used except to compute voxel displacements.

This version also allows for removal of phase data which may be acquired along with magnitude. Everything else is the same

* **Current Contact Person**
<2016-08-15> <Baxter Rogers> <baxter.rogers@vanderbilt.edu> 

* **Software Requirements**
| fMRI data in NIfTI format. PAR header associated with the fMRI data. Task or resting state.
| Matlab R2013a >
| SPM12 or >

* **Off-line Compliance**
Not compliant, uses XnatUtils.download_Scan with no offline flag

* **Data Requirements**
fMRIQA NIfTI files

* **Resources** *
| OUTLOG - STDOUT and STDERR from the process on the grid
| PBS - The DRMAA compliant batch script to run the job
| PDF - The output PDF file for determining QA status
| SNAPSHOTS - Thumbnail of the first page of the PDF resource for viewing on XNAT
| STATS
| MATLAB

* **References**
1. Luo WL, Nichols TE. Diagnosis and exploration of massively univariate neuroimaging models.Neuroimage. 2003 19(3):1014-32. PMID: 12880829.
2. Mowinckel AM, Espeseth T, Westlye LT. Network-specific effects of age and in-scanner subject motion: a resting-state fMRI study of 238 healthy adults. Neuroimage. 2012 63(3):1364-73. PMID:22992492.
3. Power JD, Barnes KA, Snyder AZ, Schlaggar BL, Petersen SE. Spurious but systematic correlations in functional connectivity MRI networks arise from subject motion. Neuroimage. 2012 59(3):2142-54.PMID: 22019881; PMCID: PMC3254728.
4. Smyser CD, Snyder AZ, Neil JJ. Functional connectivity MRI in infants: exploration of the functional organization of the developing brain. Neuroimage. 2011 56(3):1437-52. PMID: 21376813; PMCID: PMC3089442.

* **Version History**
<revision> <name> <date> <lines changed>

r4190 | blaberj | 2016-02-04 10:16:22 -0600 (Thu, 04 Feb 2016) | 1 line
	added justin's version of probtrack spider
r4042 | damons | 2015-12-22 14:07:50 -0600 (Tue, 22 Dec 2015) | 1 line
	spider to fix Todd Monore's data



	
	
