__author__ = 'frank'


from BaseObject import BaseObject
from Requestor import process_request


class Partner(BaseObject):
    """
    Partner Object

    :param id: Unique Netki identifier for this Partner.
    :param name: Unique name for this Partner.
    :return: AttrDict for valid, non-error responses. Empty dict for 204 responses. Exception for error responses.
    """

    def __init__(self, id, name):
        super(Partner, self).__init__()

        self.id = id
        self.name = name

    def delete(self):
        """
        Call delete() to remove the Partner from Netki systems.

        :return: AttrDict for valid, non-error responses. Empty dict for 204 responses. Exception for error responses.
        """
        process_request(self.netki_client, '/v1/admin/partner/' + self.name, 'DELETE')
