<p align="center">
  <a href="http://compmedchem.unibo.it/covidrugnet">
    <img src="https://raw.githubusercontent.com/LucaMenestrina/COVIDrugNet/master/data/imgs/social_image.svg" alt="COVIDrugNet: Collect and visualize network info about drugs and targets related to COVID-19"/>
  </a>
</p>

The COVID-19 pandemic poses a huge problem of public health that requires the implementation of all available means to contrast it, and drugs are one of them. In this context, we observed an unmet need of depicting the continuously evolving scenario of the ongoing drug clinical trials through an easy-to-use, freely accessible online tool. Starting from this consideration, we developed [**COVIDrugNet**](http://compmedchem.unibo.it/covidrugnet), a web application that allows users to capture a holistic view and keep up to date on how the clinical drug research is responding to the SARS-CoV-2 infection.

In [our article](https://www.nature.com/articles/s41598-021-98812-0), we describe the web app and show through some examples how one can explore the whole landscape of medicines in clinical trial for the treatment of COVID-19 and try to probe the consistency of the current approaches with the available biological and pharmacological evidence. We conclude that careful analyses of the COVID-19 drug-target system based on COVIDrugNet can help to understand the biological implications of the proposed drug options, and eventually improve the search for more effective therapies.

### Updates  

Last Database Update: 19th October 2022  (No changes since 17th May 2022)  
Analyses Update:      19th October 2022  (No changes since 17th May 2022)  

### Cite

Please cite [our paper](https://www.nature.com/articles/s41598-021-98812-0) (and the respective papers of the methods used) if you use *COVIDrugNet* in your own work:

```
@article {Menestrina2021,
	 title = {COVIDrugNet: a network-based web tool to investigate the drugs currently in clinical trial to contrast COVID-19},
	 author = {Menestrina, Luca and Cabrelle, Chiara and Recanatini, Maurizio},
	 journal = {Scientific Reports},
	 volume = {11},
	 year = {2021},
	 doi = {10.1038/s41598-021-98812-0},
	 URL = {www.nature.com/articles/s41598-021-98812-0},
	 publisher = {Nature Publishing Group},
}
```

### Data Sources

- [DrugBank](https://go.drugbank.com/)
- [STRING](https://string-db.org/)
- [DisGeNET](https://www.disgenet.org/)
- [SWISS-MODEL](https://swissmodel.expasy.org/)
- [RCSB PDB](https://www.rcsb.org/)
- [UniProt](https://www.uniprot.org/)
- [ChEMBL](https://www.ebi.ac.uk/chembl/)
- [Gordon et al. Virus-Host interactome](https://doi.org/10.1038/s41586-020-2286-9)
- [Chen et al. Virus-Host interactome](http://127.0.0.1:8050/covidrugnet/10.1101/2020.12.31.424961)

#### DisGeNET Authentication Note
Since June 2021 authentication is required for retrieving data from DisGeNET.  
In order to use COVIDrugNet locally it is required to provide the DisGeNET credentials, otherwise it will not collect gene-disease associations.  
COVIDrugNet supports both environmental variables and .env files (keys: DISGENET_EMAIL, DISGENET_PASSWORD).  
Please set them before running COVIDrugNet on your machine.  

### Browser compatibility
The website has been tested on the following browsers and OSs:

|             | Google Chrome | Firefox | Safari | Microsoft Edge |
|-------------|-------|--------|---------|---------|
| **Linux**   | ✅    | ✅     | ?      | ?     |
| **Windows** | ✅    | ✅     | ?      | ✅      |
| **macOS**   | ✅    | ✅       | ✅        | ?        |


### Dependencies

COVIDrugNet is entirely written in Python 3 and would not be possible without the following packages:

- [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/)
- [chembl_webresource_client](https://github.com/chembl/chembl_webresource_client)
- [dash](https://plotly.com/dash/)
- [dash_bootstrap_components](https://dash-bootstrap-components.opensource.faculty.ai/)
- [dash_core_components](https://dash.plotly.com/dash-core-components)
- [dash_cytoscape](https://dash.plotly.com/cytoscape)
- [dash_daq](https://dash.plotly.com/dash-daq)
- [dash_html_components](https://dash.plotly.com/dash-html-components)
- [dash_table](https://github.com/plotly/dash-table)
- [matplotlib](https://matplotlib.org/)
- [networkx](https://networkx.org/)
- [numpy](https://numpy.org/)
- [pandas](https://pandas.pydata.org/)
- [plotly](https://plotly.com/)
- [powerlaw](https://github.com/jeffalstott/powerlaw)
- [PubChemPy](https://pubchempy.readthedocs.io/)
- [pygraphviz](https://pygraphviz.github.io/)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [scikit](https://scikit-learn.org/)
- [scipy](https://www.scipy.org/)
- [rdkit](https://www.rdkit.org/)
- [requests](https://requests.readthedocs.io/en/master/)
- [tqdm](https://github.com/tqdm/tqdm)
- [visdcc](https://github.com/jimmybow/visdcc)
