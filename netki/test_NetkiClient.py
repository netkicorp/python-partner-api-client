# coding=utf-8
__author__ = 'frank'

from attrdict import AttrDict
from mock import Mock, patch
from unittest import TestCase

from NetkiClient import Netki


class TestNetkiInit(TestCase):
    def setUp(self):
        pass

    def test_go_right_api_key_auth(self):

        self.netki = Netki(
            partner_id='partner_id',
            api_key='api_key',
            api_url='api_url'
        )

        self.assertEqual('partner_id', self.netki.partner_id)
        self.assertEqual('api_key', self.netki.api_key)
        self.assertEqual('api_url', self.netki.api_url)
        self.assertEqual('api_key', self.netki._auth_type)

    def test_go_right_distributed_auth(self):

        self.netki = Netki.distributed_api_access(
            key_signing_key='ksk',
            signed_user_key='suk',
            user_key='uk',
            api_url='api_url'
        )

        self.assertEqual('ksk', self.netki.key_signing_key)
        self.assertEqual('suk', self.netki.signed_user_key)
        self.assertEqual('uk', self.netki.user_key)
        self.assertIsNone(self.netki.partner_id)
        self.assertIsNone(self.netki.api_key)
        self.assertEqual('api_url', self.netki.api_url)
        self.assertEqual('distributed', self.netki._auth_type)

    def test_go_right_certificate_auth(self):

        self.netki = Netki.certificate_api_access(
            user_key='uk',
            partner_id='partner_id',
            api_url='api_url'
        )

        self.assertFalse(hasattr(self.netki, 'key_signing_key'))
        self.assertFalse(hasattr(self.netki, 'signed_user_key'))
        self.assertEqual('uk', self.netki.user_key)
        self.assertEqual('partner_id', self.netki.partner_id)
        self.assertIsNone(self.netki.api_key)
        self.assertEqual('api_url', self.netki.api_url)
        self.assertEqual('certificate', self.netki._auth_type)

    def test_distributed_auth_missing_ksk(self):

        self.assertRaisesRegexp(
            ValueError,
            '^key_signing_key Required for Distributed API Access$',
            Netki.distributed_api_access,
            '',
            'suk',
            'uk',
            'api_url'
        )

    def test_distributed_auth_missing_suk(self):

        self.assertRaisesRegexp(
            ValueError,
            '^signed_user_key Required for Distributed API Access$',
            Netki.distributed_api_access,
            'ksk',
            '',
            'uk',
            'api_url'
        )

    def test_distributed_auth_missing_uk(self):

        self.assertRaisesRegexp(
            ValueError,
            '^user_key Required for Distributed API Access$',
            Netki.distributed_api_access,
            'ksk',
            'suk',
            '',
            'api_url'
        )

    def test_certificate_auth_missing_uk(self):

        self.assertRaisesRegexp(
            ValueError,
            '^user_key Required for Certificate API Access$',
            Netki.certificate_api_access,
            '',
            'partner_id'
        )

    def test_certificate_auth_missing_partner_id(self):

        self.assertRaisesRegexp(
            ValueError,
            '^partner_id Required for Certificate API Access$',
            Netki.certificate_api_access,
            'uk',
            ''
        )


class TestNetkiGetWalletNames(TestCase):
    def setUp(self):
        self.patcher1 = patch('NetkiClient.process_request')
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
        self.assertEqual(self.netki, call_args[0])
        self.assertEqual('/v1/partner/walletname', call_args[1])
        self.assertEqual('GET', call_args[2])

        # Validate response object
        self.assertEqual(self.mock_wallet_name.id, ret_val[0].id)
        self.assertEqual(self.mock_wallet_name.domain_name, ret_val[0].domain_name)
        self.assertEqual(self.mock_wallet_name.name, ret_val[0].name)
        self.assertEqual(self.mock_wallet_name.external_id, ret_val[0].external_id)
        self.assertDictEqual({'dgc': 'Dgccaddress', 'btc': '1btcaddress'}, ret_val[0].wallets)
        self.assertEqual(self.netki, ret_val[0].netki_client)

    def test_go_right_with_domain_name(self):

        ret_val = self.netki.get_wallet_names(domain_name='testdomain.com')

        # Validate GET data
        self.assertEqual(1, self.mockProcessRequest.call_count)
        call_args = self.mockProcessRequest.call_args[0]
        self.assertEqual(self.netki, call_args[0])
        self.assertEqual('/v1/partner/walletname?domain_name=testdomain.com', call_args[1])
        self.assertEqual('GET', call_args[2])

        # Validate response object
        self.assertEqual(self.mock_wallet_name.id, ret_val[0].id)
        self.assertEqual(self.mock_wallet_name.domain_name, ret_val[0].domain_name)
        self.assertEqual(self.mock_wallet_name.name, ret_val[0].name)
        self.assertEqual(self.mock_wallet_name.external_id, ret_val[0].external_id)
        self.assertDictEqual({'dgc': 'Dgccaddress', 'btc': '1btcaddress'}, ret_val[0].wallets)
        self.assertEqual(self.netki, ret_val[0].netki_client)

    def test_go_right_with_external_id(self):

        ret_val = self.netki.get_wallet_names(external_id='external_id')

        # Validate GET data
        self.assertEqual(1, self.mockProcessRequest.call_count)
        call_args = self.mockProcessRequest.call_args[0]
        self.assertEqual(self.netki, call_args[0])
        self.assertEqual('/v1/partner/walletname?external_id=external_id', call_args[1])
        self.assertEqual('GET', call_args[2])

        # Validate response object
        self.assertEqual(self.mock_wallet_name.id, ret_val[0].id)
        self.assertEqual(self.mock_wallet_name.domain_name, ret_val[0].domain_name)
        self.assertEqual(self.mock_wallet_name.name, ret_val[0].name)
        self.assertEqual(self.mock_wallet_name.external_id, ret_val[0].external_id)
        self.assertDictEqual({'dgc': 'Dgccaddress', 'btc': '1btcaddress'}, ret_val[0].wallets)
        self.assertEqual(self.netki, ret_val[0].netki_client)

    def test_go_right_with_domain_and_external_id(self):

        ret_val = self.netki.get_wallet_names(domain_name='testdomain.com', external_id='external_id')

        # Validate GET data
        self.assertEqual(1, self.mockProcessRequest.call_count)
        call_args = self.mockProcessRequest.call_args[0]
        self.assertEqual(self.netki, call_args[0])
        self.assertEqual(
            '/v1/partner/walletname?domain_name=testdomain.com&external_id=external_id',
            call_args[1]
        )
        self.assertEqual('GET', call_args[2])

        # Validate response object
        self.assertEqual(self.mock_wallet_name.id, ret_val[0].id)
        self.assertEqual(self.mock_wallet_name.domain_name, ret_val[0].domain_name)
        self.assertEqual(self.mock_wallet_name.name, ret_val[0].name)
        self.assertEqual(self.mock_wallet_name.external_id, ret_val[0].external_id)
        self.assertDictEqual({'dgc': 'Dgccaddress', 'btc': '1btcaddress'}, ret_val[0].wallets)
        self.assertEqual(self.netki, ret_val[0].netki_client)

    def test_no_wallet_names_returned(self):

        # Setup test case
        self.mock_response_obj.wallet_name_count = 0

        self.assertListEqual([], self.netki.get_wallet_names(domain_name='testdomain.com'))

        # Validate GET data
        self.assertEqual(1, self.mockProcessRequest.call_count)
        call_args = self.mockProcessRequest.call_args[0]
        self.assertEqual(self.netki, call_args[0])
        self.assertEqual('/v1/partner/walletname?domain_name=testdomain.com', call_args[1])
        self.assertEqual('GET', call_args[2])


class TestNetkiCreateWalletName(TestCase):
    def setUp(self):
        self.netki = Netki(
            partner_id='partner_id',
            api_key='api_key',
            api_url='api_url'
        )

    def test_go_right(self):

        ret_val = self.netki.create_wallet_name('testdomain.com', 'name', 'external_id', 'currency', 'address')

        self.assertEqual('testdomain.com', ret_val.domain_name)
        self.assertEqual('name', ret_val.name)
        self.assertEqual({'currency': 'address'}, ret_val.wallets)
        self.assertEqual('external_id', ret_val.external_id)
        self.assertEqual(self.netki, ret_val.netki_client)

    def test_go_right_unicode(self):

        ret_val = self.netki.create_wallet_name(u'ἩἸ', 'name', 'external_id', 'currency', 'address')

        self.assertEqual(u'\u1f29\u1f38', ret_val.domain_name)
        self.assertEqual('name', ret_val.name)
        self.assertEqual({'currency': 'address'}, ret_val.wallets)
        self.assertEqual('external_id', ret_val.external_id)
        self.assertEqual(self.netki, ret_val.netki_client)

    def test_go_right_unicode_2(self):

        ret_val = self.netki.create_wallet_name(u'\u1f29\u1f38', 'name', 'external_id', 'currency', 'address')

        self.assertEqual(u'\u1f29\u1f38', ret_val.domain_name)
        self.assertEqual('name', ret_val.name)
        self.assertEqual({'currency': 'address'}, ret_val.wallets)
        self.assertEqual('external_id', ret_val.external_id)
        self.assertEqual(self.netki, ret_val.netki_client)


class TestGetPartners(TestCase):
    def setUp(self):
        self.patcher1 = patch('NetkiClient.process_request')
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

        self.mockProcessRequest.return_value = AttrDict(self.response_data)

    def tearDown(self):
        self.patcher1.stop()

    def test_go_right(self):

        ret_val = self.netki.get_partners()

        # Validate request data
        self.assertEqual(1, self.mockProcessRequest.call_count)
        call_args = self.mockProcessRequest.call_args[0]
        self.assertEqual(self.netki, call_args[0])
        self.assertEqual('/v1/admin/partner', call_args[1])
        self.assertEqual('GET', call_args[2])

        # Validate return data
        self.assertEqual('id1', ret_val[0].id)
        self.assertEqual('partner1', ret_val[0].name)
        self.assertEqual(self.netki, ret_val[0].netki_client)
        self.assertEqual('id2', ret_val[1].id)
        self.assertEqual('partner2', ret_val[1].name)
        self.assertEqual(self.netki, ret_val[1].netki_client)


class TestCreatePartner(TestCase):
    def setUp(self):
        self.patcher1 = patch('NetkiClient.process_request')
        self.mockProcessRequest = self.patcher1.start()

        self.netki = Netki(
            partner_id='partner_id',
            api_key='api_key',
            api_url='api_url'
        )

        self.response_data = {'name': 'partner_name', 'id': 'partner_id'}

        self.mockProcessRequest.return_value.partner = AttrDict(self.response_data)

    def tearDown(self):
        self.patcher1.stop()

    def test_go_right(self):

        ret_val = self.netki.create_partner('partner_name')

        # Validate request data
        self.assertEqual(1, self.mockProcessRequest.call_count)
        call_args = self.mockProcessRequest.call_args[0]
        self.assertEqual(self.netki, call_args[0])
        self.assertEqual('/v1/admin/partner/partner_name', call_args[1])
        self.assertEqual('POST', call_args[2])

        # Validate return data
        self.assertEqual('partner_id', ret_val.id)
        self.assertEqual('partner_name', ret_val.name)
        self.assertEqual(self.netki, ret_val.netki_client)


class TestGetDomains(TestCase):
    def setUp(self):
        self.patcher1 = patch('NetkiClient.process_request')
        self.mockProcessRequest = self.patcher1.start()

        self.netki = Netki(
            partner_id='partner_id',
            api_key='api_key',
            api_url='api_url'
        )

        self.response_data = {'domains': [{'domain_name': 'testdomain1.com'},]}

        self.mockProcessRequest.return_value = AttrDict(self.response_data)

    def tearDown(self):
        self.patcher1.stop()

    def test_go_right(self):

        ret_val = self.netki.get_domains()

        # Validate request data
        self.assertEqual(1, self.mockProcessRequest.call_count)
        call_args = self.mockProcessRequest.call_args[0]
        self.assertEqual(self.netki, call_args[0])
        self.assertEqual('/api/domain', call_args[1])
        self.assertEqual('GET', call_args[2])

        # Validate return data
        self.assertEqual('testdomain1.com', ret_val[0].name)

    def test_go_right_no_domains(self):

        # Setup Test Case
        self.mockProcessRequest.return_value = {}

        self.assertListEqual([], self.netki.get_domains())


class TestCreatePartnerDomain(TestCase):
    def setUp(self):
        self.patcher1 = patch('NetkiClient.process_request')
        self.mockProcessRequest = self.patcher1.start()

        self.netki = Netki(
            partner_id='partner_id',
            api_key='api_key',
            api_url='api_url'
        )

        self.response_data = {'domain_name': 'domain_name', 'status': 'completed', 'nameservers': 'ns1'}

        self.mockProcessRequest.return_value = AttrDict(self.response_data)

    def test_go_right_partner_domain(self):

        ret_val = self.netki.create_partner_domain('domain_name')

        # Validate request data
        self.assertEqual(1, self.mockProcessRequest.call_count)
        call_args = self.mockProcessRequest.call_args[0]
        self.assertEqual(self.netki, call_args[0])
        self.assertEqual('/v1/partner/domain/domain_name', call_args[1])
        self.assertEqual('POST', call_args[2])
        self.assertEqual('', call_args[3])

        # Validate return data
        self.assertEqual('domain_name', ret_val.name)
        self.assertEqual('completed', ret_val.status)
        self.assertEqual('ns1', ret_val.nameservers)
        self.assertEqual(self.netki, ret_val.netki_client)

    def test_go_right_sub_partner_domain(self):

        ret_val = self.netki.create_partner_domain('domain_name', 'sub_partner_id')

        # Validate request data
        self.assertEqual(1, self.mockProcessRequest.call_count)
        call_args = self.mockProcessRequest.call_args[0]
        self.assertEqual(self.netki, call_args[0])
        self.assertEqual('/v1/partner/domain/domain_name', call_args[1])
        self.assertEqual('POST', call_args[2])
        self.assertEqual({'partner_id': 'sub_partner_id'}, call_args[3])

        # Validate return data
        self.assertEqual('domain_name', ret_val.name)
        self.assertEqual('completed', ret_val.status)
        self.assertEqual('ns1', ret_val.nameservers)
        self.assertEqual(self.netki, ret_val.netki_client)


class TestCreateCertificate(TestCase):
    def setUp(self):
        self.netki = Netki.certificate_api_access('uk', 'partner_id', 'uri')

    def test_go_right(self):

        cert = self.netki.create_certificate('cust_data', 'product_id')

        self.assertEqual('cust_data', cert.customer_data)
        self.assertEqual('product_id', cert.product_id)
        self.assertEqual(self.netki, cert.netki_client)


class TestGetCertificate(TestCase):
    def setUp(self):
        self.patcher1 = patch('NetkiClient.Certificate')
        self.mockCertificateObject = self.patcher1.start()

        self.netki = Netki.certificate_api_access('uk', 'partner_id', 'uri')

    def test_go_right(self):

        cert = self.netki.get_certificate('id')

        self.assertEqual('id', cert.id)
        self.assertEqual(1, cert.set_netki_client.call_count)
        self.assertEqual(self.netki, cert.set_netki_client.call_args[0][0])
        self.assertEqual(1, cert.get_status.call_count)


class TestGetAvailableProducts(TestCase):
    def setUp(self):
        self.patcher1 = patch('NetkiClient.process_request')
        self.mockProcessRequest = self.patcher1.start()

        self.netki = Netki.certificate_api_access('uk', 'partner_id', 'uri')

    def test_go_right(self):

        ret_val = self.netki.get_available_products()

        self.assertEqual(self.mockProcessRequest.return_value.get('products'), ret_val)
        self.assertEqual(1, self.mockProcessRequest.call_count)
        self.assertEqual(self.netki, self.mockProcessRequest.call_args[0][0])
        self.assertEqual('/v1/certificate/products', self.mockProcessRequest.call_args[0][1])
        self.assertEqual('GET', self.mockProcessRequest.call_args[0][2])


class TestGetCABundle(TestCase):
    def setUp(self):
        self.patcher1 = patch('NetkiClient.process_request')
        self.mockProcessRequest = self.patcher1.start()

        self.netki = Netki.certificate_api_access('uk', 'partner_id', 'uri')

    def test_go_right(self):

        ret_val = self.netki.get_ca_bundle()

        self.assertEqual(self.mockProcessRequest.return_value.get('cacerts'), ret_val)
        self.assertEqual(1, self.mockProcessRequest.call_count)
        self.assertEqual(self.netki, self.mockProcessRequest.call_args[0][0])
        self.assertEqual('/v1/certificate/cacert', self.mockProcessRequest.call_args[0][1])
        self.assertEqual('GET', self.mockProcessRequest.call_args[0][2])


class TestGetAccountBalance(TestCase):
    def setUp(self):
        self.patcher1 = patch('NetkiClient.process_request')
        self.mockProcessRequest = self.patcher1.start()

        self.netki = Netki.certificate_api_access('uk', 'partner_id', 'uri')

    def test_go_right(self):

        ret_val = self.netki.get_account_balance()

        self.assertEqual(self.mockProcessRequest.return_value.get('available_balance'), ret_val)
        self.assertEqual(1, self.mockProcessRequest.call_count)
        self.assertEqual(self.netki, self.mockProcessRequest.call_args[0][0])
        self.assertEqual('/v1/certificate/balance', self.mockProcessRequest.call_args[0][1])
        self.assertEqual('GET', self.mockProcessRequest.call_args[0][2])
