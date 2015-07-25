# coding=utf-8
__author__ = 'frank'


import json
from mock import Mock, patch
from unittest import TestCase

from netki import Netki, process_request, WalletName


class TestProcessRequest(TestCase):
    def setUp(self):
        self.patcher1 = patch('netki.requests')
        self.mockRequests = self.patcher1.start()

        self.headers = {
            'X-Partner-ID': 'partner_id',
            'Content-Type': 'application/json',
            'Authorization': 'api_key'
        }

        self.request_data = {'key': 'val'}

        # Setup go right condition
        self.response_data = {'success': True}
        self.mockRequests.request.return_value.json.return_value = self.response_data
        self.mockRequests.request.return_value.status_code = 200

    def tearDown(self):
        self.patcher1.stop()

    def test_get_method_go_right(self):

        ret_val = process_request('api_key', 'partner_id', 'uri', 'GET')

        # Validate submit_request data
        self.assertEqual(1, self.mockRequests.request.call_count)

        call_args = self.mockRequests.request.call_args[1]
        self.assertIsNone(call_args.get('data'))
        self.assertDictEqual(self.headers, call_args.get('headers'))
        self.assertEqual('GET', call_args.get('method'))
        self.assertEqual('uri', call_args.get('url'))

        # Validate response
        self.assertDictEqual(ret_val, self.response_data)

    def test_post_method_go_right(self):

        ret_val = process_request('api_key', 'partner_id', 'uri', 'POST', json.dumps(self.request_data))

        # Validate submit_request data
        self.assertEqual(1, self.mockRequests.request.call_count)

        call_args = self.mockRequests.request.call_args[1]
        self.assertEqual(json.dumps(self.request_data), call_args.get('data'))
        self.assertDictEqual(self.headers, call_args.get('headers'))
        self.assertEqual('POST', call_args.get('method'))
        self.assertEqual('uri', call_args.get('url'))

        # Validate response
        self.assertDictEqual(ret_val, self.response_data)

    def test_put_method_go_right(self):

        ret_val = process_request('api_key', 'partner_id', 'uri', 'PUT', json.dumps(self.request_data))

        # Validate submit_request data
        self.assertEqual(1, self.mockRequests.request.call_count)

        call_args = self.mockRequests.request.call_args[1]
        self.assertEqual(json.dumps(self.request_data), call_args.get('data'))
        self.assertDictEqual(self.headers, call_args.get('headers'))
        self.assertEqual('PUT', call_args.get('method'))
        self.assertEqual('uri', call_args.get('url'))

        # Validate response
        self.assertDictEqual(ret_val, self.response_data)

    def test_delete_method_go_right(self):

        # Setup Test case
        self.mockRequests.request.return_value.status_code = 204

        ret_val = process_request('api_key', 'partner_id', 'uri', 'DELETE')

        # Validate submit_request data
        self.assertEqual(1, self.mockRequests.request.call_count)

        call_args = self.mockRequests.request.call_args[1]
        self.assertIsNone(call_args.get('data'))
        self.assertDictEqual(self.headers, call_args.get('headers'))
        self.assertEqual('DELETE', call_args.get('method'))
        self.assertEqual('uri', call_args.get('url'))

        # Validate response
        self.assertDictEqual(ret_val, {})

    def test_unsupported_method(self):

        self.assertRaisesRegexp(
            Exception,
            'Unsupported HTTP method: PATCH',
            process_request,
            'api_key',
            'partner_id',
            'uri',
            'PATCH',
            json.dumps(self.request_data)
        )

        # Validate submit_request data
        self.assertEqual(0, self.mockRequests.request.call_count)

    def test_delete_non_204_response(self):

        # Setup Test case
        self.mockRequests.request.return_value.status_code = 200

        ret_val = process_request('api_key', 'partner_id', 'uri', 'DELETE')

        # Validate submit_request data
        self.assertEqual(1, self.mockRequests.request.call_count)

        call_args = self.mockRequests.request.call_args[1]
        self.assertIsNone(call_args.get('data'))
        self.assertDictEqual(self.headers, call_args.get('headers'))
        self.assertEqual('DELETE', call_args.get('method'))
        self.assertEqual('uri', call_args.get('url'))

        # Validate response
        self.assertDictEqual(ret_val, self.response_data)

    def test_400_status_code(self):

        # Setup Test case
        self.mockRequests.request.return_value.status_code = 400
        self.mockRequests.request.return_value.json.return_value = {'message': 'Bad request for sure'}

        self.assertRaisesRegexp(
            Exception,
            'Bad request for sure',
            process_request,
            'api_key',
            'partner_id',
            'uri',
            'POST',
            self.request_data
        )

        # Validate submit_request data
        self.assertEqual(1, self.mockRequests.request.call_count)

        call_args = self.mockRequests.request.call_args[1]
        self.assertEqual(self.request_data, call_args.get('data'))
        self.assertDictEqual(self.headers, call_args.get('headers'))
        self.assertEqual('POST', call_args.get('method'))
        self.assertEqual('uri', call_args.get('url'))

    def test_rdata_success_false_no_failures(self):

        # Setup Test case
        self.mockRequests.request.return_value.json.return_value = {
            'success': False,
            'message': 'Bad request for sure'
        }

        self.assertRaisesRegexp(
            Exception,
            'Bad request for sure',
            process_request,
            'api_key',
            'partner_id',
            'uri',
            'POST',
            self.request_data
        )

        # Validate submit_request data
        self.assertEqual(1, self.mockRequests.request.call_count)

        call_args = self.mockRequests.request.call_args[1]
        self.assertEqual(self.request_data, call_args.get('data'))
        self.assertDictEqual(self.headers, call_args.get('headers'))
        self.assertEqual('POST', call_args.get('method'))
        self.assertEqual('uri', call_args.get('url'))

    def test_rdata_success_false_with_failures(self):

        # Setup Test case
        self.mockRequests.request.return_value.json.return_value = {
            'success': False,
            'message': 'Bad request for sure',
            'failures': [
                {'message': 'error 1'},
                {'message': 'error 2'}
            ]
        }

        self.assertRaisesRegexp(
            Exception,
            'Bad request for sure \[FAILURES: error 1, error 2\]',
            process_request,
            'api_key',
            'partner_id',
            'uri',
            'POST',
            self.request_data
        )

        # Validate submit_request data
        self.assertEqual(1, self.mockRequests.request.call_count)

        call_args = self.mockRequests.request.call_args[1]
        self.assertEqual(self.request_data, call_args.get('data'))
        self.assertDictEqual(self.headers, call_args.get('headers'))
        self.assertEqual('POST', call_args.get('method'))
        self.assertEqual('uri', call_args.get('url'))


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
        self.patcher1 = patch('netki.process_request')
        self.mockProcessRequest = self.patcher1.start()

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
        self.mockProcessRequest.return_value = self.response_obj

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

        self.assertEqual(1, self.mockProcessRequest.call_count)
        self.assertEqual(self.wallet_name.id, self.mock_wallet_name_response_obj.id)

        call_args = self.mockProcessRequest.call_args[0]
        self.assertEqual(self.wallet_name.api_key, call_args[0])
        self.assertEqual(self.wallet_name.partner_id, call_args[1])
        self.assertEqual(self.wallet_name.api_url + '/v1/partner/walletname', call_args[2])
        self.assertEqual('PUT', call_args[3])
        self.assertEqual(json.dumps(self.mock_wn_api_data), call_args[4])

    def test_wallet_create_go_right(self):

        # Setup test case
        self.wallet_name.id = None
        del self.mock_wn_api_data.get('wallet_names')[0]['id']

        self.wallet_name.save()

        self.assertEqual(1, self.mockProcessRequest.call_count)
        self.assertEqual(self.wallet_name.id, self.mock_wallet_name_response_obj.id)

        call_args = self.mockProcessRequest.call_args[0]
        self.assertEqual(self.wallet_name.api_key, call_args[0])
        self.assertEqual(self.wallet_name.partner_id, call_args[1])
        self.assertEqual(self.wallet_name.api_url + '/v1/partner/walletname', call_args[2])
        self.assertEqual('POST', call_args[3])
        self.assertEqual(json.dumps(self.mock_wn_api_data), call_args[4])


class TestWalletNameDelete(TestCase):
    def setUp(self):
        self.patcher1 = patch('netki.process_request')
        self.mockProcessRequest = self.patcher1.start()

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
        self.mockProcessRequest.return_value.status_code = 204
        self.response_obj = Mock()
        self.mockProcessRequest.return_value = self.response_obj

    def tearDown(self):
        self.patcher1.stop()

    def test_go_right(self):

        self.assertIsNone(self.wallet_name.delete())

        # Validate delete data
        call_args = self.mockProcessRequest.call_args[0]
        self.assertEqual(self.wallet_name.api_key, call_args[0])
        self.assertEqual(self.wallet_name.partner_id, call_args[1])
        self.assertEqual(self.wallet_name.api_url + '/v1/partner/walletname', call_args[2])
        self.assertEqual('DELETE', call_args[3])
        self.assertEqual(json.dumps(self.mock_wn_api_data), call_args[4])


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
        self.patcher1 = patch('netki.process_request')
        self.mockProcessRequest = self.patcher1.start()

        self.netki = Netki(
            partner_id='partner_id',
            api_key='api_key',
            api_url='api_url'
        )

        # Setup Response object
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

        self.mockProcessRequest.return_value = self.mock_response_obj

    def tearDown(self):
        self.patcher1.stop()

    def test_go_right_no_args(self):

        ret_val = self.netki.get_wallet_names()

        # Validate GET data
        self.assertEqual(1, self.mockProcessRequest.call_count)
        call_args = self.mockProcessRequest.call_args[0]
        self.assertEqual(self.netki.api_key, call_args[0])
        self.assertEqual(self.netki.partner_id, call_args[1])
        self.assertEqual(self.netki.api_url + '/v1/partner/walletname', call_args[2])
        self.assertEqual('GET', call_args[3])

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
        self.assertEqual(1, self.mockProcessRequest.call_count)
        call_args = self.mockProcessRequest.call_args[0]
        self.assertEqual(self.netki.api_key, call_args[0])
        self.assertEqual(self.netki.partner_id, call_args[1])
        self.assertEqual(self.netki.api_url + '/v1/partner/walletname?domain_name=testdomain.com', call_args[2])
        self.assertEqual('GET', call_args[3])

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
        self.assertEqual(1, self.mockProcessRequest.call_count)
        call_args = self.mockProcessRequest.call_args[0]
        self.assertEqual(self.netki.api_key, call_args[0])
        self.assertEqual(self.netki.partner_id, call_args[1])
        self.assertEqual(self.netki.api_url + '/v1/partner/walletname?external_id=external_id', call_args[2])
        self.assertEqual('GET', call_args[3])

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
        self.assertEqual(1, self.mockProcessRequest.call_count)
        call_args = self.mockProcessRequest.call_args[0]
        self.assertEqual(self.netki.api_key, call_args[0])
        self.assertEqual(self.netki.partner_id, call_args[1])
        self.assertEqual(
            self.netki.api_url + '/v1/partner/walletname?domain_name=testdomain.com&external_id=external_id',
            call_args[2]
        )
        self.assertEqual('GET', call_args[3])

        # Validate response object
        self.assertEqual(self.mock_wallet_name.id, ret_val[0].id)
        self.assertEqual(self.mock_wallet_name.domain_name, ret_val[0].domain_name)
        self.assertEqual(self.mock_wallet_name.name, ret_val[0].name)
        self.assertEqual(self.mock_wallet_name.external_id, ret_val[0].external_id)
        self.assertDictEqual({'dgc': 'Dgccaddress', 'btc': '1btcaddress'}, ret_val[0].wallets)
        self.assertEqual('api_url', ret_val[0].api_url)
        self.assertEqual('api_key', ret_val[0].api_key)
        self.assertEqual('partner_id', ret_val[0].partner_id)

    def test_no_wallet_names_returned(self):

        # Setup test case
        self.mock_response_obj.wallet_name_count = 0

        self.assertListEqual([], self.netki.get_wallet_names(domain_name='testdomain.com'))

        # Validate GET data
        self.assertEqual(1, self.mockProcessRequest.call_count)
        call_args = self.mockProcessRequest.call_args[0]
        self.assertEqual(self.netki.api_key, call_args[0])
        self.assertEqual(self.netki.partner_id, call_args[1])
        self.assertEqual(self.netki.api_url + '/v1/partner/walletname?domain_name=testdomain.com', call_args[2])
        self.assertEqual('GET', call_args[3])


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

    def test_go_right_unicode(self):

        ret_val = self.netki.create_wallet_name(u'ἩἸ', 'name', {'key': 'val'}, 'external_id')

        self.assertEqual(u'\u1f29\u1f38', ret_val.domain_name)
        self.assertEqual('name', ret_val.name)
        self.assertEqual({'key': 'val'}, ret_val.wallets)
        self.assertEqual('external_id', ret_val.external_id)
        self.assertEqual('api_url', ret_val.api_url)
        self.assertEqual('api_key', ret_val.api_key)
        self.assertEqual('partner_id', ret_val.partner_id)

    def test_go_right_unicode_2(self):

        ret_val = self.netki.create_wallet_name(u'\u1f29\u1f38', 'name', {'key': 'val'}, 'external_id')

        self.assertEqual(u'\u1f29\u1f38', ret_val.domain_name)
        self.assertEqual('name', ret_val.name)
        self.assertEqual({'key': 'val'}, ret_val.wallets)
        self.assertEqual('external_id', ret_val.external_id)
        self.assertEqual('api_url', ret_val.api_url)
        self.assertEqual('api_key', ret_val.api_key)
        self.assertEqual('partner_id', ret_val.partner_id)


class TestCreatePartner(TestCase):
    def setUp(self):
        self.patcher1 = patch('netki.process_request')
        self.mockProcessRequest = self.patcher1.start()

        self.netki = Netki(
            partner_id='partner_id',
            api_key='api_key',
            api_url='api_url'
        )

        self.response_data = {'name': 'partner_name', 'id': 'partner_id'}

        self.mockProcessRequest.return_value.partner = self.response_data

    def tearDown(self):
        self.patcher1.stop()

    def test_go_right(self):

        ret_val = self.netki.create_partner('partner_name')

        # Validate request data
        self.assertEqual(1, self.mockProcessRequest.call_count)
        call_args = self.mockProcessRequest.call_args[0]
        self.assertEqual(self.netki.api_key, call_args[0])
        self.assertEqual(self.netki.partner_id, call_args[1])
        self.assertEqual(self.netki.api_url + '/v1/admin/partner/partner_name', call_args[2])
        self.assertEqual('POST', call_args[3])

        # Validate return data
        self.assertEqual(self.response_data, ret_val)


class TestGetPartners(TestCase):
    def setUp(self):
        self.patcher1 = patch('netki.process_request')
        self.mockProcessRequest = self.patcher1.start()

        self.netki = Netki(
            partner_id='partner_id',
            api_key='api_key',
            api_url='api_url'
        )

        self.response_data = {'partners': [
            {'name': 'partner1', 'id': 'id1'},
            {'name': 'partner2', 'id': 'id2'}
        ]}

        self.mockProcessRequest.return_value = self.response_data

    def tearDown(self):
        self.patcher1.stop()

    def test_go_right(self):

        ret_val = self.netki.get_partners()

        # Validate request data
        self.assertEqual(1, self.mockProcessRequest.call_count)
        call_args = self.mockProcessRequest.call_args[0]
        self.assertEqual(self.netki.api_key, call_args[0])
        self.assertEqual(self.netki.partner_id, call_args[1])
        self.assertEqual(self.netki.api_url + '/v1/admin/partner', call_args[2])
        self.assertEqual('GET', call_args[3])

        # Validate return data
        self.assertEqual(self.response_data, ret_val)


class TestDeletePartner(TestCase):
    def setUp(self):
        self.patcher1 = patch('netki.process_request')
        self.mockProcessRequest = self.patcher1.start()

        self.netki = Netki(
            partner_id='partner_id',
            api_key='api_key',
            api_url='api_url'
        )

    def tearDown(self):
        self.patcher1.stop()

    def test_go_right(self):

        ret_val = self.netki.delete_partner('partner_name')

        # Validate request data
        self.assertEqual(1, self.mockProcessRequest.call_count)
        call_args = self.mockProcessRequest.call_args[0]
        self.assertEqual(self.netki.api_key, call_args[0])
        self.assertEqual(self.netki.partner_id, call_args[1])
        self.assertEqual(self.netki.api_url + '/v1/admin/partner/partner_name', call_args[2])
        self.assertEqual('DELETE', call_args[3])

        # Validate return data
        self.assertIsNone(ret_val)


class TestCreatePartnerDomain(TestCase):
    def setUp(self):
        self.patcher1 = patch('netki.process_request')
        self.mockProcessRequest = self.patcher1.start()

        self.netki = Netki(
            partner_id='partner_id',
            api_key='api_key',
            api_url='api_url'
        )

        self.response_data = {'domain_name': 'domain_name'}

        self.mockProcessRequest.return_value = self.response_data

    def test_go_right_partner_domain(self):

        ret_val = self.netki.create_partner_domain('domain_name')

        # Validate request data
        self.assertEqual(1, self.mockProcessRequest.call_count)
        call_args = self.mockProcessRequest.call_args[0]
        self.assertEqual(self.netki.api_key, call_args[0])
        self.assertEqual(self.netki.partner_id, call_args[1])
        self.assertEqual(self.netki.api_url + '/v1/partner/domain/domain_name', call_args[2])
        self.assertEqual('POST', call_args[3])

        # Validate return data
        self.assertEqual(self.response_data, ret_val)

    def test_go_right_sub_partner_domain(self):

        ret_val = self.netki.create_partner_domain('domain_name', 'partner_id')

        # Validate request data
        self.assertEqual(1, self.mockProcessRequest.call_count)
        call_args = self.mockProcessRequest.call_args[0]
        self.assertEqual(self.netki.api_key, call_args[0])
        self.assertEqual(self.netki.partner_id, call_args[1])
        self.assertEqual(self.netki.api_url + '/v1/partner/domain/domain_name', call_args[2])
        self.assertEqual('POST', call_args[3])
        self.assertEqual(json.dumps({'partner_id': 'partner_id'}), call_args[4])

        # Validate return data
        self.assertEqual(self.response_data, ret_val)


class TestGetDomains(TestCase):
    def setUp(self):
        self.patcher1 = patch('netki.process_request')
        self.mockProcessRequest = self.patcher1.start()

        self.netki = Netki(
            partner_id='partner_id',
            api_key='api_key',
            api_url='api_url'
        )

        self.response_data = {'domains': [
            {'domain_name': 'testdomain1.com'},
            {'domain_name': 'testdomain2.com'},
        ]}

        self.mockProcessRequest.return_value = self.response_data

    def tearDown(self):
        self.patcher1.stop()

    def test_go_right(self):

        ret_val = self.netki.get_domains()

        # Validate request data
        self.assertEqual(1, self.mockProcessRequest.call_count)
        call_args = self.mockProcessRequest.call_args[0]
        self.assertEqual(self.netki.api_key, call_args[0])
        self.assertEqual(self.netki.partner_id, call_args[1])
        self.assertEqual(self.netki.api_url + '/api/domain', call_args[2])
        self.assertEqual('GET', call_args[3])

        # Validate return data
        self.assertEqual(self.response_data, ret_val)


class TestGetDomainStatus(TestCase):
    def setUp(self):
        self.patcher1 = patch('netki.process_request')
        self.mockProcessRequest = self.patcher1.start()

        self.netki = Netki(
            partner_id='partner_id',
            api_key='api_key',
            api_url='api_url'
        )

        self.response_data = {'domains': [
            {'domain_name': 'testdomain1.com', 'status': 'complete'},
        ]}

        self.mockProcessRequest.return_value = self.response_data

    def tearDown(self):
        self.patcher1.stop()

    def test_go_right(self):

        ret_val = self.netki.get_domain_status('domain_name')

        # Validate request data
        self.assertEqual(1, self.mockProcessRequest.call_count)
        call_args = self.mockProcessRequest.call_args[0]
        self.assertEqual(self.netki.api_key, call_args[0])
        self.assertEqual(self.netki.partner_id, call_args[1])
        self.assertEqual(self.netki.api_url + '/v1/partner/domain/domain_name', call_args[2])
        self.assertEqual('GET', call_args[3])

        # Validate return data
        self.assertEqual(self.response_data, ret_val)


class TestGetDomainDNSSECDetails(TestCase):
    def setUp(self):
        self.patcher1 = patch('netki.process_request')
        self.mockProcessRequest = self.patcher1.start()

        self.netki = Netki(
            partner_id='partner_id',
            api_key='api_key',
            api_url='api_url'
        )

        self.response_data = {'domains': [
            {'public_key_signing_key': 'PKSK'},
        ]}

        self.mockProcessRequest.return_value = self.response_data

    def tearDown(self):
        self.patcher1.stop()

    def test_go_right(self):

        ret_val = self.netki.get_domain_dnssec_details('domain_name')

        # Validate request data
        self.assertEqual(1, self.mockProcessRequest.call_count)
        call_args = self.mockProcessRequest.call_args[0]
        self.assertEqual(self.netki.api_key, call_args[0])
        self.assertEqual(self.netki.partner_id, call_args[1])
        self.assertEqual(self.netki.api_url + '/v1/partner/domain/dnssec/domain_name', call_args[2])
        self.assertEqual('GET', call_args[3])

        # Validate return data
        self.assertEqual(self.response_data, ret_val)


class TestDeletePartnerDomain(TestCase):
    def setUp(self):
        self.patcher1 = patch('netki.process_request')
        self.mockProcessRequest = self.patcher1.start()

        self.netki = Netki(
            partner_id='partner_id',
            api_key='api_key',
            api_url='api_url'
        )

    def test_go_right(self):

        ret_val = self.netki.delete_partner_domain('domain_name')

        # Validate request data
        self.assertEqual(1, self.mockProcessRequest.call_count)
        call_args = self.mockProcessRequest.call_args[0]
        self.assertEqual(self.netki.api_key, call_args[0])
        self.assertEqual(self.netki.partner_id, call_args[1])
        self.assertEqual(self.netki.api_url + '/v1/partner/domain/domain_name', call_args[2])
        self.assertEqual('DELETE', call_args[3])

        # Validate return data
        self.assertIsNone(ret_val)
