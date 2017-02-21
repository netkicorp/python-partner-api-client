__author__ = 'frank'

from datetime import datetime
from OpenSSL import crypto

from BaseObject import BaseObject
from Requestor import process_request


class Certificate(BaseObject):
    """
    Certificate Object

    :param customer_data: Dictionary of customer data required for identity validation and certificate generation.
    :param product_id: Product ID for the specific type of certificate being requested.
    """

    def __init__(self, customer_data=None, product_id=None):
        super(Certificate, self).__init__()

        self.customer_data = customer_data or dict()
        self.id = None
        self.data_token = None
        self.order_status = None
        self.order_error = None
        self.bundle = {
            'root': None,
            'intermediate': [],
            'certificate': None
        }
        self.product_id = product_id

    def submit_customer_data(self):
        """
        Call submit_customer_data() to submit customer information to the API for validation. A token representing the
        customer data is stored in the certificate object and used when submitting a certificate order.

        :return: Exception for error responses including data validation failures.
        """

        if not self.customer_data:
            raise ValueError('customer_data must be set on Certificate object')

        post_data = dict()
        for key, value in self.customer_data.iteritems():
            if key == 'partner_name':
                continue

            if isinstance(value, datetime):
                value = value.strftime('%Y-%m-%d')

            post_data[key] = value

        post_data['product'] = self.product_id

        response = process_request(self.netki_client, '/v1/certificate/token', 'POST', post_data)

        self.data_token = response.get('token')

    def submit_certificate_order(self, stripe_token=None):
        """
        Call submit_customer_data() to submit customer information to the API for validation. A token representing the
        customer data is stored in the certificate object and used when submitting a certificate order.

        :param stripe_token: If a user is being billed by Netki, submit the stripe_token returned from the Netki widget.

        :return Exception for error responses or required missing data.
        """

        if self.id:
            raise Exception('Certificate Order Has Already Been Submitted')

        if not self.data_token:
            raise ValueError('Customer Data Submission Not Complete')

        if not self.customer_data.get('email'):
            raise ValueError('Email Required in customer_data For Order Submission')

        if not self.product_id:
            raise ValueError('Product ID required for Order Submission')

        post_data = {
            'certdata_token': self.data_token,
            'email': self.customer_data.get('email'),
            'product': self.product_id,
            'stripe_token': stripe_token
        }

        response = process_request(self.netki_client, '/v1/certificate', 'POST', post_data)

        self.id = response.get('order_id')

    def submit_csr(self, pkey_obj):
        """
        Call submit_csr() to generate and send a CSR to the API for use when creating the customer's certificate.

        :param pkey_obj: OpenSSL.crypto.PKEY object used to sign the CSR and be bound to the issued certificate.

        :return Exception for error responses or required missing data.
        """

        if not self.id:
            raise ValueError('Missing ID - Order Not Yet Submitted')

        csr_pem = Certificate.generate_csr(self.customer_data, pkey_obj)

        process_request(self.netki_client, '/v1/certificate/%s/csr' % self.id, 'POST', {'signed_csr': csr_pem})

    def revoke(self, reason):
        """
        Call revoke() to add the certificate to the revocation list, effectively invalidating it.

        :param reason: Provide a reason for revocation, such as private key lost.

        :return Exception for error responses or required missing data.
        """

        if not self.id:
            raise ValueError('Missing ID - Order Not Yet Submitted')

        process_request(self.netki_client, '/v1/certificate/%s' % self.id, 'DELETE', {'revocation_reason': reason})

    def get_status(self):
        """
        Call get_status() to retrieve the order status. If an order is complete, the certificate bundle will be returned.

        :return Exception for error responses or required missing data.
        """

        if not self.id:
            raise ValueError('Missing ID - Order Not Yet Submitted')

        response = process_request(self.netki_client, '/v1/certificate/%s' % self.id, 'GET')

        self.order_status = response.get('order_status')
        self.order_error = response.get('order_error')

        if response.get('certificate_bundle'):
            self.bundle['root'] = response['certificate_bundle'].get('root')
            self.bundle['intermediate'] = response['certificate_bundle'].get('intermediate')
            self.bundle['certificate'] = response['certificate_bundle'].get('certificate')

    def is_order_complete(self):
        """
        Call is_order_compete() to return a boolean indicating whether the order is complete.

        :return Exception for error responses or required missing data.
        """

        if self.order_status and self.order_status == 'Order Finalized':
            return True

        self.get_status()
        return False

    def set_partner_name(self, partner_name):
        """
        Call set_partner_name() to provide your Netki partner name used during customer data submission.
        """

        self.customer_data['partner_name'] = partner_name
    
    @staticmethod
    def generate_csr(customer_data, pkey_obj):
        """
        Generate a CSR using the customer data and OpenSSL.crypto.PKEY object.

        :param customer_data: Dictionary that includes all customer data required for the certificate and the partner name.
        :param pkey_obj: OpenSSL.crypto.PKEY object used to sign the CSR and to be associated with the certificate.

        :return CSR PEM string.
        """

        if not isinstance(pkey_obj, crypto.PKey):
            raise ValueError('OpenSSL crypto.PKey Type Required For Private Key')

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
