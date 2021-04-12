<p align="center">
  <a href="http://compmedchem.unibo.it/covidrugnet">
    <img src="https://raw.githubusercontent.com/LucaMenestrina/COVIDrugNet/master/data/imgs/social_image.svg" alt="COVIDrugNet: Collect and visualize network info about drugs and targets related to COVID-19"/>
  </a>
</p>

The COVID-19 pandemic poses a huge problem of public health that requires the implementation of all available means to contrast it, and drugs are one of them. In this context, we observed an unmet need of depicting the continuously evolving scenario of the ongoing drug clinical trials through an easy-to-use, freely accessible online tool. Starting from this consideration, we developed [**COVIDrugNet**](http://compmedchem.unibo.it/covidrugnet), a web application that allows users to capture a holistic view and keep up to date on how the clinical drug research is responding to the SARS-CoV-2 infection.

In [our article](https://www.biorxiv.org/content/early/2021/03/09/2021.03.05.433897), we describe the web app and show through some examples how one can explore the whole landscape of medicines in clinical trial for the treatment of COVID-19 and try to probe the consistency of the current approaches with the available biological and pharmacological evidence. We conclude that careful analyses of the COVID-19 drug-target system based on COVIDrugNet can help to understand the biological implications of the proposed drug options, and eventually improve the search for more effective therapies.

### Updates  

Last Database Update: 12th April 2021  
Analyses Update:      12th April 2021

### Cite

Please cite [our paper](https://www.biorxiv.org/content/early/2021/03/09/2021.03.05.433897) (and the respective papers of the methods used) if you use *COVIDrugNet* in your own work:

```
@article {Menestrina2021.03.05.433897,
	 title = {COVIDrugNet: a network-based web tool to investigate the drugs currently in clinical trial to contrast COVID-19},
	 author = {Menestrina, Luca and Cabrelle, Chiara and Recanatini, Maurizio},
	 journal = {bioRxiv}
	 year = {2021},
	 doi = {10.1101/2021.03.05.433897},
	 URL = {https://www.biorxiv.org/content/early/2021/03/09/2021.03.05.433897},
	 publisher = {Cold Spring Harbor Laboratory},
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
- [scikit](https://scikit-learn.org/)
- [scipy](https://www.scipy.org/)
- [rdkit](https://www.rdkit.org/)
- [requests](https://requests.readthedocs.io/en/master/)
- [tqdm](https://github.com/tqdm/tqdm)
- [visdcc](https://github.com/jimmybow/visdcc)
