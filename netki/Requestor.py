__author__ = 'frank'

import hashlib
import json
import requests
from attrdict import AttrDict
from ecdsa import SigningKey
from ecdsa.util import sigencode_der


def process_request(netki_client, uri, method, data=''):
    """
    API request processor handling supported API methods and error messages returned from API. Refer to the Netki
    Apiary documentation for additional information. http://docs.netki.apiary.io/

    :param netki_client: Netki client reference
    :param uri: api_url from Netki class init
    :param method: Request method
    :param data: PUT / POST data
    :return: AttrDict for valid, non-error responses. Empty dict for 204 responses. Exception for error responses.
    """

    if method not in ['GET', 'POST', 'PUT', 'DELETE']:
        raise Exception('Unsupported HTTP method: %s' % method)

    headers = {}
    if data:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(data)

    if netki_client._auth_type == 'api_key':
        headers.update({
            'Authorization': netki_client.api_key,
            'X-Partner-ID': netki_client.partner_id
        })

    elif netki_client._auth_type == 'distributed':

        key = SigningKey.from_der(netki_client.user_key.decode('hex'))

        encoded_user_pub_key = key.get_verifying_key().to_der().encode('hex')
        encoded_data_sig = key.sign(
            netki_client.api_url + uri + data,
            hashfunc=hashlib.sha256, sigencode=sigencode_der
        ).encode('hex')

        headers.update({
            'X-Partner-Key': netki_client.key_signing_key,
            'X-Partner-KeySig': netki_client.signed_user_key,
            'X-Identity': encoded_user_pub_key,
            'X-Signature': encoded_data_sig
        })

    elif netki_client._auth_type == 'certificate':

        key = SigningKey.from_der(netki_client.user_key.decode('hex'))

        encoded_user_pub_key = key.get_verifying_key().to_der().encode('hex')
        encoded_data_sig = key.sign(netki_client.api_url + uri + data, hashfunc=hashlib.sha256, sigencode=sigencode_der).encode('hex')

        headers.update({
            'X-Identity': encoded_user_pub_key,
            'X-Signature': encoded_data_sig,
            'X-Partner-ID': netki_client.partner_id
        })

    else:
        raise Exception('Invalid Access Type Defined')

    response = requests.request(method=method, url=netki_client.api_url + uri, headers=headers, data=data if data else None)

    if method == 'DELETE' and response.status_code == 204:
        return {}

    rdata = AttrDict(response.json())

    if response.status_code >= 300 or not rdata.success:
        error_message = rdata.message

        if 'failures' in rdata:
            error_message += ' [FAILURES: '
            failures = []
            for failure in rdata.failures:
                failures.append(failure.message)

            error_message = error_message + ', '.join(failures) + ']'

        raise Exception(error_message)

    return rdata
