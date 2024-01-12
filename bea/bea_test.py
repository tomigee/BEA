from unittest import TestCase, mock
# import os

from bea import bea
from bea.bea import Bea

# Testing methodology
# 1. Develop unit tests for each method
# 2. Develop integration tests for the public methods
# 3. Develop integration tests for the public methods, including the API's responses


class TestBeaInit(TestCase):

    # Unit tests
    @classmethod
    def setUpClass(self):
        patcher1 = mock.patch('requests.Session', autospec=True)
        patcher2 = mock.patch.dict(bea.os.environ, {"BEA_API_KEY": "ABCD-EFGH-IJKL-MNOP-1234"})
        self.addClassCleanup(patcher1.stop)
        self.addClassCleanup(patcher2.stop)
        self.mock_request = patcher1.start()
        self.mock_os = patcher2.start()
        self.client = Bea()

    def test_assigns_api_token(self):
        assert hasattr(self.client, "_Bea__api_token")
        self.assertEqual(self.client._Bea__api_token, "ABCD-EFGH-IJKL-MNOP-1234")

    def test_assigns_query_params(self):
        assert hasattr(self.client, "_Bea__query_params")
        # TODO: Should I test for the different entries in __query_params?

    def test_assigns_origin_url(self):
        assert hasattr(self.client, "_Bea__origin_url")

    def test_initiates_requests_session(self):
        assert hasattr(self.client, "request_session")
        self.mock_request.assert_called()
        # print(self.client.request_session.return_value.assert_called())
        pass


class TestBeaValidateInputs(TestCase):
    # Unit tests
    def test_output_value(self):
        pass
    pass


class TestBeaComposeFullUrl(TestCase):
    # Unit tests
    def test_output_value(self):
        pass
    pass


class TestSendRequest(TestCase):
    # Unit tests
    def test_request_made_with_correct_arguments(self):
        pass
    pass


class TestProcessRequest(TestCase):
    # Unit tests
    def test_calls_validate_inputs_correctly(self):
        pass

    def test_calls_compose_full_url_correctly(self):
        pass

    def test_calls_send_request_correctly(self):
        pass

    # Integration tests
    def test_output_value(self):
        pass
    pass


class TestNipa(TestCase):
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


class TestNiUnderlyingDetail(TestCase):
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


class TestFixedAssets(TestCase):
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
