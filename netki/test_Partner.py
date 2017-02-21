__author__ = 'frank'

from mock import patch
from unittest import TestCase

from Partner import Partner


class TestInit(TestCase):
    def test_init(self):
        partner = Partner('id', 'name')

        self.assertEqual('id', partner.id)
        self.assertEqual('name', partner.name)


class TestDelete(TestCase):
    def setUp(self):
        self.patcher1 = patch('Partner.process_request')
        self.mockProcessRequest = self.patcher1.start()

    def tearDown(self):
        self.patcher1.stop()

    def test_go_right(self):

        partner = Partner('id', 'name')

        partner.delete()

        self.assertEqual(1, self.mockProcessRequest.call_count)
        self.assertEqual(partner.netki_client, self.mockProcessRequest.call_args[0][0])
        self.assertEqual('/v1/admin/partner/name', self.mockProcessRequest.call_args[0][1])
        self.assertEqual('DELETE', self.mockProcessRequest.call_args[0][2])
