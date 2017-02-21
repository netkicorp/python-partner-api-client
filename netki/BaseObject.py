__author__ = 'frank'


class BaseObject(object):

    def __init__(self):

        self.netki_client = None

    def set_netki_client(self, netki_client):
        """
        After instantiating the client in the appropriate mode, adding the client to the object will allow for API
        operations.

        :param netki_client: NetkiClient.Netki instance to be associated with the object.
        """

        self.netki_client = netki_client
