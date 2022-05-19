Open-source Distributed Energy Resources (OpenDER) Model
========================================================
EPRI’s OpenDER is an open-source Distributed Energy Resource (DER) model that aims to accurately represent 
steady-state and dynamic behaviors of DERs following interconnection standards or grid-codes and commercial 
products. The first version models DER behaviors according to the capabilities and functionalities required 
by the IEEE standard 1547-2018. This model can be used to run snapshot, Quasi-Static Time Series (QSTS), and 
dynamic analyses to study impacts of DERs on distribution circuits and potential benefits of smart inverter 
grid support functions. 

..contents::

OpenDER is under active development
----------------------------------- 
Use the following resources to get involved.

* Model specification: IEEE 1547-2018 DER Model: Version 1.0, EPRI, Palo Alto, CA: 2021. 3002021694 (`link <https://www.epri.com/research/products/000000003002021694>`_)

* EPRI OpenDER page (`link <https://www.epri.com/>`_)

Development Objective
---------------------
* Harmonize accurate understanding of IEEE Std 1547-2018TM DER interconnection standard among all stakeholders, including utilities, distribution analysis tool developers, and original equipment manufacturers (OEMs).

* Build consensus through an open-to-all DER Model Users Group (DERMUG), which will utilize model specifications and codes and provide feedback to EPRI for continuous improvement of the OpenDER model
* Help the industry to accurately model the DERs being installed in the field and evaluate impacts on the distribution circuit.
  
Requirements
------------
Python >= 3.7

Dependencies
------------
numpy
pandas
matplotlib

Dependencies of the package are auto-installed by pip command below. 

Installation
------------
pip install path-to-package\opender-1.0.0-py3-none-any.whl

PyPI release to be available soon.

Example of Using the DER Model
------------------------------ 
This example generate DER output power in a dynamic simulation to demonstrate DER trip and enter service behavior.\
The grid voltage is set to be alternating between 1 and 1.11 per unit every ~10 minutes. \
DER should be observed to enter service and trip periodically.\

To run the example script: main.py
Please ensure python PATH is set in the environment variables before running the batch file

Unit tests
----------
Dependency: pytest

Execution command: pytest path-to-package\\tests


