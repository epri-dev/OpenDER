.. figure:: https://raw.githubusercontent.com/epri-dev/OpenDER/develop_req_SQA/docs/logo.png
    :alt: Open-source Distributed Energy Resources (OpenDER) Model

EPRI’s OpenDER model aims to accurately represent steady-state and dynamic behaviors of inverter-based distributed
energy resources (DERs). The model follows interconnection standards or grid-codes and is informed by the observed
behaviors of commercial products. Currently, model version 2.0 includes photovoltaic (PV) and battery energy storage
system (BESS) DER behaviors according to the capabilities and functionalities required by the IEEE standard 1547-2018.
This first-of-its-kind model can be used to run snapshot, Quasi-Static Time Series (QSTS), and a variety of dynamic
analyses to study the impacts of DERs on distribution operations and planning.

This project is licensed under the terms of the BSD-3 clause license.


.. |GitHub license| image:: https://img.shields.io/badge/License-BSD_3--Clause-blue.svg
   :target: https://github.com/epri-dev/opender/blob/master/LICENSE.txt

Resources
---------
OpenDER is under active development. Use the following resources to get involved.

* EPRI OpenDER homepage (`link <https://www.epri.com/OpenDER>`__)

* Model specification: IEEE 1547-2018 OpenDER Model: Version 2.0, EPRI, Palo Alto, CA: 2022. 3002025583
  (`link <https://www.epri.com/research/products/000000003002025583>`__)

Development Objective
---------------------
* Harmonize accurate interpretations of the IEEE Std 1547-2018 DER interconnection standard among all the stakeholders,
  including utilities, distribution analysis tool developers, and original equipment manufacturers (OEMs).

* Build consensus through an open-to-all DER Model User’s Group (DERMUG), which will utilize EPRI developed model
  specifications and codes and provide feedback for continuous improvement of the OpenDER model.

* Help the industry properly model the DERs that are (or to be) grid interconnected and evaluate the associated impacts
  on distribution circuits accurately.

Overall Block Diagram
---------------------
.. figure:: https://raw.githubusercontent.com/epri-dev/OpenDER/develop_req_SQA/docs/blockdiagram.png
    :width: 900

Dependencies
------------
Python >= 3.7

numpy

pandas

matplotlib

Dependencies of the package are auto-installed by pip command below.

Installation
------------
pip install opender


Example of Using the DER Model
------------------------------
Example script: main.py

This example generate DER output power in a dynamic simulation to demonstrate DER trip and enter service behavior.

The grid voltage is set to be alternating between 1 and 1.11 per unit every ~10 minutes.

DER should be observed to enter service and trip periodically.

Please ensure python PATH is set in the environment variables before running the batch file

Unit tests
----------
Dependency: pytest

Execution command: pytest path-to-package\\tests


