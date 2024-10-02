# sfa_flooring
This repository provides the code related to the publication "Increasing the recycling of PVC flooring requires phthalate removal for ensuring consumers’ safety: A cross-checked substance flow analysis of plasticizers for Switzerland" authored by M. Klotz, S. Schmidt, H. Wiesinger, D. Laner, Z. Wang and S. Hellweg, DOI: 10.1021/acs.est.4c04164.



Steps to conduct Material and Substance Flow Analyses (MFA and SFA) with the model provided:

1. define the system(s) that you want to assess in the 'tables' Excel workbook (for our paper, this corresponds to all sheets from 'system' to 'comp_ch_pve' from the SI2 file)
2. install all necessary packages (that are imported in the different scripts)
3. run main to read in the data from the Excel file 'tables', store it in a database, and from this create the instances of the System class of those systems that you defined in the 'tables' file and want to assess
4. using the different functions of the System instances (defined in System class), you can calculate and plot your material and substance flows and do balance checks
