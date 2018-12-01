.. IEXTools documentation master file, created by
   sphinx-quickstart on Sat Dec  1 14:53:29 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

IEXTools Documentation
====================================

This package provides tools for working with data provided by IEX's REST API and tools to decode and use IEX's binary market data (dubbed "HIST"). For more information on the type of data offered by IEX please visit their website: https://iextrading.com/developer/docs and https://iextrading.com/trading/market-data/

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   webapi
   datadownloader
   parser

Installation
============
**Note: both of these installation methods will fail without Python 3.7 or greater.**

Install from PyPI:

``$ py -m pip install IEXTools``

OR

Navigate to the folder containing the README.md file and run the pip command to install the package:

``$ pip install .``

Requirements
------------

- Python 3.7 or greater
- requests


Indices and tables
==================
 
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
