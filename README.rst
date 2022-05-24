Open-source Distributed Energy Resources (OpenDER) Model
========================================================
EPRI's OpenDER model aims to properly represent steady-state and dynamic behavior of DERs The model follows
interconnection standards or grid-codes and are informed by the observed behavior of commercial products.
The first version models photovoltaic (PV) DER behavior according to the capabilities and functionalities
required by the IEEE standard 1547-2018 :superscript:`TM` . This model can be used to run snapshot, Quasi-Static Time Series (QSTS),
and a variety of dynamic analyses to study the impacts of DERs on distribution operation and planning.

This project is licensed under the terms of the BSD-3 clause license.

|GitHub license|

.. |GitHub license| image:: https://img.shields.io/badge/License-BSD_3--Clause-blue.svg
   :target: https://github.com/epri-dev/opender/blob/master/LICENSE.txt


Resources
---------
OpenDER is under active development. Use the following resources to get involved.

* Model specification: IEEE 1547-2018 DER Model: Version 1.0, EPRI, Palo Alto, CA: 2021. 3002021694
  (`link <https://www.epri.com/research/products/000000003002021694>`_)

* EPRI OpenDER page (`link <https://www.epri.com/pages/sa/opender>`_ to be available)

* Readthedocs documentations (`link <https://opender.readthedocs.io/>`_)

Development Objective
---------------------
* Harmonize accurate interpretations of IEEE Std 1547-2018TM DER interconnection standard among stakeholders,
  including utilities, distribution analysis tool developers, and original equipment manufacturers (OEMs).

* Build consensus through an open-to-all DER Model Users Group (DERMUG), which will utilize the developed
  model specifications and codes and provide feedbacks for continuous improvement of the OpenDER model

* Help the industry to properly model the DERs that are (or to be) interconnected and evaluate the impacts
  on the distribution circuit.

Overall Block Diagram
---------------------
.. figure:: https://github.com/epri-dev/OpenDER/blob/main/docs/blockdiagram.png
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
pip install path-to-package\\opender-1.0.0-py3-none-any.whl

PyPI release to be available soon.

Example of Using the DER Model
------------------------------
This example generate DER output power in a dynamic simulation to demonstrate DER trip and enter service behavior.

The grid voltage is set to be alternating between 1 and 1.11 per unit every ~10 minutes.

DER should be observed to enter service and trip periodically.

To run the example script: main.py

Please ensure python PATH is set in the environment variables before running the batch file

Unit tests
----------
Dependency: pytest

Execution command: pytest path-to-package\\tests


