# TODO: APIError handling

import os
from json import load

import requests


class Bea:
    methods = ["GetData",
               "GetDatasetList",
               "GetParameterList",
               "GetParameterValues",
               "GetParameterValuesFiltered"]

    # Load config file
    dataset_args_filename = "datasets_args.json"
    dataset_args_filepath = os.path.join(os.path.dirname(__file__), dataset_args_filename)
    with open(dataset_args_filepath, "r") as file:
        datasets_args = load(file)

    def __init__(self):
        self.__api_token = os.environ["BEA_API_KEY"]
        self.__query_params = {
            "UserID": self.__api_token,
            "method": "GetData",
            "ResultFormat": "json",
        }
        self.__origin_url = "https://apps.bea.gov/api/data"
        self.request_session = requests.Session()

    def __validate_inputs(self, params):
        # TODO: Custom logic for MNE Dataset
        # TODO: Validate param values

        # Overwrite default query params with user-supplied params
        query_params = self.__query_params
        for param in params:
            query_params[param] = params[param]
        return query_params

    def __compose_full_url(self, path=None):
        # Creating this method just in case the implementation of URLs changes in the future
        return self.__origin_url

    def __send_request(self, full_url, kwargs):
        response = self.request_session.get(full_url, params=kwargs)
        if response.ok:
            return response
        else:
            raise requests.exceptions.RequestException()

    def __process_request(self, dataset_name, params):
        params["datasetname"] = dataset_name
        query_params = self.__validate_inputs(params)
        full_url = self.__compose_full_url()
        response = self.__send_request(full_url, query_params)
        return response

    def nipa(self, year, frequency, tableName, **kwargs):
        kwargs["Year"], kwargs["Frequency"], kwargs["TableName"] = year, frequency, tableName
        response = self.__process_request('NIPA', kwargs)
        return response.text

    def ni_underlying_detail(self, year, frequency, **kwargs):
        kwargs["Year"], kwargs["Frequency"] = year, frequency
        response = self.__process_request('NIUnderlyingDetail', kwargs)
        return response.text

    def fixed_assets(self, year, tableName, **kwargs):
        kwargs["Year"], kwargs["TableName"] = year, tableName
        response = self.__process_request('FixedAssets', kwargs)
        return response.text

    def mne_di(self, direction_of_investment, classification, year, **kwargs):
        kwargs["Year"] = year
        kwargs["DirectionOfInvestment"] = direction_of_investment
        kwargs["Classification"] = classification
        response = self.__process_request('MNE', kwargs)
        return response.text

    def mne_amne(self,
                 direction_of_investment,
                 classification,
                 year,
                 ownership_level,
                 non_bank_affiliates_only,
                 **kwargs):
        kwargs["DirectionOfInvestment"] = direction_of_investment
        kwargs["Classification"] = classification
        kwargs["Year"] = year
        kwargs["OwnershipLevel"] = ownership_level
        kwargs["NonBankAffiliatesOnly"] = non_bank_affiliates_only
        response = self.__process_request('MNE', kwargs)
        return response.text

    def gdp_by_industry(self, table_id, frequency, year, industry, **kwargs):
        kwargs["TableID"] = table_id
        kwargs["Frequency"] = frequency
        kwargs["Year"] = year
        kwargs["Industry"] = industry
        response = self.__process_request('GDPbyIndustry', kwargs)
        return response.text

    def ita(self, **kwargs):
        response = self.__process_request('ITA', kwargs)
        return response.text

    def iip(self, **kwargs):
        response = self.__process_request('IIP', kwargs)
        return response.text

    def input_output(self, table_id, year, **kwargs):
        kwargs["TableID"], kwargs["Year"] = table_id, year
        response = self.__process_request('InputOutput', kwargs)
        return response.text

    def underlying_gdp_by_industry(self, table_id, frequency, year, industry, **kwargs):
        kwargs["TableID"] = table_id
        kwargs["Frequency"] = frequency
        kwargs["Year"] = year
        kwargs["Industry"] = industry
        response = self.__process_request('UnderlyingGDPbyIndustry', kwargs)
        return response.text

    def intl_serv_trade(self, **kwargs):
        response = self.__process_request('IntlServTrade', kwargs)
        return response.text

    def regional(self, table_name, line_code, geo_fips, **kwargs):
        kwargs["TableName"] = table_name
        kwargs["LineCode"] = line_code
        kwargs["GeoFips"] = geo_fips
        response = self.__process_request('Regional', kwargs)
        return response.text

    def intl_serv_sta(self, **kwargs):
        response = self.__process_request('IntlServSTA', kwargs)
        return response.text
