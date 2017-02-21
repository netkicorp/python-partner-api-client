__author__ = 'frank'

from unittest import TestCase

from BaseObject import BaseObject


class TestBaseObject(TestCase):

    def test_init(self):
        obj = BaseObject()

        self.assertIsNone(obj.netki_client)

    def test_set_netki_client(self):
        obj = BaseObject()
        obj.set_netki_client('new client')

        self.assertEqual('new client', obj.netki_client)
