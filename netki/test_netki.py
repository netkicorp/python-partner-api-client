__author__ = 'frank'

import json
from mock import Mock, patch
from unittest import TestCase

from netki import Netki, submit_request, WalletName


class TestSubmitRequest(TestCase):
    def setUp(self):
        self.patcher1 = patch('netki.requests')
        self.mockRequests = self.patcher1.start()

        self.headers = {
            'X-Partner-ID': 'partner_id',
            'Content-Type': 'application/json',
            'Authorization': 'api_key'
        }

        self.request_data = {'key': 'val'}

    def tearDown(self):
        self.patcher1.stop()

    def test_get_request(self):

        ret_val = submit_request('api_key', 'partner_id', 'uri', 'GET')

        # Validate submit_request data
        self.assertEqual(1, self.mockRequests.get.call_count)
        self.assertEqual(0, self.mockRequests.post.call_count)
        self.assertEqual(0, self.mockRequests.put.call_count)
        self.assertEqual(0, self.mockRequests.delete.call_count)

        call_args = self.mockRequests.get.call_args
        self.assertEqual('uri', call_args[0][0])
        self.assertDictEqual(self.headers, call_args[1].get('headers'))

        # Validate response
        self.assertEqual(ret_val, self.mockRequests.get.return_value)

    def test_post_request(self):

        ret_val = submit_request('api_key', 'partner_id', 'uri', 'POST', self.request_data)

        # Validate submit_request data
        self.assertEqual(0, self.mockRequests.get.call_count)
        self.assertEqual(1, self.mockRequests.post.call_count)
        self.assertEqual(0, self.mockRequests.put.call_count)
        self.assertEqual(0, self.mockRequests.delete.call_count)

        call_args = self.mockRequests.post.call_args
        self.assertEqual('uri', call_args[0][0])
        self.assertDictEqual(self.headers, call_args[1].get('headers'))
        self.assertDictEqual(self.request_data, call_args[1].get('data'))

        # Validate response
        self.assertEqual(ret_val, self.mockRequests.post.return_value)

    def test_put_request(self):

        ret_val = submit_request('api_key', 'partner_id', 'uri', 'PUT', self.request_data)

        # Validate submit_request data
        self.assertEqual(0, self.mockRequests.get.call_count)
        self.assertEqual(0, self.mockRequests.post.call_count)
        self.assertEqual(1, self.mockRequests.put.call_count)
        self.assertEqual(0, self.mockRequests.delete.call_count)

        call_args = self.mockRequests.put.call_args
        self.assertEqual('uri', call_args[0][0])
        self.assertDictEqual(self.headers, call_args[1].get('headers'))
        self.assertDictEqual(self.request_data, call_args[1].get('data'))

        # Validate response
        self.assertEqual(ret_val, self.mockRequests.put.return_value)

    def test_delete_request(self):

        ret_val = submit_request('api_key', 'partner_id', 'uri', 'DELETE')

        # Validate submit_request data
        self.assertEqual(0, self.mockRequests.get.call_count)
        self.assertEqual(0, self.mockRequests.post.call_count)
        self.assertEqual(0, self.mockRequests.put.call_count)
        self.assertEqual(1, self.mockRequests.delete.call_count)

        call_args = self.mockRequests.delete.call_args
        self.assertEqual('uri', call_args[0][0])
        self.assertDictEqual(self.headers, call_args[1].get('headers'))

        # Validate response
        self.assertEqual(ret_val, self.mockRequests.delete.return_value)

    def test_unknown_request(self):

        self.assertRaisesRegexp(
            Exception,
            'Unsupported method',
            submit_request,
            'api_key',
            'partner_id',
            'uri',
            'PATCH',
            self.request_data
        )

        # Validate submit_request data
        self.assertEqual(0, self.mockRequests.get.call_count)
        self.assertEqual(0, self.mockRequests.post.call_count)
        self.assertEqual(0, self.mockRequests.put.call_count)
        self.assertEqual(0, self.mockRequests.delete.call_count)


class TestWalletNameInit(TestCase):
    def setUp(self):
        self.wallet_name = WalletName(
            id='id',
            domain_name='testdomain.com',
            name='myname',
            wallets={'key': 'value'},
            external_id='external_id'
        )

    def test_init_values(self):
        self.assertEqual('id', self.wallet_name.id)
        self.assertEqual('testdomain.com', self.wallet_name.domain_name)
        self.assertEqual('myname', self.wallet_name.name)
        self.assertDictEqual({'key': 'value'}, self.wallet_name.wallets)
        self.assertEqual('external_id', self.wallet_name.external_id)


class TestWalletNameSetApiOpts(TestCase):
    def setUp(self):
        self.wallet_name = WalletName(
            id='id',
            domain_name='testdomain.com',
            name='myname',
            wallets={'key': 'value'},
            external_id='external_id'
        )

    def test_set_api_opts(self):
        self.wallet_name.set_api_opts('url', 'api_key', 'partner_id')

        self.assertEqual('url', self.wallet_name.api_url)
        self.assertEqual('api_key', self.wallet_name.api_key)
        self.assertEqual('partner_id', self.wallet_name.partner_id)


class TestWalletNameGettersSetters(TestCase):
    def setUp(self):
        self.wallet_name = WalletName(
            id='id',
            domain_name='testdomain.com',
            name='myname',
            wallets={'key': 'value'},
            external_id='external_id'
        )

    def test_get_used_currencies(self):

        self.assertDictEqual({'key': 'value'}, self.wallet_name.get_used_currencies())

    def test_get_wallet_address(self):

        self.assertEqual('value', self.wallet_name.get_wallet_address('key'))

    def test_set_currency_address(self):

        self.wallet_name.set_currency_address('key2', 'value2')

        self.assertDictEqual({'key': 'value', 'key2': 'value2'}, self.wallet_name.wallets)

    def test_remove_currency_address(self):

        self.wallet_name.remove_currency_address('key')

        self.assertEqual({}, self.wallet_name.wallets)


class TestWalletNameSave(TestCase):
    def setUp(self):
        self.patcher1 = patch('netki.submit_request')
        self.patcher2 = patch('netki.AttrDict')
        self.mockSubmitRequest = self.patcher1.start()
        self.mockAttrDict = self.patcher2.start()

        self.wallet_name = WalletName(
            id='id',
            domain_name='testdomain.com',
            name='myname',
            wallets={'key': 'value'},
            external_id='external_id'
        )

        # Setup Wallet Name object data
        self.wallet_name.id = 'id'
        self.wallet_name.domain_name = 'testdomain.com'
        self.wallet_name.name = 'name'
        self.wallet_name.wallets = {'key': 'value'}
        self.wallet_name.external_id = 'external_id'

        # Add API opts for mock API call
        self.wallet_name.api_url = 'url'
        self.wallet_name.api_key = 'api_key'
        self.wallet_name.partner_id = 'partner_id'

        # Setup mock response data for validation
        self.mockSubmitRequest.return_value.status_code = 200

        self.mock_wallet_name_response_obj = Mock()
        self.mock_wallet_name_response_obj.id = 'id'
        self.mock_wallet_name_response_obj.domain_name = 'testdomain.com'
        self.mock_wallet_name_response_obj.name = 'name'
        self.mock_wallet_name_response_obj.wallets = {'key': 'value'}
        self.mock_wallet_name_response_obj.external_id = 'external_id'

        self.response_obj = Mock()
        self.response_obj.success = True
        self.response_obj.wallet_names = [
            self.mock_wallet_name_response_obj
        ]
        self.mockAttrDict.return_value = self.response_obj

        # Setup mock wn_api_data to validate submission data
        self.mock_wn_api_data = {
            'wallet_names': [
                {
                    'domain_name': self.wallet_name.domain_name,
                    'name': self.wallet_name.name,
                    'wallets': [
                        {
                            'currency': 'key',
                            'wallet_address': 'value'
                        }
                    ],
                    'external_id': self.wallet_name.external_id,
                    'id': 'id'
                }
            ]
        }

    def tearDown(self):
        self.patcher1.stop()

    def test_wallet_update_go_right(self):

        self.wallet_name.save()

        self.assertEqual(1, self.mockSubmitRequest.call_count)

        call_args = self.mockSubmitRequest.call_args[0]
        self.assertEqual(call_args[0], self.wallet_name.api_key)
        self.assertEqual(call_args[1], self.wallet_name.partner_id)
        self.assertEqual(call_args[2], self.wallet_name.api_url + '/v1/partner/walletname')
        self.assertEqual(call_args[3], 'PUT')
        self.assertEqual(call_args[4], json.dumps(self.mock_wn_api_data))

    def test_wallet_create_go_right(self):

        # Setup test case
        self.wallet_name.id = None
        del self.mock_wn_api_data.get('wallet_names')[0]['id']

        self.wallet_name.save()

        self.assertEqual(1, self.mockSubmitRequest.call_count)
        self.assertEqual(self.wallet_name.id, self.mock_wallet_name_response_obj.id)

        call_args = self.mockSubmitRequest.call_args[0]
        self.assertEqual(self.wallet_name.api_key, call_args[0])
        self.assertEqual(self.wallet_name.partner_id, call_args[1])
        self.assertEqual(self.wallet_name.api_url + '/v1/partner/walletname', call_args[2])
        self.assertEqual('POST', call_args[3])
        self.assertEqual(json.dumps(self.mock_wn_api_data), call_args[4])

    def test_save_failed_with_failures(self):

        # Setup test case
        self.mockSubmitRequest.return_value.status_code = 404
        self.failure_message = Mock()
        self.failure_message.message = 'this failed'
        self.response_obj.failures = [self.failure_message]

        self.assertRaisesRegexp(Exception, 'WalletName Save Failed! this failed', self.wallet_name.save)

        self.assertEqual(1, self.mockSubmitRequest.call_count)

        call_args = self.mockSubmitRequest.call_args[0]
        self.assertEqual(self.wallet_name.api_key, call_args[0])
        self.assertEqual(self.wallet_name.partner_id, call_args[1])
        self.assertEqual(self.wallet_name.api_url + '/v1/partner/walletname', call_args[2])
        self.assertEqual('PUT', call_args[3])
        self.assertEqual(json.dumps(self.mock_wn_api_data), call_args[4])

    def test_save_failed_with_message(self):

        # Setup test case
        self.mockSubmitRequest.return_value.status_code = 404
        self.response_obj.get.return_value = None
        self.response_obj.message = 'this also failed'

        self.assertRaisesRegexp(Exception, 'WalletName Save Failed! this also failed', self.wallet_name.save)

        self.assertEqual(1, self.mockSubmitRequest.call_count)

        call_args = self.mockSubmitRequest.call_args[0]
        self.assertEqual(self.wallet_name.api_key, call_args[0])
        self.assertEqual(self.wallet_name.partner_id, call_args[1])
        self.assertEqual(self.wallet_name.api_url + '/v1/partner/walletname', call_args[2])
        self.assertEqual('PUT', call_args[3])
        self.assertEqual(json.dumps(self.mock_wn_api_data), call_args[4])


class TestWalletNameDelete(TestCase):
    def setUp(self):
        self.patcher1 = patch('netki.submit_request')
        self.patcher2 = patch('netki.AttrDict')
        self.mockSubmitRequest = self.patcher1.start()
        self.mockAttrDict = self.patcher2.start()

        self.wallet_name = WalletName(
            id='id',
            domain_name='testdomain.com',
            name='myname',
            wallets={'key': 'value'},
            external_id='external_id'
        )

        # Setup Wallet Name object data
        self.wallet_name.id = 'id'
        self.wallet_name.domain_name = 'testdomain.com'

        # Add API opts for mock call
        self.wallet_name.api_url = 'url'
        self.wallet_name.api_key = 'api_key'
        self.wallet_name.partner_id = 'partner_id'

        # Setup mock wn_api_data to validate submission data
        self.mock_wn_api_data = {
            'wallet_names': [
                {
                    'domain_name': self.wallet_name.domain_name,
                    'id': self.wallet_name.id
                }
            ]
        }

        # Setup mock response data for validation
        self.mockSubmitRequest.return_value.status_code = 204
        self.response_obj = Mock()
        self.mockAttrDict.return_value = self.response_obj

    def tearDown(self):
        self.patcher1.stop()

    def test_go_right(self):

        self.assertIsNone(self.wallet_name.delete())

        # Validate delete data
        self.assertEqual(1, self.mockSubmitRequest.call_count)
        call_args = self.mockSubmitRequest.call_args[0]
        self.assertEqual(call_args[0], self.wallet_name.api_key)
        self.assertEqual(call_args[1], self.wallet_name.partner_id)
        self.assertEqual(call_args[2], self.wallet_name.api_url + '/v1/partner/walletname')
        self.assertEqual(call_args[3], 'DELETE')
        self.assertEqual(call_args[4], json.dumps(self.mock_wn_api_data))

    def test_delete_failed_with_failures(self):

        # Setup test case
        self.mockSubmitRequest.return_value.status_code = 404
        self.failure_message = Mock()
        self.failure_message.message = 'this failed'
        self.response_obj.failures = [self.failure_message]

        self.assertRaisesRegexp(Exception, 'WalletName Delete Failed! this failed', self.wallet_name.delete)

        # Validate delete data
        self.assertEqual(1, self.mockSubmitRequest.call_count)
        call_args = self.mockSubmitRequest.call_args[0]
        self.assertEqual(call_args[0], self.wallet_name.api_key)
        self.assertEqual(call_args[1], self.wallet_name.partner_id)
        self.assertEqual(call_args[2], self.wallet_name.api_url + '/v1/partner/walletname')
        self.assertEqual(call_args[3], 'DELETE')
        self.assertEqual(call_args[4], json.dumps(self.mock_wn_api_data))

    def test_delete_failed_with_message(self):

        # Setup test case
        self.mockSubmitRequest.return_value.status_code = 404
        self.response_obj.get.return_value = None
        self.response_obj.message = 'this also failed'

        self.assertRaisesRegexp(Exception, 'WalletName Delete Failed! this also failed', self.wallet_name.delete)

        # Validate delete data
        self.assertEqual(1, self.mockSubmitRequest.call_count)
        call_args = self.mockSubmitRequest.call_args[0]
        self.assertEqual(call_args[0], self.wallet_name.api_key)
        self.assertEqual(call_args[1], self.wallet_name.partner_id)
        self.assertEqual(call_args[2], self.wallet_name.api_url + '/v1/partner/walletname')
        self.assertEqual(call_args[3], 'DELETE')
        self.assertEqual(call_args[4], json.dumps(self.mock_wn_api_data))


class TestNetkiInit(TestCase):
    def setUp(self):
        self.netki = Netki(
            partner_id='partner_id',
            api_key='api_key',
            api_url='api_url'
        )

    def test_go_right(self):
        self.assertEqual('partner_id', self.netki.partner_id)
        self.assertEqual('api_key', self.netki.api_key)
        self.assertEqual('api_url', self.netki.api_url)


class TestNetkiGetWalletNames(TestCase):
    def setUp(self):
        self.patcher1 = patch('netki.submit_request')
        self.patcher2 = patch('netki.AttrDict')
        self.mockSubmitRequest = self.patcher1.start()
        self.mockAttrDict = self.patcher2.start()

        self.netki = Netki(
            partner_id='partner_id',
            api_key='api_key',
            api_url='api_url'
        )

        # Setup Response object
        self.mockSubmitRequest.return_value.status_code = 200

        self.mock_wallet_name = Mock()
        self.mock_wallet_name.id = 'id'
        self.mock_wallet_name.domain_name = 'testdomain.com'
        self.mock_wallet_name.name = 'name'
        self.mock_wallet_name.external_id = 'external_id'
        self.mock_wallets_obj_1 = Mock()
        self.mock_wallets_obj_1.currency = 'btc'
        self.mock_wallets_obj_1.wallet_address = '1btcaddress'
        self.mock_wallets_obj_2 = Mock()
        self.mock_wallets_obj_2.currency = 'dgc'
        self.mock_wallets_obj_2.wallet_address = 'Dgccaddress'
        self.mock_wallet_name.wallets = [self.mock_wallets_obj_1, self.mock_wallets_obj_2]

        self.mock_response_obj = Mock()
        self.mock_response_obj.wallet_names = [self.mock_wallet_name]
        self.mock_response_obj.wallet_name_count = 1

        self.mockAttrDict.return_value = self.mock_response_obj

    def test_go_right_no_args(self):

        ret_val = self.netki.get_wallet_names()

        # Validate GET data
        self.assertEqual(1, self.mockSubmitRequest.call_count)
        call_args = self.mockSubmitRequest.call_args[0]
        self.assertEqual(call_args[0], self.netki.api_key)
        self.assertEqual(call_args[1], self.netki.partner_id)
        self.assertEqual(call_args[2], self.netki.api_url + '/v1/partner/walletname')
        self.assertEqual(call_args[3], 'GET')

        # Validate response object
        self.assertEqual(self.mock_wallet_name.id, ret_val[0].id)
        self.assertEqual(self.mock_wallet_name.domain_name, ret_val[0].domain_name)
        self.assertEqual(self.mock_wallet_name.name, ret_val[0].name)
        self.assertEqual(self.mock_wallet_name.external_id, ret_val[0].external_id)
        self.assertDictEqual({'dgc': 'Dgccaddress', 'btc': '1btcaddress'}, ret_val[0].wallets)
        self.assertEqual('api_url', ret_val[0].api_url)
        self.assertEqual('api_key', ret_val[0].api_key)
        self.assertEqual('partner_id', ret_val[0].partner_id)

    def test_go_right_with_domain_name(self):

        ret_val = self.netki.get_wallet_names(domain_name='testdomain.com')

        # Validate GET data
        self.assertEqual(1, self.mockSubmitRequest.call_count)
        call_args = self.mockSubmitRequest.call_args[0]
        self.assertEqual(call_args[0], self.netki.api_key)
        self.assertEqual(call_args[1], self.netki.partner_id)
        self.assertEqual(call_args[2], self.netki.api_url + '/v1/partner/walletname?domain_name=testdomain.com')
        self.assertEqual(call_args[3], 'GET')

        # Validate response object
        self.assertEqual(self.mock_wallet_name.id, ret_val[0].id)
        self.assertEqual(self.mock_wallet_name.domain_name, ret_val[0].domain_name)
        self.assertEqual(self.mock_wallet_name.name, ret_val[0].name)
        self.assertEqual(self.mock_wallet_name.external_id, ret_val[0].external_id)
        self.assertDictEqual({'dgc': 'Dgccaddress', 'btc': '1btcaddress'}, ret_val[0].wallets)
        self.assertEqual('api_url', ret_val[0].api_url)
        self.assertEqual('api_key', ret_val[0].api_key)
        self.assertEqual('partner_id', ret_val[0].partner_id)

    def test_go_right_with_external_id(self):

        ret_val = self.netki.get_wallet_names(external_id='external_id')

        # Validate GET data
        self.assertEqual(1, self.mockSubmitRequest.call_count)
        call_args = self.mockSubmitRequest.call_args[0]
        self.assertEqual(call_args[0], self.netki.api_key)
        self.assertEqual(call_args[1], self.netki.partner_id)
        self.assertEqual(call_args[2], self.netki.api_url + '/v1/partner/walletname?external_id=external_id')
        self.assertEqual(call_args[3], 'GET')

        # Validate response object
        self.assertEqual(self.mock_wallet_name.id, ret_val[0].id)
        self.assertEqual(self.mock_wallet_name.domain_name, ret_val[0].domain_name)
        self.assertEqual(self.mock_wallet_name.name, ret_val[0].name)
        self.assertEqual(self.mock_wallet_name.external_id, ret_val[0].external_id)
        self.assertDictEqual({'dgc': 'Dgccaddress', 'btc': '1btcaddress'}, ret_val[0].wallets)
        self.assertEqual('api_url', ret_val[0].api_url)
        self.assertEqual('api_key', ret_val[0].api_key)
        self.assertEqual('partner_id', ret_val[0].partner_id)

    def test_go_right_with_domain_and_external_id(self):

        ret_val = self.netki.get_wallet_names(domain_name='testdomain.com', external_id='external_id')

        # Validate GET data
        self.assertEqual(1, self.mockSubmitRequest.call_count)
        call_args = self.mockSubmitRequest.call_args[0]
        self.assertEqual(call_args[0], self.netki.api_key)
        self.assertEqual(call_args[1], self.netki.partner_id)
        self.assertEqual(
            call_args[2],
            self.netki.api_url + '/v1/partner/walletname?domain_name=testdomain.com&external_id=external_id'
        )
        self.assertEqual(call_args[3], 'GET')

        # Validate response object
        self.assertEqual(self.mock_wallet_name.id, ret_val[0].id)
        self.assertEqual(self.mock_wallet_name.domain_name, ret_val[0].domain_name)
        self.assertEqual(self.mock_wallet_name.name, ret_val[0].name)
        self.assertEqual(self.mock_wallet_name.external_id, ret_val[0].external_id)
        self.assertDictEqual({'dgc': 'Dgccaddress', 'btc': '1btcaddress'}, ret_val[0].wallets)
        self.assertEqual('api_url', ret_val[0].api_url)
        self.assertEqual('api_key', ret_val[0].api_key)
        self.assertEqual('partner_id', ret_val[0].partner_id)

    def test_non_200_response(self):

        # Setup test case
        self.mockSubmitRequest.return_value.status_code = 404
        self.mock_response_obj.message = 'Domain not found'

        self.assertRaisesRegexp(Exception, 'Get WalletNames Failed! Domain not found', self.netki.get_wallet_names)

        # Validate GET data
        self.assertEqual(1, self.mockSubmitRequest.call_count)
        call_args = self.mockSubmitRequest.call_args[0]
        self.assertEqual(call_args[0], self.netki.api_key)
        self.assertEqual(call_args[1], self.netki.partner_id)
        self.assertEqual(call_args[2], self.netki.api_url + '/v1/partner/walletname')
        self.assertEqual(call_args[3], 'GET')

    def test_no_wallet_names_returned(self):

        # Setup test case
        self.mock_response_obj.wallet_name_count = 0

        self.assertEqual([], self.netki.get_wallet_names(domain_name='testdomain.com'))

        # Validate GET data
        self.assertEqual(1, self.mockSubmitRequest.call_count)
        call_args = self.mockSubmitRequest.call_args[0]
        self.assertEqual(call_args[0], self.netki.api_key)
        self.assertEqual(call_args[1], self.netki.partner_id)
        self.assertEqual(call_args[2], self.netki.api_url + '/v1/partner/walletname?domain_name=testdomain.com')
        self.assertEqual(call_args[3], 'GET')


class TestNetkiCreateWalletName(TestCase):
    def setUp(self):
        self.netki = Netki(
            partner_id='partner_id',
            api_key='api_key',
            api_url='api_url'
        )

    def test_go_right(self):

        ret_val = self.netki.create_wallet_name('testdomain.com', 'name', {'key': 'val'}, 'external_id')

        self.assertEqual('testdomain.com', ret_val.domain_name)
        self.assertEqual('name', ret_val.name)
        self.assertEqual({'key': 'val'}, ret_val.wallets)
        self.assertEqual('external_id', ret_val.external_id)
        self.assertEqual('api_url', ret_val.api_url)
        self.assertEqual('api_key', ret_val.api_key)
        self.assertEqual('partner_id', ret_val.partner_id)

