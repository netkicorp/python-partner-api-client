__author__ = 'frank'

from mock import patch
from unittest import TestCase

from Domain import Domain


class TestInit(TestCase):
    def test_init(self):
        domain = Domain('domain_name')

        self.assertEqual('domain_name', domain.name)
        self.assertIsNone(domain.netki_client)
        self.assertIsNone(domain.status)
        self.assertIsNone(domain.delegation_message)
        self.assertEqual(0, domain.wallet_name_count)
        self.assertIsNone(domain.next_roll)
        self.assertIsNone(domain.ds_records)
        self.assertIsNone(domain.nameservers)
        self.assertIsNone(domain.public_key_signing_key)


class TestDelete(TestCase):
    def setUp(self):
        self.patcher1 = patch('Domain.process_request')
        self.mockProcessRequest = self.patcher1.start()

    def tearDown(self):
        self.patcher1.stop()

    def test_go_right(self):

        domain = Domain('domain_name')
        domain.delete()

        self.assertEqual(1, self.mockProcessRequest.call_count)
        self.assertEqual(domain.netki_client, self.mockProcessRequest.call_args[0][0])
        self.assertEqual('/v1/partner/domain/domain_name', self.mockProcessRequest.call_args[0][1])
        self.assertEqual('DELETE', self.mockProcessRequest.call_args[0][2])


class TestLoadStatus(TestCase):
    def setUp(self):
        self.patcher1 = patch('Domain.process_request')
        self.mockProcessRequest = self.patcher1.start()

    def tearDown(self):
        self.patcher1.stop()

    def test_go_right(self):

        domain = Domain('domain_name')
        domain.load_status()

        # Validate Calls
        self.assertEqual(1, self.mockProcessRequest.call_count)
        self.assertEqual(domain.netki_client, self.mockProcessRequest.call_args[0][0])
        self.assertEqual('/v1/partner/domain/domain_name', self.mockProcessRequest.call_args[0][1])
        self.assertEqual('GET', self.mockProcessRequest.call_args[0][2])

        # Validate Domain Object Updates
        self.assertEqual(self.mockProcessRequest.return_value.get('status'), domain.status)
        self.assertEqual(self.mockProcessRequest.return_value.get('delegation_status'), domain.delegation_status)
        self.assertEqual(self.mockProcessRequest.return_value.get('delegation_message'), domain.delegation_message)
        self.assertEqual(self.mockProcessRequest.return_value.get('wallet_name_count'), domain.wallet_name_count)


class TestLoadDnssecDetails(TestCase):
    def setUp(self):
        self.patcher1 = patch('Domain.process_request')
        self.mockProcessRequest = self.patcher1.start()

    def tearDown(self):
        self.patcher1.stop()

    def test_go_right(self):

        domain = Domain('domain_name')
        domain.load_dnssec_details()

        # Validate Calls
        self.assertEqual(1, self.mockProcessRequest.call_count)
        self.assertEqual(domain.netki_client, self.mockProcessRequest.call_args[0][0])
        self.assertEqual('/v1/partner/domain/dnssec/domain_name', self.mockProcessRequest.call_args[0][1])
        self.assertEqual('GET', self.mockProcessRequest.call_args[0][2])

        # Validate Domain Object Updates
        self.assertEqual(self.mockProcessRequest.return_value.get('public_key_signing_key'), domain.public_key_signing_key)
        self.assertEqual(self.mockProcessRequest.return_value.get('ds_records'), domain.ds_records)
        self.assertEqual(self.mockProcessRequest.return_value.get('nameservers'), domain.nameservers)
        self.assertEqual(self.mockProcessRequest.return_value.get('next_roll'), domain.next_roll)
