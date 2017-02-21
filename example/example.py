__author__ = 'frank'

from netki.NetkiClient import Netki

if __name__ == '__main__':

    api_base = 'https://api.netki.com'

    ########################
    # Wallet Name Examples #
    ########################
    api_key = 'netki_XXXXXXXXXXXXXXXXXXXXXXXXX'
    partner_id = 'XXXXXXXXXXXXXXXXXXXXXXXXX'

    # Access Type: Partner ID & API Key
    client = Netki(api_key, partner_id, api_base)

    # Get All Domains
    domains = client.get_domains()

    # Create a new domain not belonging to a partner
    new_domain = client.create_partner_domain('newtestdomain.com')

    # Get All Partners
    partners = client.get_partners()

    # Create a new Partner
    new_partner = client.create_partner('NewPartner')

    # Create a new domain belonging to a partner
    new_partner_domain = client.create_partner_domain('newpartnerdomain.com', new_partner.id)

    # Delete Domain
    new_domain.delete()
    new_partner_domain.delete()

    # Delete Partner
    new_partner.delete()

    # Get All Wallet Names
    wallet_names = client.get_wallet_names()

    # Update a Wallet Name's BTC Wallet Address
    wallet_name_to_update = wallet_names[0]
    wallet_name_to_update.set_currency_address('btc', '3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy')
    wallet_name_to_update.save()

    # Create a New Wallet Name
    new_wallet_name = client.create_wallet_name(
        'testdomain.com',
        'newtestwallet',
        'external_id',
        'btc',
        '3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy'
    )
    new_wallet_name.save()

    # Add a Litecoin Wallet Address
    new_wallet_name.set_currency_address('ltc', 'LQVeWKif6kR1Z5KemVcijyNTL2dE3SfYQM')
    new_wallet_name.save()

    # Get all Wallet Names for a Domain
    filtered_wallet_names = client.get_wallet_names('testdomain.com')

    # Get all Wallet Names matching an External ID
    filtered_wallet_names = client.get_wallet_names(None, 'external_id')

    # Get all Wallet Names for a Domain matching an External ID
    filtered_wallet_names = client.get_wallet_names('testdomain.com', 'external_id')

    # Delete Wallet Name
    new_wallet_name.delete()

    ###########################################
    # Distributed API Access for Wallet Names #
    ###########################################

    # When using Distributed API Access, the client has access only to their Wallet Name(s) created using their user's
    # public key. Keys and signatures are DER encoded and transfered in a HEX encoded format.

    partner_verifying_key = '30563010060...'
    user_private_key = '3074020101042070a8...'
    user_private_key_signature = '3045022100e97...'

    client = Netki.distributed_api_access(partner_verifying_key, user_private_key_signature, user_private_key, api_base)

    #############################################################
    # Certificate API Access with Partner Signed Authentication #
    #############################################################
    user_private_key = '3074020101042070a89046...'
    partner_id = 'XXXXXXXXXXXXXXXXXXXXXXXXX'
    partner_name = 'Your Partner Name'
    existing_certificate_id = 'XXXXXXXXXXXXXXXXXXXXXXXXX'

    client = Netki.certificate_api_access(user_private_key, partner_id, api_base)

    # Get Available Products
    products = client.get_available_products()
    selected_product = products[0]

    # Setup Customer Data for Submission
    from datetime import datetime
    customer_data = {
        'partner_name': 'Partner Name',
        'country': 'AU',
        'city': 'Brisbane',
        'first_name': 'Testy',
        'middle_name': 'Veritas',
        'last_name': 'Testerson',
        'state': 'QLD',
        'street_address': '123 Main St.',
        'postal_code': '4120',
        'email': 'user6@domain.com',
        'dob': datetime(1981, 01, 02),
        'phone': '+61 1300 975 707',
        'identity': '1234567890',
        'identity_type': 'drivers license',
        'identity_expiration': datetime(2030, 01, 02),
        'identity_state': 'QLD',
        'identity_gender': 'F'
    }

    # Create Certificate
    cert = client.create_certificate(customer_data, selected_product.get('id'))
    cert.set_partner_name(partner_name)

    # Submit User Data for Tokenization
    cert.submit_customer_data()

    # Submit Certificate Order
    cert.submit_certificate_order()

    # Submit CSR with Customer Data
    from OpenSSL import crypto
    pkey_obj = crypto.PKey()
    pkey_obj.generate_key(crypto.TYPE_RSA, 2048)

    cert.submit_csr(pkey_obj)

    # Poll for order completion
    from time import sleep
    while not cert.is_order_complete():
        cert.get_status()
        sleep(10)

    # Retrieve existing certificate
    existing_cert = client.get_certificate(existing_certificate_id)

    # Get Deposit Account Balance
    balance = client.get_account_balance()

    # Retrieve Netki Certificate Bundle
    cert_bundle = client.get_ca_bundle()

