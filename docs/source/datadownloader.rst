Data Downloader
===============

Usage
-----

Purpose: Download IEX's pcap files containing nanosecond precision stock data - the so called HIST files.

The `DataDownloader` class can be instantiated without any arguments by simply calling the class.

``d1 = IEXTools.DataDownloader()``

There are three available methods in this class::

   >>> print([method for method in dir(IEXTools.DataDownloader) if not method.startswith('_')])
   
   ['decompress', 'download', 'download_decompressed']

- download: Downloads the gziped TOPS or DEEP file for a given datetime input
- decompress: Unzips the compressed HIST file into a pcap
- download_decompressed: downloads and decompresses the HIST file - deletes the zipped file at the end

**Warning, IEX HIST files are generally very large (multiple gbs)**

Usage::

   >>> import IEXTools
   >>> from datetime import datetime
   >>> d1 = IEXTools.DataDownloader()
   >>> d1.download_decompressed(datetime(2018, 7, 13), feed_type='tops')
   '20180713_IEXTP1_TOPS1.6.pcap'

Module Docs
-----------

.. automodule:: IEXTools.IEXDownloader
   :members:

.. autoclass:: DataDownloader
    :members:

Indices and tables
------------------
 
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
