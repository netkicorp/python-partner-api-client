__author__ = 'frank'

from BaseObject import BaseObject
from Requestor import process_request


class Domain(BaseObject):
    """
    Domain Object

    :param name: Unique name for this Domain.
    """

    def __init__(self, name):
        super(Domain, self).__init__()

        self.name = name

        self.status = None
        self.delegation_status = None
        self.delegation_message = None
        self.wallet_name_count = 0
        self.next_roll = None
        self.ds_records = None
        self.nameservers = None
        self.public_key_signing_key = None

    def delete(self):
        """
        Call delete() to remove the Domain from Netki systems.

        :return: AttrDict for valid, non-error responses. Empty dict for 204 responses. Exception for error responses.
        """

        process_request(self.netki_client, '/v1/partner/domain/' + self.name, 'DELETE')

    def load_status(self):
        """
        Call load_status() to retrieve meta data about the domain.

        :return: AttrDict for valid, non-error responses. Empty dict for 204 responses. Exception for error responses.
        """

        response = process_request(self.netki_client, '/v1/partner/domain/' + self.name, 'GET')

        self.status = response.get('status')
        self.delegation_status = response.get('delegation_status')
        self.delegation_message = response.get('delegation_message')
        self.wallet_name_count = response.get('wallet_name_count')

    def load_dnssec_details(self):
        """
        Call load_dnssec_details() to retrieve DNSSEC information required for secure DNS setup.

        :return: AttrDict for valid, non-error responses. Empty dict for 204 responses. Exception for error responses.
        """

        response = process_request(self.netki_client, '/v1/partner/domain/dnssec/' + self.name, 'GET')

        self.public_key_signing_key = response.get('public_key_signing_key')
        self.ds_records = response.get('ds_records')
        self.nameservers = response.get('nameservers')
        self.next_roll = response.get('next_roll')
