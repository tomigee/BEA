from unittest import TestCase, mock
from copy import copy
from json import loads, dumps

from bea import bea
from bea.bea import Bea

# Testing methodology
# 1. Develop unit tests for each method
# 2. Develop integration tests for the public methods
# 3. Develop integration tests for the public methods, including the API's responses


def common_setup(func):
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        patcher1 = mock.patch.dict(bea.os.environ, {"BEA_API_KEY": "ABCD-EFGH-IJKL-MNOP-1234"})
        self.addClassCleanup(patcher1.stop)
        self.mock_os = patcher1.start()
        self.client = Bea()

    return wrapper


def strip_time_from_api_response(response):
    if isinstance(response, str):
        response = loads(response)
    response["BEAAPI"]["Results"]["UTCProductionTime"] = "null"
    return dumps(response)


def impute_api_token(response, api_token):
    if isinstance(response, str):
        response = loads(response)
    params = response["BEAAPI"]["Request"]["RequestParam"]
    for name_val_pair in params:
        if name_val_pair["ParameterName"] == "USERID":
            name_val_pair["ParameterValue"] = api_token
            break
    return dumps(response)


class TestBeaInit(TestCase):

    @classmethod
    @common_setup
    def setUpClass(self):
        patcher2 = mock.patch('requests.Session', autospec=True)
        self.addClassCleanup(patcher2.stop)
        self.mock_request = patcher2.start()

    # Unit tests

    def test_assigns_api_token(self):
        assert hasattr(self.client, "_Bea__api_token")
        self.assertEqual(self.client._Bea__api_token, "ABCD-EFGH-IJKL-MNOP-1234")

    def test_assigns_query_params(self):
        assert hasattr(self.client, "_Bea__query_params")
        # TODO: Should I test for the different entries in __query_params? Yes, you should

    def test_assigns_origin_url(self):
        assert hasattr(self.client, "_Bea__origin_url")

    def test_output_value_origin_url(self):
        self.assertEqual(
            self.client._Bea__origin_url,
            "https://apps.bea.gov/api/data"
        )

    def test_initiates_requests_session(self):
        assert hasattr(self.client, "request_session")
        self.mock_request.assert_called()

    # TODO: Do I have to implement tearDownClass()?
    @classmethod
    def tearDownClass(self):
        del self.client


class TestBeaValidateInputs(TestCase):

    @classmethod
    @common_setup
    def setUpClass(self):
        pass

    # Unit tests
    def test_output_value(self):
        params_test_cases = {
            "input1": {
                "dummy_key1": 1234,
                "dummy_key2": "dummy_val"
                },
            "output1": {
                "UserID": self.client._Bea__api_token,
                "method": "GetData",
                "ResultFormat": "json",
                "dummy_key1": 1234,
                "dummy_key2": "dummy_val"
                },
            "input2": {
                "dummy_key1": "dummy_val1",
                "method": "DummyMethod",
                "ResultFormat": "xml"
                },
            "output2": {
                "UserID": self.client._Bea__api_token,
                "dummy_key1": "dummy_val1",
                "method": "DummyMethod",
                "ResultFormat": "xml"
            }
        }

        self.assertEqual(self.client._Bea__validate_inputs(), self.client._Bea__query_params)
        self.assertEqual(
            self.client._Bea__validate_inputs(params_test_cases["input1"]),
            params_test_cases["output1"]
        )
        self.assertEqual(
            self.client._Bea__validate_inputs(params_test_cases["input2"]),
            params_test_cases["output2"]
        )

    @classmethod
    def tearDownClass(self):
        del self.client


class TestBeaComposeFullUrl(TestCase):

    @classmethod
    @common_setup
    def setUpClass(self):
        pass

    # Unit tests
    def test_output_value(self):
        self.assertEqual(
            self.client._Bea__compose_full_url(),
            self.client._Bea__origin_url
        )
        self.assertEqual(
            self.client._Bea__compose_full_url("/this/url/should/not/be/concatenated"),
            self.client._Bea__origin_url
        )

    @classmethod
    def tearDownClass(self):
        del self.client


class TestSendRequest(TestCase):

    @classmethod
    @common_setup
    def setUpClass(self):
        patcher2 = mock.patch('requests.Session.get', autospec=True)
        self.addClassCleanup(patcher2.stop)
        self.mock_request = patcher2.start()

    # Unit tests
    def test_request_made_with_correct_arguments(self):
        test_cases = {
            "input1": (
                "https://apps.bea.gov/api/data",
                {
                    "key1": "val1",
                    "key2": "val2"
                }
            )
        }
        self.client._Bea__send_request(*test_cases["input1"])
        self.mock_request.assert_called_once_with(
            self.client.request_session,
            test_cases["input1"][0],
            params=test_cases["input1"][1]
        )

    @classmethod
    def tearDownClass(self):
        del self.client


class TestProcessRequest(TestCase):

    @classmethod
    @common_setup
    def setUpClass(self):
        pass

    # Unit tests
    def test_calls_validate_inputs_correctly(self):
        test_cases = {
            "input1": (
                "NIPA",
                {
                    "key1": "val1",
                    "key2": "val2"
                }
            ),
            "output1": {
                "key1": "val1",
                "key2": "val2",
                "datasetname": "NIPA"
            }
        }

        with mock.patch(
            'bea.bea.Bea._Bea__validate_inputs',
            wraps=self.client._Bea__validate_inputs
        ) as small_mock:
            self.client._Bea__process_request(*test_cases["input1"])
            small_mock.assert_called_once_with(
                test_cases["output1"]
            )

    def test_calls_compose_full_url_correctly(self):
        test_cases = {
            "input1": (
                "NIPA",
                {
                    "key1": "val1",
                    "key2": "val2"
                }
            ),
        }

        with mock.patch(
            'bea.bea.Bea._Bea__compose_full_url',
            wraps=self.client._Bea__compose_full_url
        ) as small_mock:
            self.client._Bea__process_request(*test_cases["input1"])
            calls = [mock.call()]
            small_mock.assert_has_calls(calls, any_order=True)

    def test_calls_send_request_correctly(self):
        test_inputs = {
            "input1": (
                "NIPA",
                {
                    "key1": "val1",
                    "key2": "val2"
                }
            ),
        }

        test_outputs = {
            "output1": (
                self.client._Bea__compose_full_url(),
                self.client._Bea__validate_inputs(
                    {
                        **test_inputs["input1"][1],
                        "datasetname": test_inputs["input1"][0]
                    }
                )
            ),
        }

        with mock.patch(
            'bea.bea.Bea._Bea__send_request',
            wraps=self.client._Bea__send_request
        ) as small_mock:
            self.client._Bea__process_request(*test_inputs["input1"])
            small_mock.assert_called_once_with(
                *test_outputs["output1"]
            )

    # Integration tests w/ API
    def test_output_value(self):
        pass

    @classmethod
    def tearDownClass(self):
        del self.client


class TestNipa(TestCase):

    @classmethod
    def setUpClass(self):
        self.client = Bea()

    # Unit tests
    def test_calls_process_request_correctly(self):
        # TODO: Make this unit test independent of the API being functional/non-functional
        test_cases = [
            {
                "year": 2022,
                "frequency": "a",
                "tableName": "NCR322T"
            },
        ]

        args_to_remove = ["year", "frequency", "tableName"]

        with mock.patch(
            'bea.bea.Bea._Bea__process_request',
            wraps=self.client._Bea__process_request
        ) as mock_process:
            for test_case in test_cases:
                self.client.nipa(**test_case)
                dummy_test_case = copy(test_case)
                [dummy_test_case.pop(key) for key in args_to_remove]
                kwargs = {
                    **dummy_test_case,
                    "Year": test_case["year"],
                    "Frequency": test_case["frequency"],
                    "TableName": test_case["tableName"]
                }
                mock_process.assert_called_once_with('NIPA', kwargs)

    # Integration tests w API
    def test_output_value_API(self):
        test_inputs = {
            "input1": {
                "year": 2005,
                "frequency": "a",
                "tableName": "T10102",
            }
        }
        responses = {
            "response1": {
                "BEAAPI": {
                    "Request": {
                        "RequestParam": [
                            {
                                "ParameterName": "USERID",
                                "ParameterValue": "dummy_api_token"
                            },
                            {
                                "ParameterName": "METHOD",
                                "ParameterValue": "GETDATA"
                            },
                            {
                                "ParameterName": "RESULTFORMAT",
                                "ParameterValue": "JSON"
                            },
                            {
                                "ParameterName": "YEAR",
                                "ParameterValue": "2005"
                            },
                            {
                                "ParameterName": "FREQUENCY",
                                "ParameterValue": "A"
                            },
                            {
                                "ParameterName": "TABLENAME",
                                "ParameterValue": "T10102"
                            },
                            {
                                "ParameterName": "DATASETNAME",
                                "ParameterValue": "NIPA"
                            },
                            {
                                "ParameterName": "ShowMillions",
                                "ParameterValue": "N"
                            }
                        ]
                    },
                    "Results": {
                        "Statistic": "NIPA Table",
                        "UTCProductionTime": "2024-01-20T20:28:28.923",
                        "Dimensions": [
                            {
                                "Ordinal": "1",
                                "Name": "TableName",
                                "DataType": "string",
                                "IsValue": "0"
                            },
                            {
                                "Ordinal": "2",
                                "Name": "SeriesCode",
                                "DataType": "string",
                                "IsValue": "0"
                            },
                            {
                                "Ordinal": "3",
                                "Name": "LineNumber",
                                "DataType": "numeric",
                                "IsValue": "0"
                            },
                            {
                                "Ordinal": "4",
                                "Name": "LineDescription",
                                "DataType": "string",
                                "IsValue": "0"
                            },
                            {
                                "Ordinal": "5",
                                "Name": "TimePeriod",
                                "DataType": "string",
                                "IsValue": "0"
                            },
                            {
                                "Ordinal": "6",
                                "Name": "CL_UNIT",
                                "DataType": "string",
                                "IsValue": "0"
                            },
                            {
                                "Ordinal": "7",
                                "Name": "UNIT_MULT",
                                "DataType": "numeric",
                                "IsValue": "0"
                            },
                            {
                                "Ordinal": "8",
                                "Name": "METRIC_NAME",
                                "DataType": "string",
                                "IsValue": "0"
                            },
                            {
                                "Ordinal": "9",
                                "Name": "DataValue",
                                "DataType": "numeric",
                                "IsValue": "1"
                            }
                        ],
                        "Data": [
                            {
                                "TableName": "T10102",
                                "SeriesCode": "A191RL",
                                "LineNumber": "1",
                                "LineDescription": "Gross domestic product",
                                "TimePeriod": "2005",
                                "METRIC_NAME": "Fisher Quantity Index",
                                "CL_UNIT": "Percent change, annual rate",
                                "UNIT_MULT": "0",
                                "DataValue": "3.5",
                                "NoteRef": "T10102"
                            },
                            {
                                "TableName": "T10102",
                                "SeriesCode": "DPCERY",
                                "LineNumber": "2",
                                "LineDescription": "Personal consumption expenditures",
                                "TimePeriod": "2005",
                                "METRIC_NAME": "Quantity Contributions",
                                "CL_UNIT": "Level",
                                "UNIT_MULT": "0",
                                "DataValue": "2.38",
                                "NoteRef": "T10102"
                            },
                            {
                                "TableName": "T10102",
                                "SeriesCode": "DGDSRY",
                                "LineNumber": "3",
                                "LineDescription": "Goods",
                                "TimePeriod": "2005",
                                "METRIC_NAME": "Quantity Contributions",
                                "CL_UNIT": "Level",
                                "UNIT_MULT": "0",
                                "DataValue": "0.98",
                                "NoteRef": "T10102"
                            },
                            {
                                "TableName": "T10102",
                                "SeriesCode": "DDURRY",
                                "LineNumber": "4",
                                "LineDescription": "Durable goods",
                                "TimePeriod": "2005",
                                "METRIC_NAME": "Quantity Contributions",
                                "CL_UNIT": "Level",
                                "UNIT_MULT": "0",
                                "DataValue": "0.48",
                                "NoteRef": "T10102"
                            },
                            {
                                "TableName": "T10102",
                                "SeriesCode": "DNDGRY",
                                "LineNumber": "5",
                                "LineDescription": "Nondurable goods",
                                "TimePeriod": "2005",
                                "METRIC_NAME": "Quantity Contributions",
                                "CL_UNIT": "Level",
                                "UNIT_MULT": "0",
                                "DataValue": "0.50",
                                "NoteRef": "T10102"
                            },
                            {
                                "TableName": "T10102",
                                "SeriesCode": "DSERRY",
                                "LineNumber": "6",
                                "LineDescription": "Services",
                                "TimePeriod": "2005",
                                "METRIC_NAME": "Quantity Contributions",
                                "CL_UNIT": "Level",
                                "UNIT_MULT": "0",
                                "DataValue": "1.40",
                                "NoteRef": "T10102"
                            },
                            {
                                "TableName": "T10102",
                                "SeriesCode": "A006RY",
                                "LineNumber": "7",
                                "LineDescription": "Gross private domestic investment",
                                "TimePeriod": "2005",
                                "METRIC_NAME": "Quantity Contributions",
                                "CL_UNIT": "Level",
                                "UNIT_MULT": "0",
                                "DataValue": "1.26",
                                "NoteRef": "T10102"
                            },
                            {
                                "TableName": "T10102",
                                "SeriesCode": "A007RY",
                                "LineNumber": "8",
                                "LineDescription": "Fixed investment",
                                "TimePeriod": "2005",
                                "METRIC_NAME": "Quantity Contributions",
                                "CL_UNIT": "Level",
                                "UNIT_MULT": "0",
                                "DataValue": "1.33",
                                "NoteRef": "T10102"
                            },
                            {
                                "TableName": "T10102",
                                "SeriesCode": "A008RY",
                                "LineNumber": "9",
                                "LineDescription": "Nonresidential",
                                "TimePeriod": "2005",
                                "METRIC_NAME": "Quantity Contributions",
                                "CL_UNIT": "Level",
                                "UNIT_MULT": "0",
                                "DataValue": "0.92",
                                "NoteRef": "T10102"
                            },
                            {
                                "TableName": "T10102",
                                "SeriesCode": "A009RY",
                                "LineNumber": "10",
                                "LineDescription": "Structures",
                                "TimePeriod": "2005",
                                "METRIC_NAME": "Quantity Contributions",
                                "CL_UNIT": "Level",
                                "UNIT_MULT": "0",
                                "DataValue": "0.06",
                                "NoteRef": "T10102"
                            },
                            {
                                "TableName": "T10102",
                                "SeriesCode": "Y033RY",
                                "LineNumber": "11",
                                "LineDescription": "Equipment",
                                "TimePeriod": "2005",
                                "METRIC_NAME": "Quantity Contributions",
                                "CL_UNIT": "Level",
                                "UNIT_MULT": "0",
                                "DataValue": "0.60",
                                "NoteRef": "T10102"
                            },
                            {
                                "TableName": "T10102",
                                "SeriesCode": "Y001RY",
                                "LineNumber": "12",
                                "LineDescription": "Intellectual property products",
                                "TimePeriod": "2005",
                                "METRIC_NAME": "Quantity Contributions",
                                "CL_UNIT": "Level",
                                "UNIT_MULT": "0",
                                "DataValue": "0.26",
                                "NoteRef": "T10102"
                            },
                            {
                                "TableName": "T10102",
                                "SeriesCode": "A011RY",
                                "LineNumber": "13",
                                "LineDescription": "Residential",
                                "TimePeriod": "2005",
                                "METRIC_NAME": "Quantity Contributions",
                                "CL_UNIT": "Level",
                                "UNIT_MULT": "0",
                                "DataValue": "0.41",
                                "NoteRef": "T10102"
                            },
                            {
                                "TableName": "T10102",
                                "SeriesCode": "A014RY",
                                "LineNumber": "14",
                                "LineDescription": "Change in private inventories",
                                "TimePeriod": "2005",
                                "METRIC_NAME": "Quantity Contributions",
                                "CL_UNIT": "Level",
                                "UNIT_MULT": "0",
                                "DataValue": "-0.07",
                                "NoteRef": "T10102"
                            },
                            {
                                "TableName": "T10102",
                                "SeriesCode": "A019RY",
                                "LineNumber": "15",
                                "LineDescription": "Net exports of goods and services",
                                "TimePeriod": "2005",
                                "METRIC_NAME": "Quantity Contributions",
                                "CL_UNIT": "Level",
                                "UNIT_MULT": "0",
                                "DataValue": "-0.30",
                                "NoteRef": "T10102"
                            },
                            {
                                "TableName": "T10102",
                                "SeriesCode": "A020RY",
                                "LineNumber": "16",
                                "LineDescription": "Exports",
                                "TimePeriod": "2005",
                                "METRIC_NAME": "Quantity Contributions",
                                "CL_UNIT": "Level",
                                "UNIT_MULT": "0",
                                "DataValue": "0.67",
                                "NoteRef": "T10102"
                            },
                            {
                                "TableName": "T10102",
                                "SeriesCode": "A253RY",
                                "LineNumber": "17",
                                "LineDescription": "Goods",
                                "TimePeriod": "2005",
                                "METRIC_NAME": "Quantity Contributions",
                                "CL_UNIT": "Level",
                                "UNIT_MULT": "0",
                                "DataValue": "0.52",
                                "NoteRef": "T10102"
                            },
                            {
                                "TableName": "T10102",
                                "SeriesCode": "A646RY",
                                "LineNumber": "18",
                                "LineDescription": "Services",
                                "TimePeriod": "2005",
                                "METRIC_NAME": "Quantity Contributions",
                                "CL_UNIT": "Level",
                                "UNIT_MULT": "0",
                                "DataValue": "0.15",
                                "NoteRef": "T10102"
                            },
                            {
                                "TableName": "T10102",
                                "SeriesCode": "A021RY",
                                "LineNumber": "19",
                                "LineDescription": "Imports",
                                "TimePeriod": "2005",
                                "METRIC_NAME": "Quantity Contributions",
                                "CL_UNIT": "Level",
                                "UNIT_MULT": "0",
                                "DataValue": "-0.98",
                                "NoteRef": "T10102"
                            },
                            {
                                "TableName": "T10102",
                                "SeriesCode": "A255RY",
                                "LineNumber": "20",
                                "LineDescription": "Goods",
                                "TimePeriod": "2005",
                                "METRIC_NAME": "Quantity Contributions",
                                "CL_UNIT": "Level",
                                "UNIT_MULT": "0",
                                "DataValue": "-0.88",
                                "NoteRef": "T10102"
                            },
                            {
                                "TableName": "T10102",
                                "SeriesCode": "A656RY",
                                "LineNumber": "21",
                                "LineDescription": "Services",
                                "TimePeriod": "2005",
                                "METRIC_NAME": "Quantity Contributions",
                                "CL_UNIT": "Level",
                                "UNIT_MULT": "0",
                                "DataValue": "-0.09",
                                "NoteRef": "T10102"
                            },
                            {
                                "TableName": "T10102",
                                "SeriesCode": "A822RY",
                                "LineNumber": "22",
                                "LineDescription": "Government consumption expenditures and gross investment",
                                "TimePeriod": "2005",
                                "METRIC_NAME": "Quantity Contributions",
                                "CL_UNIT": "Level",
                                "UNIT_MULT": "0",
                                "DataValue": "0.14",
                                "NoteRef": "T10102"
                            },
                            {
                                "TableName": "T10102",
                                "SeriesCode": "A823RY",
                                "LineNumber": "23",
                                "LineDescription": "Federal",
                                "TimePeriod": "2005",
                                "METRIC_NAME": "Quantity Contributions",
                                "CL_UNIT": "Level",
                                "UNIT_MULT": "0",
                                "DataValue": "0.15",
                                "NoteRef": "T10102"
                            },
                            {
                                "TableName": "T10102",
                                "SeriesCode": "A824RY",
                                "LineNumber": "24",
                                "LineDescription": "National defense",
                                "TimePeriod": "2005",
                                "METRIC_NAME": "Quantity Contributions",
                                "CL_UNIT": "Level",
                                "UNIT_MULT": "0",
                                "DataValue": "0.11",
                                "NoteRef": "T10102"
                            },
                            {
                                "TableName": "T10102",
                                "SeriesCode": "A825RY",
                                "LineNumber": "25",
                                "LineDescription": "Nondefense",
                                "TimePeriod": "2005",
                                "METRIC_NAME": "Quantity Contributions",
                                "CL_UNIT": "Level",
                                "UNIT_MULT": "0",
                                "DataValue": "0.04",
                                "NoteRef": "T10102"
                            },
                            {
                                "TableName": "T10102",
                                "SeriesCode": "A829RY",
                                "LineNumber": "26",
                                "LineDescription": "State and local",
                                "TimePeriod": "2005",
                                "METRIC_NAME": "Quantity Contributions",
                                "CL_UNIT": "Level",
                                "UNIT_MULT": "0",
                                "DataValue": "0.00",
                                "NoteRef": "T10102"
                            }
                        ],
                        "Notes": [
                            {
                                "NoteRef": "T10102",
                                "NoteText": "Table 1.1.2. Contributions to Percent Change in Real Gross Domestic Product  - LastRevised: December 21, 2023"
                            }
                        ]
                    }
                }
            },
        }
        test_outputs = {
            "output1": impute_api_token(
                strip_time_from_api_response(responses["response1"]),
                self.client._Bea__api_token
                ),
        }

        self.assertEqual(
            strip_time_from_api_response(
                self.client.nipa(**test_inputs["input1"])
            ),
            test_outputs["output1"]
        )

    @classmethod
    def tearDownClass(self):
        del self.client


class TestNiUnderlyingDetail(TestCase):

    @classmethod
    @common_setup
    def setUpClass(self):
        pass

    # Unit tests
    def test_calls_process_request_correctly(self):
        pass

    # Integration tests
    def test_output_value_(self):
        pass

    # Integration tests w API
    def test_output_value_API(self):
        pass
    pass


class TestFixedAssets(TestCase):

    @classmethod
    @common_setup
    def setUpClass(self):
        pass

    # Unit tests
    def test_calls_process_request_correctly(self):
        pass

    # Integration tests
    def test_output_value(self):
        pass

    # Integration tests w API
    def test_output_value_API(self):
        pass
    pass


class TestMneDi(TestCase):

    @classmethod
    @common_setup
    def setUpClass(self):
        pass

    # Unit tests
    def test_calls_process_request_correctly(self):
        pass

    # Integration tests
    def test_output_value(self):
        pass

    # Integration tests w API
    def test_output_value_API(self):
        pass
    pass


class TestMneAmne(TestCase):

    @classmethod
    @common_setup
    def setUpClass(self):
        pass

    # Unit tests
    def test_calls_process_request_correctly(self):
        pass

    # Integration tests
    def test_output_value(self):
        pass

    # Integration tests w API
    def test_output_value_API(self):
        pass
    pass


class TestGdpByIndustry(TestCase):

    @classmethod
    @common_setup
    def setUpClass(self):
        pass

    # Unit tests
    def test_calls_process_request_correctly(self):
        pass

    # Integration tests
    def test_output_value(self):
        pass

    # Integration tests w API
    def test_output_value_API(self):
        pass
    pass


class TestIta(TestCase):

    @classmethod
    @common_setup
    def setUpClass(self):
        pass

    # Unit tests
    def test_calls_process_request_correctly(self):
        pass

    # Integration tests
    def test_output_value(self):
        pass

    # Integration tests w API
    def test_output_value_API(self):
        pass
    pass


class TestIip(TestCase):

    @classmethod
    @common_setup
    def setUpClass(self):
        pass

    # Unit tests
    def test_calls_process_request_correctly(self):
        pass

    # Integration tests
    def test_output_value(self):
        pass

    # Integration tests w API
    def test_output_value_API(self):
        pass
    pass


class TestInputOutput(TestCase):

    @classmethod
    @common_setup
    def setUpClass(self):
        pass

    # Unit tests
    def test_calls_process_request_correctly(self):
        pass

    # Integration tests
    def test_output_value(self):
        pass

    # Integration tests w API
    def test_output_value_API(self):
        pass
    pass


class TestUnderlyingGdpByIndustry(TestCase):

    @classmethod
    @common_setup
    def setUpClass(self):
        pass

    # Unit tests
    def test_calls_process_request_correctly(self):
        pass

    # Integration tests
    def test_output_value(self):
        pass

    # Integration tests w API
    def test_output_value_API(self):
        pass
    pass


class TestIntlServTrade(TestCase):

    @classmethod
    @common_setup
    def setUpClass(self):
        pass

    # Unit tests
    def test_calls_process_request_correctly(self):
        pass

    # Integration tests
    def test_output_value(self):
        pass

    # Integration tests w API
    def test_output_value_API(self):
        pass
    pass


class TestRegional(TestCase):

    @classmethod
    @common_setup
    def setUpClass(self):
        pass

    # Unit tests
    def test_calls_process_request_correctly(self):
        pass

    # Integration tests
    def test_output_value(self):
        pass

    # Integration tests w API
    def test_output_value_API(self):
        pass
    pass


class TestIntlServSta(TestCase):

    @classmethod
    @common_setup
    def setUpClass(self):
        pass

    # Unit tests
    def test_calls_process_request_correctly(self):
        pass

    # Integration tests
    def test_output_value(self):
        pass

    # Integration tests w API
    def test_output_value_API(self):
        pass
    pass
