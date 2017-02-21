__author__ = 'frank'

from datetime import datetime
from mock import Mock, patch
from unittest import TestCase

from Certificate import Certificate


class TestInit(TestCase):
    def test_init(self):
        cert = Certificate('cust_data', 'product_id')

        self.assertIsNone(cert.netki_client)
        self.assertEqual('cust_data', cert.customer_data)
        self.assertIsNone(cert.id)
        self.assertIsNone(cert.data_token)
        self.assertIsNone(cert.order_status)
        self.assertIsNone(cert.order_error)
        self.assertDictEqual({'root': None, 'intermediate': [], 'certificate': None}, cert.bundle)
        self.assertEqual('product_id', cert.product_id)


class TestSubmitCustomerData(TestCase):
    def setUp(self):
        self.patcher1 = patch('Certificate.process_request')
        self.mockProcessRequest = self.patcher1.start()

        # Setup Certificate Object in Test
        customer_data = {
            'first_name': 'first_name',
            'partner_name': 'partner_name',
            'identity_expiration': datetime(2020, 01, 03)
        }

        self.cert = Certificate()
        self.cert.product_id = 'product_id'
        self.cert.customer_data = customer_data

        # Setup Mock Response
        self.mockProcessRequest.return_value = {'token': 'token'}

    def tearDown(self):
        self.patcher1.stop()

    def test_go_right(self):

        # Setup Expected Post Data
        expected_post_data = {
            'first_name': 'first_name',
            'identity_expiration': '2020-01-03',
            'product': 'product_id'
        }

        self.cert.submit_customer_data()

        self.assertEqual(1, self.mockProcessRequest.call_count)
        self.assertEqual(self.cert.netki_client, self.mockProcessRequest.call_args[0][0])
        self.assertEqual('/v1/certificate/token', self.mockProcessRequest.call_args[0][1])
        self.assertEqual('POST', self.mockProcessRequest.call_args[0][2])
        self.assertDictEqual(expected_post_data, self.mockProcessRequest.call_args[0][3])
        self.assertEqual('token', self.cert.data_token)

    def test_customer_data_missing(self):

        self.cert.customer_data = None

        self.assertRaisesRegexp(
            ValueError,
            '^customer_data must be set on Certificate object$',
            self.cert.submit_customer_data
        )

        self.assertEqual(0, self.mockProcessRequest.call_count)


class TestSubmitCertificateOrder(TestCase):
    def setUp(self):
        self.patcher1 = patch('Certificate.process_request')
        self.mockProcessRequest = self.patcher1.start()

        self.cert = Certificate({'email': 'test@user.com'}, 'product_id')
        self.cert.data_token = 'data_token'

        # Setup Mock Response
        self.mockProcessRequest.return_value = {'order_id': 'order_id'}

    def tearDown(self):
        self.patcher1.stop()

    def test_go_right(self):

        # Setup Expected post_data
        expected_post_data = {
            'certdata_token': 'data_token',
            'email': 'test@user.com',
            'product': 'product_id',
            'stripe_token': 'stripe_token'
        }

        self.cert.submit_certificate_order('stripe_token')

        self.assertEqual(1, self.mockProcessRequest.call_count)
        self.assertEqual(self.cert.netki_client, self.mockProcessRequest.call_args[0][0])
        self.assertEqual('/v1/certificate', self.mockProcessRequest.call_args[0][1])
        self.assertEqual('POST', self.mockProcessRequest.call_args[0][2])
        self.assertEqual(expected_post_data, self.mockProcessRequest.call_args[0][3])

    def test_certificate_order_already_submitted(self):

        self.cert.id = 'id'

        self.assertRaisesRegexp(
            Exception,
            '^Certificate Order Has Already Been Submitted$',
            self.cert.submit_certificate_order
        )

        self.assertEqual(0, self.mockProcessRequest.call_count)

    def test_customer_data_not_yet_submitted(self):

        self.cert.data_token = None

        self.assertRaisesRegexp(
            Exception,
            '^Customer Data Submission Not Complete$',
            self.cert.submit_certificate_order
        )

        self.assertEqual(0, self.mockProcessRequest.call_count)

    def test_email_address_missing(self):

        del self.cert.customer_data['email']

        self.assertRaisesRegexp(
            Exception,
            '^Email Required in customer_data For Order Submission$',
            self.cert.submit_certificate_order
        )

        self.assertEqual(0, self.mockProcessRequest.call_count)

    def test_product_id_missing(self):

        self.cert.product_id = None

        self.assertRaisesRegexp(
            Exception,
            '^Product ID required for Order Submission$',
            self.cert.submit_certificate_order
        )

        self.assertEqual(0, self.mockProcessRequest.call_count)


class TestSubmitCSR(TestCase):
    def setUp(self):
        self.patcher1 = patch('Certificate.process_request')
        self.patcher2 = patch('Certificate.Certificate.generate_csr')

        self.mockProcessRequest = self.patcher1.start()
        self.mockGenerateCSR = self.patcher2.start()

        self.cert = Certificate()
        self.cert.id = 'id'

    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()

    def test_go_right(self):

        # Setup Pkey Mock For Tracking generate_csr Call
        pkey_obj = Mock()

        self.cert.submit_csr(pkey_obj)

        self.assertEqual(1, self.mockGenerateCSR.call_count)
        self.assertEqual(self.cert.customer_data, self.mockGenerateCSR.call_args[0][0])
        self.assertEqual(pkey_obj, self.mockGenerateCSR.call_args[0][1])

        self.assertEqual(1, self.mockProcessRequest.call_count)
        self.assertEqual(self.cert.netki_client, self.mockProcessRequest.call_args[0][0])
        self.assertEqual('/v1/certificate/%s/csr' % self.cert.id, self.mockProcessRequest.call_args[0][1])
        self.assertEqual('POST', self.mockProcessRequest.call_args[0][2])
        self.assertDictEqual({'signed_csr': self.mockGenerateCSR.return_value}, self.mockProcessRequest.call_args[0][3])

    def test_missing_id(self):

        self.cert.id = None

        self.assertRaisesRegexp(
            ValueError,
            '^Missing ID - Order Not Yet Submitted$',
            self.cert.submit_csr,
            Mock()
        )

        self.assertEqual(0, self.mockGenerateCSR.call_count)


class TestRevoke(TestCase):
    def setUp(self):
        self.patcher1 = patch('Certificate.process_request')
        self.mockProcessRequest = self.patcher1.start()

        self.cert = Certificate()
        self.cert.id = 'id'

    def tearDown(self):
        self.patcher1.stop()

    def test_go_right(self):

        self.cert.revoke('reason')

        self.assertEqual(1, self.mockProcessRequest.call_count)
        self.assertEqual(self.cert.netki_client, self.mockProcessRequest.call_args[0][0])
        self.assertEqual('/v1/certificate/%s' % self.cert.id, self.mockProcessRequest.call_args[0][1])
        self.assertEqual('DELETE', self.mockProcessRequest.call_args[0][2])
        self.assertDictEqual({'revocation_reason': 'reason'}, self.mockProcessRequest.call_args[0][3])

    def test_missing_id(self):

        self.cert.id = None

        self.assertRaisesRegexp(
            ValueError,
            '^Missing ID - Order Not Yet Submitted$',
            self.cert.revoke,
            'reason'
        )

        self.assertEqual(0, self.mockProcessRequest.call_count)


class TestGetStatus(TestCase):
    def setUp(self):
        self.patcher1 = patch('Certificate.process_request')
        self.mockProcessRequest = self.patcher1.start()

        self.cert = Certificate()
        self.cert.id = 'id'

    def tearDown(self):
        self.patcher1.stop()

    def test_go_right_no_certificate_bundle(self):

        self.cert.get_status()

        # Validate Calls
        self.assertEqual(1, self.mockProcessRequest.call_count)
        self.assertEqual(self.cert.netki_client, self.mockProcessRequest.call_args[0][0])
        self.assertEqual('/v1/certificate/%s' % self.cert.id, self.mockProcessRequest.call_args[0][1])
        self.assertEqual('GET', self.mockProcessRequest.call_args[0][2])

        # Validate Certificate Object Updates
        self.assertEqual(self.mockProcessRequest.return_value.get('order_status'), self.cert.order_status)
        self.assertEqual(self.mockProcessRequest.return_value.get('order_error'), self.cert.order_error)
        self.assertNotEqual({'root': None, 'intermediate': [], 'certificate': None}, self.cert.bundle)

    def test_go_right_certificate_bundle_available(self):

        # Setup Expected Data
        expected_bundle = {
            'root': 'rootpem',
            'intermediate': ['intermediatepem'],
            'certificate': 'certpem'
        }
        self.mockProcessRequest.return_value = {'certificate_bundle': expected_bundle}

        self.cert.get_status()

        # Validate Calls
        self.assertEqual(1, self.mockProcessRequest.call_count)
        self.assertEqual(self.cert.netki_client, self.mockProcessRequest.call_args[0][0])
        self.assertEqual('/v1/certificate/%s' % self.cert.id, self.mockProcessRequest.call_args[0][1])
        self.assertEqual('GET', self.mockProcessRequest.call_args[0][2])

        # Validate Certificate Object Updates
        self.assertEqual(self.mockProcessRequest.return_value.get('order_status'), self.cert.order_status)
        self.assertEqual(self.mockProcessRequest.return_value.get('order_error'), self.cert.order_error)
        self.assertNotEqual({'root': None, 'intermediate': [], 'certificate': None}, self.cert.bundle)

    def test_missing_id(self):

        self.cert.id = None

        self.assertRaisesRegexp(
            ValueError,
            '^Missing ID - Order Not Yet Submitted$',
            self.cert.get_status
        )

        self.assertEqual(0, self.mockProcessRequest.call_count)


class TestIsOrderComplete(TestCase):
    def setUp(self):
        self.patcher1 = patch('Certificate.process_request')
        self.patcher2 = patch('Certificate.Certificate.get_status')

        self.mockProcessRequest = self.patcher1.start()
        self.mockGetStatus = self.patcher2.start()

        self.cert = Certificate()
        self.cert.order_status = 'Order Finalized'

    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()

    def test_go_right_order_complete(self):

        self.assertTrue(self.cert.is_order_complete())
        self.assertEqual(0, self.mockGetStatus.call_count)

    def test_go_right_order_not_complete(self):

        # Setup Test Case
        self.cert.order_status = 'pending'

        self.assertFalse(self.cert.is_order_complete())
        self.assertEqual(1, self.mockGetStatus.call_count)


class TestSetPartnerName(TestCase):
    def test_go_right(self):
        self.cert = Certificate()
        self.cert.set_partner_name('partner_name')
        self.assertEqual('partner_name', self.cert.customer_data['partner_name'])


class TestGenerateCSR(TestCase):
    def setUp(self):
        from OpenSSL import crypto
        self.pkey_obj = crypto.PKey()
        self.pkey_obj.generate_key(crypto.TYPE_RSA, 512)

        self.customer_data = {
            'partner_name': 'partner_name',
            'first_name': 'first_name',
            'last_name': 'last_name',
            'country': 'us',
            'city': 'city',
            'state': 'state',
            'street_address': 'street_address',
            'postal_code': 'postal_code'
        }

        self.cert = Certificate()

    @staticmethod
    def generate_csr(customer_data, pkey_obj):

        from OpenSSL import crypto
        req = crypto.X509Req()
        req.get_subject().organizationName = customer_data.get('partner_name')
        req.get_subject().CN = '%s %s' % (customer_data.get('first_name'), customer_data.get('last_name'))
        req.get_subject().countryName = customer_data.get('country')
        req.get_subject().localityName = customer_data.get('city')
        req.get_subject().stateOrProvinceName = customer_data.get('state')
        req.get_subject().street = customer_data.get('street_address')
        req.get_subject().postalCode = customer_data.get('postal_code')

        base_constraints = ([
            crypto.X509Extension("keyUsage", False, "Digital Signature, Non Repudiation, Key Encipherment"),
            crypto.X509Extension("basicConstraints", False, "CA:FALSE")
        ])

        req.add_extensions(base_constraints)
        req.set_pubkey(pkey_obj)
        req.sign(pkey_obj, 'sha256')

        return crypto.dump_certificate_request(crypto.FILETYPE_PEM, req)

    def test_go_right(self):

        ret_val = self.cert.generate_csr(self.customer_data, self.pkey_obj)

        self.assertEqual(self.generate_csr(self.customer_data, self.pkey_obj), ret_val)

    def test_invalid_PKey(self):

        self.assertRaisesRegexp(
            ValueError,
            '^OpenSSL crypto.PKey Type Required For Private Key$',
            self.cert.generate_csr,
            self.customer_data,
            'badpkey'
        )
