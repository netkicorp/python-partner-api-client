__author__ = 'frank'

import hashlib
import json
from ecdsa import curves, SigningKey
from ecdsa.util import sigdecode_der
from mock import Mock, patch
from unittest import TestCase

from Requestor import process_request


class TestProcessRequest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user_key = SigningKey.generate(curve=curves.SECP256k1)

    def setUp(self):
        self.patcher1 = patch('Requestor.requests')
        self.mockRequests = self.patcher1.start()

        # Setup Mock netki_client
        self.netki_client = Mock()
        self.netki_client._auth_type = 'api_key'
        self.netki_client.api_url = ''

        # Setup Keys for distributed and certificate auth types

        # Setup Common Data For Verification
        self.api_key_auth_headers = {
            'X-Partner-ID': self.netki_client.partner_id,
            'Content-Type': 'application/json',
            'Authorization': self.netki_client.api_key
        }

        self.distributed_auth_headers = {
            'X-Partner-Key': self.netki_client.key_signing_key,
            'X-Partner-KeySig': self.netki_client.signed_user_key,
            'X-Identity': self.user_key.get_verifying_key().to_der().encode('hex'),
            'Content-Type': 'application/json'
        }

        self.certificate_auth_headers = {
            'X-Identity': self.user_key.get_verifying_key().to_der().encode('hex'),
            'X-Partner-ID': self.netki_client.partner_id,
            'Content-Type': 'application/json'
        }

        self.request_data = {'key': 'val'}

        # Setup go right condition
        self.response_data = {'success': True}
        self.mockRequests.request.return_value.json.return_value = self.response_data
        self.mockRequests.request.return_value.status_code = 200

    def tearDown(self):
        self.patcher1.stop()

    def test_api_key_auth_get_method_go_right(self):

        del self.api_key_auth_headers['Content-Type']

        ret_val = process_request(self.netki_client, 'uri', 'GET')

        # Validate submit_request data
        self.assertEqual(1, self.mockRequests.request.call_count)

        call_args = self.mockRequests.request.call_args[1]
        self.assertIsNone(call_args.get('data'))
        self.assertDictEqual(self.api_key_auth_headers, call_args.get('headers'))
        self.assertEqual('GET', call_args.get('method'))
        self.assertEqual('uri', call_args.get('url'))

        # Validate response
        self.assertDictEqual(ret_val, self.response_data)

    def test_api_key_auth_post_method_go_right(self):

        ret_val = process_request(self.netki_client, 'uri', 'POST', self.request_data)

        # Validate submit_request data
        self.assertEqual(1, self.mockRequests.request.call_count)

        call_args = self.mockRequests.request.call_args[1]
        self.assertEqual(json.dumps(self.request_data), call_args.get('data'))
        self.assertDictEqual(self.api_key_auth_headers, call_args.get('headers'))
        self.assertEqual('POST', call_args.get('method'))
        self.assertEqual('uri', call_args.get('url'))

        # Validate response
        self.assertDictEqual(ret_val, self.response_data)

    def test_api_key_auth_put_method_go_right(self):

        ret_val = process_request(self.netki_client, 'uri', 'PUT', self.request_data)

        # Validate submit_request data
        self.assertEqual(1, self.mockRequests.request.call_count)

        call_args = self.mockRequests.request.call_args[1]
        self.assertEqual(json.dumps(self.request_data), call_args.get('data'))
        self.assertDictEqual(self.api_key_auth_headers, call_args.get('headers'))
        self.assertEqual('PUT', call_args.get('method'))
        self.assertEqual('uri', call_args.get('url'))

        # Validate response
        self.assertDictEqual(ret_val, self.response_data)

    def test_api_key_auth_delete_method_go_right(self):

        # Setup Test case
        self.mockRequests.request.return_value.status_code = 204
        del self.api_key_auth_headers['Content-Type']

        ret_val = process_request(self.netki_client, 'uri', 'DELETE')

        # Validate submit_request data
        self.assertEqual(1, self.mockRequests.request.call_count)

        call_args = self.mockRequests.request.call_args[1]
        self.assertIsNone(call_args.get('data'))
        self.assertDictEqual(self.api_key_auth_headers, call_args.get('headers'))
        self.assertEqual('DELETE', call_args.get('method'))
        self.assertEqual('uri', call_args.get('url'))

        # Validate response
        self.assertDictEqual(ret_val, {})

    def test_distributed_auth_post_method_go_right(self):

        # Setup Test Case
        self.netki_client._auth_type = 'distributed'
        self.netki_client.user_key = self.user_key.to_der().encode('hex')

        ret_val = process_request(self.netki_client, 'uri', 'POST', self.request_data)

        # Validate submit_request data
        self.assertEqual(1, self.mockRequests.request.call_count)

        call_args = self.mockRequests.request.call_args[1]
        self.assertEqual(json.dumps(self.request_data), call_args.get('data'))

        self.assertTrue(  # Validate that the Appropriate PK Was Used to Sign the Data
            self.user_key.get_verifying_key().verify(
                call_args['headers']['X-Signature'].decode('hex'),
                self.netki_client.api_url + 'uri' + json.dumps(self.request_data),
                hashfunc=hashlib.sha256, sigdecode=sigdecode_der
            )
        )

        del call_args['headers']['X-Signature']  # Delete sig and Validate Remaining Headers
        self.assertDictEqual(self.distributed_auth_headers, call_args.get('headers'))
        self.assertEqual('POST', call_args.get('method'))
        self.assertEqual('uri', call_args.get('url'))

        # Validate response
        self.assertDictEqual(ret_val, self.response_data)

    def test_certificate_auth_post_method_go_right(self):

        # Setup Test Case
        self.netki_client._auth_type = 'certificate'
        self.netki_client.user_key = self.user_key.to_der().encode('hex')

        ret_val = process_request(self.netki_client, 'uri', 'POST', self.request_data)

        # Validate submit_request data
        self.assertEqual(1, self.mockRequests.request.call_count)

        call_args = self.mockRequests.request.call_args[1]
        self.assertEqual(json.dumps(self.request_data), call_args.get('data'))

        self.assertTrue(  # Validate that the Appropriate PK Was Used to Sign the Data
            self.user_key.get_verifying_key().verify(
                call_args['headers']['X-Signature'].decode('hex'),
                self.netki_client.api_url + 'uri' + json.dumps(self.request_data),
                hashfunc=hashlib.sha256, sigdecode=sigdecode_der
            )
        )

        del call_args['headers']['X-Signature']  # Delete sig and Validate Remaining Headers
        self.assertDictEqual(self.certificate_auth_headers, call_args.get('headers'))
        self.assertEqual('POST', call_args.get('method'))
        self.assertEqual('uri', call_args.get('url'))

        # Validate response
        self.assertDictEqual(ret_val, self.response_data)

    def test_unsupported_method(self):

        self.assertRaisesRegexp(
            Exception,
            '^Unsupported HTTP method: PATCH$',
            process_request,
            self.netki_client,
            'uri',
            'PATCH',
            self.request_data
        )

        # Validate submit_request data
        self.assertEqual(0, self.mockRequests.request.call_count)

    def test_delete_non_204_response(self):

        # Setup Test case
        self.mockRequests.request.return_value.status_code = 200
        del self.api_key_auth_headers['Content-Type']

        ret_val = process_request(self.netki_client, 'uri', 'DELETE')

        # Validate submit_request data
        self.assertEqual(1, self.mockRequests.request.call_count)

        call_args = self.mockRequests.request.call_args[1]
        self.assertIsNone(call_args.get('data'))
        self.assertDictEqual(self.api_key_auth_headers, call_args.get('headers'))
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
            self.netki_client,
            'uri',
            'POST',
            self.request_data
        )

        # Validate submit_request data
        self.assertEqual(1, self.mockRequests.request.call_count)

        call_args = self.mockRequests.request.call_args[1]
        self.assertEqual(json.dumps(self.request_data), call_args.get('data'))
        self.assertDictEqual(self.api_key_auth_headers, call_args.get('headers'))
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
            self.netki_client,
            'uri',
            'POST',
            self.request_data
        )

        # Validate submit_request data
        self.assertEqual(1, self.mockRequests.request.call_count)

        call_args = self.mockRequests.request.call_args[1]
        self.assertEqual(json.dumps(self.request_data), call_args.get('data'))
        self.assertDictEqual(self.api_key_auth_headers, call_args.get('headers'))
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
            self.netki_client,
            'uri',
            'POST',
            self.request_data
        )

        # Validate submit_request data
        self.assertEqual(1, self.mockRequests.request.call_count)

        call_args = self.mockRequests.request.call_args[1]
        self.assertEqual(json.dumps(self.request_data), call_args.get('data'))
        self.assertDictEqual(self.api_key_auth_headers, call_args.get('headers'))
        self.assertEqual('POST', call_args.get('method'))
        self.assertEqual('uri', call_args.get('url'))