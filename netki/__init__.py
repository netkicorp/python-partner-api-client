__author__ = 'frank'

from attrdict import AttrDict
import json
import requests


def submit_request(api_key, partner_id, uri, method, data=None):

    headers = {
        'Content-Type': 'application/json',
        'Authorization': api_key,
        'X-Partner-ID': partner_id
    }

    if method == 'GET':
        return requests.get(uri, headers=headers)
    elif method == 'POST':
        return requests.post(uri, data=data, headers=headers)
    elif method == 'PUT':
        return requests.put(uri, data=data, headers=headers)
    elif method == 'DELETE':
        return requests.delete(uri, data=data, headers=headers)
    else:
        raise Exception('Unsupported method')


class WalletName:
    def __init__(self, id=None, domain_name='', name='', wallets={}, external_id=None):

        self.id = id
        self.domain_name = domain_name
        self.name = name
        self.wallets = wallets
        self.external_id = external_id

    # Values used for save() and delete()
    def set_api_opts(self, api_url, api_key, partner_id):
        self.api_url = api_url
        self.api_key = api_key
        self.partner_id = partner_id

    # Return all currencies and wallet addresses
    def get_used_currencies(self):
        return self.wallets

    # Return wallet address for the specific currency provided
    def get_wallet_address(self, currency):
        return self.wallets[currency]

    # Create or Update a Wallet Name currency and wallet address
    def set_currency_address(self, currency, wallet_address):
        self.wallets[currency] = wallet_address

    # Remove a currency and wallet address
    def remove_currency_address(self, currency):
        if self.wallets[currency]:
            del self.wallets[currency]

    # Submit a new Wallet Name or changes for existing Wallet Name
    def save(self):
        wallet_data = []

        for k in self.wallets.keys():
            wallet_data.append({
                'currency': k,
                'wallet_address': self.wallets[k]
            })

        wallet_name_data = {
            'domain_name': self.domain_name,
            'name': self.name,
            'wallets': wallet_data,
            'external_id': self.external_id
        }

        wn_api_data = {'wallet_names': [wallet_name_data]}

        # If an ID is present it exists in Netki's systems, therefore submit an update
        if self.id:
            wallet_name_data['id'] = self.id
            response = submit_request(
                self.api_key,
                self.partner_id,
                self.api_url + '/v1/partner/walletname',
                'PUT',
                json.dumps(wn_api_data)
            )
        else:
            response = submit_request(
                self.api_key,
                self.partner_id,
                self.api_url + '/v1/partner/walletname',
                'POST',
                json.dumps(wn_api_data)
            )

        resp = AttrDict(response.json())

        if response.status_code in [200, 201, 202]:
            for wn_resp in resp.wallet_names:
                if resp.success and wn_resp.domain_name == self.domain_name and wn_resp.name == self.name:
                    self.id = wn_resp.id
        else:
            if resp.get('failures'):
                raise Exception('WalletName Save Failed! %s' % resp.failures[0].message)
            else:
                raise Exception('WalletName Save Failed! %s' % resp.message)

    # Delete an existing Wallet Name
    def delete(self):
        if not self.id:
            raise Exception('Unable to Delete Object that Does Not Exist Remotely')

        wn_api_data = {
            'wallet_names': [
                {
                    'domain_name': self.domain_name,
                    'id': self.id
                }
            ]
        }

        response = submit_request(
            self.api_key,
            self.partner_id,
            self.api_url + '/v1/partner/walletname',
            'DELETE',
            json.dumps(wn_api_data)
        )

        if response.status_code != 204:
            resp = AttrDict(response.json())

            if resp.get('failures'):
                raise Exception('WalletName Delete Failed! %s' % resp.failures[0].message)
            else:
                raise Exception('WalletName Delete Failed! %s' % resp.message)


class Netki:
    def __init__(self, partner_id=None, api_key=None, api_url='https://api.netki.com'):

        self.partner_id = partner_id
        self.api_key = api_key
        self.api_url = api_url

    # Return all partner Wallet Names, or a filtered list by partner domain_name and/or external_id
    def get_wallet_names(self, domain_name=None, external_id=None):

        args = []
        if domain_name:
            args.append('domain_name=%s' % domain_name)

        if external_id:
            args.append('external_id=%s' % external_id)

        uri = self.api_url + '/v1/partner/walletname'

        if args:
            uri = uri + '?' + '&'.join(args)

        resp = submit_request(self.api_key, self.partner_id, uri, 'GET')
        response_object = AttrDict(resp.json())

        if resp.status_code != 200:
            raise Exception('Get WalletNames Failed! %s' % response_object.message)

        if not response_object.wallet_name_count:
            return []

        # Assemble and return a list of Wallet Name objects from the response data
        all_wallet_names = []
        for wn in response_object.wallet_names:
            wallet_name = WalletName()
            wallet_name.id = wn.id
            wallet_name.domain_name = wn.domain_name
            wallet_name.name = wn.name
            wallet_name.external_id = wn.external_id
            wallet_name.wallets = {}

            for wallet in wn.wallets:
                wallet_name.wallets[wallet.currency] = wallet.wallet_address

            wallet_name.set_api_opts(self.api_url, self.api_key, self.partner_id)

            all_wallet_names.append(wallet_name)

        return all_wallet_names

    # Create a Wallet Name object with required data
    def create_wallet_name(self, domain_name, name, wallets={}, external_id=None):
        wallet_name = WalletName()
        wallet_name.domain_name = domain_name
        wallet_name.name = name
        wallet_name.wallets = wallets
        wallet_name.external_id = external_id
        wallet_name.set_api_opts(self.api_url, self.api_key, self.partner_id)

        return wallet_name
