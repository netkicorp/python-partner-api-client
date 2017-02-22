from setuptools import setup

install_requires = [
    'attrdict==2.0.0',
    'ecdsa==0.13',
    'pyOpenSSL==16.0.0',
    'requests==2.7.0',
    'six==1.9.0',
    'wsgiref==0.1.2'
]

test_requires = [
    'mock==1.0.1'
]

setup(
    name='netki-partner-client',
    packages=['netki-partner-client'],
    version='1.0.0',
    description='This Python module provides a client for Netki\'s (https://netki.com) Partner API.',
    author='Netki Opensource',
    author_email='opensource@netki.com',
    url='https://github.com/netkicorp/python-partner-api-client',
    keywords=['netki', 'partner', 'certificate', 'walletname', 'wallet', 'name', 'bitcoin', 'blockchain', 'identity'],
    license='BSD',
    install_requires=install_requires,
    test_requires=test_requires
)
