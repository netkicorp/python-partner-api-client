__author__ = 'frank'

from mock import Mock, patch
from unittest import TestCase

from WalletName import WalletName


class TestWalletNameInit(TestCase):
    def setUp(self):
        self.wallet_name = WalletName(
            domain_name='testdomain.com',
            name='myname',
            external_id='external_id',
            id='id'
        )

    def test_init_values(self):
        self.assertEqual('testdomain.com', self.wallet_name.domain_name)
        self.assertEqual('myname', self.wallet_name.name)
        self.assertEqual('external_id', self.wallet_name.external_id)
        self.assertEqual('id', self.wallet_name.id)
        self.assertDictEqual({}, self.wallet_name.wallets)


class TestWalletNameGettersSetters(TestCase):
    def setUp(self):
        self.wallet_name = WalletName(
            domain_name='testdomain.com',
            name='myname',
            external_id='external_id'
        )

        self.wallet_name.set_currency_address('currency', 'wallet_address')

    def test_get_used_currencies(self):

        self.assertDictEqual({'currency': 'wallet_address'}, self.wallet_name.get_used_currencies())

    def test_get_wallet_address(self):

        self.assertEqual('wallet_address', self.wallet_name.get_wallet_address('currency'))

    def test_set_currency_address(self):

        self.wallet_name.set_currency_address('currency2', 'wallet_address2')

        self.assertDictEqual(
            {'currency': 'wallet_address', 'currency2': 'wallet_address2'},
            self.wallet_name.wallets
        )

    def test_remove_currency_address(self):

        self.wallet_name.remove_currency_address('currency')

        self.assertEqual({}, self.wallet_name.wallets)


class TestWalletNameSave(TestCase):
    def setUp(self):
        self.patcher1 = patch('WalletName.process_request')
        self.mockProcessRequest = self.patcher1.start()

        self.wallet_name = WalletName(
            domain_name='testdomain.com',
            name='myname',
            external_id='external_id',
            id='id'
        )
        self.wallet_name.set_currency_address('currency', 'wallet_address')

        # Setup Wallet Name object data
        self.wallet_name.id = 'id'
        self.wallet_name.domain_name = 'testdomain.com'
        self.wallet_name.name = 'name'
        self.wallet_name.wallets = {'currency': 'wallet_address'}
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
        self.mock_wallet_name_response_obj.wallets = {'currency': 'wallet_address'}
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
                            'currency': 'currency',
                            'wallet_address': 'wallet_address'
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
        self.assertEqual(self.wallet_name.netki_client, call_args[0])
        self.assertEqual('/v1/partner/walletname', call_args[1])
        self.assertEqual('PUT', call_args[2])
        self.assertEqual(self.mock_wn_api_data, call_args[3])

    def test_wallet_create_go_right(self):

        # Setup test case
        self.wallet_name.id = None
        del self.mock_wn_api_data.get('wallet_names')[0]['id']

        self.wallet_name.save()

        self.assertEqual(1, self.mockProcessRequest.call_count)
        self.assertEqual(self.wallet_name.id, self.mock_wallet_name_response_obj.id)

        call_args = self.mockProcessRequest.call_args[0]
        self.assertEqual(self.wallet_name.netki_client, call_args[0])
        self.assertEqual('/v1/partner/walletname', call_args[1])
        self.assertEqual('POST', call_args[2])
        self.assertEqual(self.mock_wn_api_data, call_args[3])


class TestWalletNameDelete(TestCase):
    def setUp(self):
        self.patcher1 = patch('WalletName.process_request')
        self.mockProcessRequest = self.patcher1.start()

        self.wallet_name = WalletName(
            id='id',
            domain_name='testdomain.com',
            name='myname',
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
        self.assertEqual(self.wallet_name.netki_client, call_args[0])
        self.assertEqual('/v1/partner/walletname', call_args[1])
        self.assertEqual('DELETE', call_args[2])
        self.assertEqual(self.mock_wn_api_data, call_args[3])

    def test_missing_id(self):

        # Setup Test Case
        self.wallet_name.id = None

        self.assertRaisesRegexp(
            Exception,
            '^Unable to Delete Object that Does Not Exist Remotely$',
            self.wallet_name.delete
        )
