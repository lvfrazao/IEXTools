"""
This module defines the DataDownloader class which finds and downloads the IEX
HIST files that the user requests. If the file cannot be found an exception is
raised.

IEX offers their HIST TOPS and DEEP binary data files on their website. The URL
where these files are located can be retrieved from the IEX web API.
"""
from datetime import datetime
import os
import sys
from . import IEXHISTExceptions
import requests
import gzip
import shutil
from typing import Dict


class DataDownloader(object):
    def __init__(self) -> None:
        """
        Initiate the class with the IEX API endpoint information and
        initializes the folder to put the downloaded data into.
        """
        self.base_endpoint = "https://api.iextrading.com/1.0/"

        if sys.argv[0]:
            os.chdir(os.path.dirname(sys.argv[0]))

        self.directory = "IEX_data"
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def _get_endpoint(self, date: datetime) -> str:
        """
        Constructs the IEX API endpoint that provides the download link for the
        HIST data of a given date.

        Inputs:

            date    : date of HIST data being requested

        Returns:

            endpoint    : URL of IEX API endpoint to send GET request to
        """
        yyyy = date.year
        mm = str(date.month).zfill(2)
        dd = str(date.day).zfill(2)
        date_str = f"{yyyy}{mm}{dd}"
        endpoint = f"{self.base_endpoint}/hist?date={date_str}"
        return endpoint

    def _get_download_link(self, date: datetime) -> Dict[str, Dict[str, str]]:
        """
        Extract the download URL and filename from the IEX API for the
        requested HIST file.

        Inputs:

            date    : date of HIST data being requested

        Returns:

            links   : contains URL and name of desired file
        """
        endpoint = self._get_endpoint(date)
        response = requests.get(endpoint)
        try:
            response.raise_for_status()
        except requests.RequestException as e:
            raise IEXHISTExceptions.RequestsException(e.args)

        links: Dict[str, Dict[str, str]] = {}
        for entry in response.json():
            links[entry["feed"]] = {
                "url": entry["link"],
                "file": (
                    f'{entry["date"]}_{entry["protocol"]}_{entry["feed"]}'
                    f'{entry["version"]}.pcap.gz'
                ),
            }

        return links

    def download(self, date: datetime, feed_type: str) -> str:
        """
        Downloads the pcap file (either TOPS or DEEP) for a given date and
        returns the filename.

        Inputs:

            date        : date of desired HIST file
            feed_type   : type of feed file requested (either TOPS or HIST)
        
        Returns:

            file_name   : name of downloaded file
        """
        feed_type = feed_type.upper()
        if feed_type not in ["TOPS", "DEEP"]:
            raise IEXHISTExceptions.IEXHISTException(
                "feed_type must be either TOPS or DEEP"
            )

        link_info = self._get_download_link(date)
        url = link_info[feed_type]["url"]
        filename = link_info[feed_type]["file"]
        response = requests.get(url, stream=True)
        try:
            response.raise_for_status()
        except requests.RequestException as e:
            raise IEXHISTExceptions.RequestsException(e.args)

        file_in = os.path.join(self.directory, filename)
        with open(file_in, "wb") as data_file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    data_file.write(chunk)

        return filename

    def decompress(
        self, file_in: str, file_out: str, remove_source: bool = False
    ) -> None:
        """
        Decompress the gziped HIST files that were downloaded.

        Inputs:

            file_in     : file name that needs to be unzipped
            file_out    : file name of the decompressed file
            remove_src  : option to delete the compressed file
        """
        with gzip.open(file_in, "rb") as f_in:
            with open(file_out, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        if remove_source:
            os.remove(file_in)

    def download_decompressed(self, date: datetime, feed_type: str) -> str:
        """
        Single method to both download the gziped pcap file, but also
        decompress it and return the filename of the decompressed pcap file.

        Inputs:

            date        : date of desired HIST file
            feed_type   : type of feed file requested (either TOPS or HIST)
        
        Returns:

            file_name   : name of downloaded file
        """
        file_name = self.download(date, feed_type)
        file_in = os.path.join(self.directory, file_name)
        file_out = os.path.join(self.directory, file_name.replace(".gz", ""))
        self.decompress(file_in, file_out, remove_source=True)
        return file_name.replace(".gz", "")
