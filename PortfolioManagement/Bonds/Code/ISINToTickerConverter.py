from typing import List

import requests
from env import env

openfigi_apikey = ""  # Put API Key here


class ISINToTickerConverter:
    def __init__(self):
        self.__env = env()

    def __map_jobs(self, jobs: List[dict]):
        """
        Send an collection of mapping jobs to the API in order to obtain the
        associated FIGI(s).
        Parameters
        ----------
        jobs : list(dict)
            A list of dicts that conform to the OpenFIGI API request structure. See
            https://www.openfigi.com/api#request-format for more information. Note
            rate-limiting requirements when considering length of `jobs`.
        Returns
        -------
        list(dict)
            One dict per item in `jobs` list that conform to the OpenFIGI API
            response structure.  See https://www.openfigi.com/api#response-fomats
            for more information.
        """
        openfigi_url = "https://api.openfigi.com/v1/mapping"
        openfigi_headers = {"Content-Type": "text/json"}
        openfigi_apikey = self.__env.figiApiKey
        if openfigi_apikey:
            openfigi_headers["X-OPENFIGI-APIKEY"] = openfigi_apikey
        response = requests.post(url=openfigi_url, headers=openfigi_headers, json=jobs)
        if response.status_code != 200:
            raise Exception("Bad response code {}".format(str(response.status_code)))
        return response.json()

    def getTickerForISIN(self, isin: str) -> str:
        """This function accepts an isin and returns a possible ticker for this isin"""
        jobs = [
            {"idType": "ID_ISIN", "idValue": f"{isin}", "exchCode": "US"},
        ]
        response = self.__map_jobs(jobs)
        try:
            ticker = response[0]["data"][0]["ticker"]
        except:
            print(response)
            print("no ticker could be found for " + isin)
            ticker = "n/a"
        return ticker

    def getAllTickerForISIN(self, isin: str) -> set[str]:
        """This function accepts an isin and returns a list of possible tickers for this isin"""
        jobs = [
            {"idType": "ID_ISIN", "idValue": f"{isin}"},
        ]
        response = self.__map_jobs(jobs)
        try:
            return set(map(lambda ticker: (ticker["ticker"]), response[0]["data"]))
        except:
            return set()


isinConverter = ISINToTickerConverter()
# print(isinConverter.getTickerForISIN("IE00B0M63623"))
isinConverter.getAllTickerForISIN("IE00B0M63623")
