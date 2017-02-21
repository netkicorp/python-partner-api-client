__author__ = 'frank'

from Certificate import Certificate
from Domain import Domain
from Partner import Partner
from Requestor import process_request
from WalletName import WalletName


class Netki:
    """
    General methods for interacting with Netki's Partner API.

    :param partner_id: Your Partner ID available in the API Keys section of your My Account page.
    :param api_key: API Key available in the API Key section of your My Account page.
    :param api_url: https://api.netki.com unless otherwise noted
    """
    def __init__(self, api_key, partner_id, api_url='https://api.netki.com'):

        self.api_key = api_key
        self.api_url = api_url
        self.partner_id = partner_id
        self._auth_type = 'api_key'

    @classmethod
    def distributed_api_access(cls, key_signing_key, signed_user_key, user_key, api_url='https://api.netki.com'):
        """
        Instantiate the Netki Client for distributed_api_access if your user's clients will communicate directly with
         Netki to manage Wallet Names instead of communicating with your servers. More information can be found here:
         http://docs.netki.apiary.io/#reference/partner-api

        :param key_signing_key:
        :param signed_user_key:
        :param user_key:
        :param api_url: https://api.netki.com unless otherwise noted
        :return: Netki client.
        """
        client = cls(None, None, api_url)
        client.key_signing_key = key_signing_key
        client.signed_user_key = signed_user_key
        client.user_key = user_key
        client._auth_type = 'distributed'

        if not client.key_signing_key:
            raise ValueError('key_signing_key Required for Distributed API Access')

        if not client.signed_user_key:
            raise ValueError('signed_user_key Required for Distributed API Access')

        if not user_key:
            raise ValueError('user_key Required for Distributed API Access')

        return client

    @classmethod
    def certificate_api_access(cls, user_key, partner_id, api_url='https://api.netki.com'):
        """
        Instantiate the Netki Client for certificate_api_access in order manage your user's Digital Identity Certificates

        :param user_key:
        :param partner_id:
        :param api_url: https://api.netki.com unless otherwise noted
        :return: Netki client.
        """
        client = cls(None, None, api_url)
        client.user_key = user_key
        client.partner_id = partner_id
        client._auth_type = 'certificate'

        if not client.user_key:
            raise ValueError('user_key Required for Certificate API Access')

        if not client.partner_id:
            raise ValueError('partner_id Required for Certificate API Access')

        return client

    # Wallet Name Operations #
    def get_wallet_names(self, domain_name=None, external_id=None):
        """
        Wallet Name Operation

        Retrieve Wallet Names from the Netki API. Four options are available for retrieval:

        * Retrieve all Wallet Names associated with your partner_id by not specifying a domain_name or external_id.
        * Retrieve all Wallet Names associated with a particular partner domain_name by specifying a domain_name.
        * Retrieve all Wallet Names associated with a particular external_id by specifying an external_id.
        * Retrieve all Wallet Names associated with a domain_name and external_id by specifying both domain_name
        and external_id.

        :param domain_name: Domain name to which the requested Wallet Names belong. ``partnerdomain.com``
        :param external_id: Your unique customer identifier specified when creating a Wallet Name.
        :return: List of WalletName objects.
        """

        args = []
        if domain_name:
            args.append('domain_name=%s' % domain_name)

        if external_id:
            args.append('external_id=%s' % external_id)

        uri = '/v1/partner/walletname'

        if args:
            uri = uri + '?' + '&'.join(args)

        response = process_request(self, uri, 'GET')

        if not response.wallet_name_count:
            return []

        # Assemble and return a list of Wallet Name objects from the response data
        all_wallet_names = []

        for wn in response.wallet_names:
            wallet_name = WalletName(
                domain_name=wn.domain_name,
                name=wn.name,
                external_id=wn.external_id,
                id=wn.id
            )

            for wallet in wn.wallets:
                wallet_name.set_currency_address(wallet.currency, wallet.wallet_address)

            wallet_name.set_netki_client(self)

            all_wallet_names.append(wallet_name)

        return all_wallet_names

    def create_wallet_name(self, domain_name, name, external_id, currency, wallet_address):
        """
        Wallet Name Operation

        Create a new WalletName object with the required data. Execute save() to commit your changes to the API.

        :param domain_name: Domain name to which the requested Wallet Name's belong. ``partnerdomain.com``
        :param name: Customers Wallet Name appended to domain_name. ``joe``
        :param external_id: Your unique customer identifier for this user's Wallet Name.
        :param currency: Digital currency abbreviation noted in Netki API documentation
        :param wallet_address: Digital currency address
        :return: WalletName object
        """
        wallet_name = WalletName(
            domain_name=domain_name,
            name=name,
            external_id=external_id
        )

        wallet_name.set_currency_address(currency, wallet_address)
        wallet_name.set_netki_client(self)

        return wallet_name

    # Partner Operations #
    def get_partners(self):
        """
        Sub-partner Operation

        Get all partners (partner and sub-partners) associated with your account.

        :return: List containing Partner objects
        """

        response = process_request(self, '/v1/admin/partner', 'GET')

        partner_objects = list()
        for p in response.partners:
            partner = Partner(id=p.id, name=p.name)
            partner_objects.append(partner)

            partner.set_netki_client(self)

        return partner_objects

    def create_partner(self, partner_name):
        """
        Sub-partner Operation

        Create a sub-partner.

        :param partner_name: Partner Name
        :return: Partner object
        """

        response = process_request(self, '/v1/admin/partner/' + partner_name, 'POST')

        partner = Partner(id=response.partner.id, name=response.partner.name)
        partner.set_netki_client(self)

        return partner

    # Domain Operations #
    def get_domains(self, domain_name=None):
        """
        Domain Operation

        Retrieve all domains associated with your partner_id or a specific domain_name if supplied

        :return: List of Domain objects.
        """

        response = process_request(self, '/api/domain/%s' % domain_name if domain_name else '/api/domain', 'GET')

        if not response.get('domains'):
            return []

        domain_list = list()
        for d in response.domains:
            domain = Domain(d.domain_name)
            domain.set_netki_client(self)

            domain_list.append(domain)

        return domain_list

    def create_partner_domain(self, domain_name, sub_partner_id=None):
        """
        Domain Operation

        Create a partner domain used to offer Wallet Names.

        :param domain_name: ``partnerdomain.com``
        :param (Optional) sub_partner_id: When provided, create a domain_name under the sub_partner_id that you are
            managing.
        :return: Domain object with status and information required to complete domain setup.
        """

        post_data = {'partner_id': sub_partner_id} if sub_partner_id else ''

        response = process_request(self, '/v1/partner/domain/' + domain_name, 'POST', post_data)

        domain = Domain(response.domain_name)
        domain.status = response.status
        domain.nameservers = response.nameservers

        domain.set_netki_client(self)

        return domain

    # Certificate Operations #
    def create_certificate(self, customer_data, product_id):
        """
        Certificate Operation

        Create a partner domain used to offer Wallet Names.

        :param customer_data: Customer personal idenity information to be validated and used in the final certificate.
        :param product_id: Specific product_id (Certificate type). Product IDs can be retrieved from
        get_available_products() below.
        :return: Certificate Object
        """

        certificate = Certificate(customer_data, product_id)
        certificate.set_netki_client(self)

        return certificate

    def get_certificate(self, id):
        """
        Certificate Operation

        Retrieve an existing certificate by certificate ID from the API.

        :param id: Unique certificate ID issued after successful creation of a certificate object and save() to the API.
        :return: Certificate Object
        """

        if not id:
            raise ValueError('Certificate ID Required')

        certificate = Certificate()
        certificate.id = id
        certificate.set_netki_client(self)
        certificate.get_status()

        return certificate

    def get_available_products(self):
        """
        Certificate Operation

        Get all available certificate products associated with your account including tier and pricing information.

        :return: Dictionary containing product details.
        """

        return process_request(self, '/v1/certificate/products', 'GET').get('products')

    def get_ca_bundle(self):
        """
        Certificate Operation

        Download the root bundle used to validate the certificate chain for Netki issued certificates.

        :return: Dictionary containing certificate bundle.
        """

        return process_request(self, '/v1/certificate/cacert', 'GET').get('cacerts')

    def get_account_balance(self):
        """
        Certificate Operation

        Get available balance for certificate purchases when using Deposit/Retainer billing.

        :return: Dictionary containing available balance.
        """

        return process_request(self, '/v1/certificate/balance', 'GET').get('available_balance')
