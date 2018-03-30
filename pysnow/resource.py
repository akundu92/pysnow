# -*- coding: utf-8 -*-

import logging

from copy import copy

from .request import SnowRequest
from .attachment import Attachment
from .url_builder import URLBuilder
from .exceptions import InvalidUsage

logger = logging.getLogger('pysnow')


class Resource(object):
    """Creates a new :class:`Resource` object

    Resources provides a natural way of interfacing with ServiceNow APIs.

    :param base_path: Base path
    :param api_path: API path
    :param chunk_size: Response stream parser chunk size (in bytes)
    :param \*\*kwargs: Arguments to pass along to :class:`Request`
    """

    def __init__(self, base_url=None, base_path=None, api_path=None, parameters=None, **kwargs):

        self._base_url = base_url
        self._base_path = base_path
        self._api_path = api_path
        self._url_builder = URLBuilder(base_url, base_path, api_path)

        self.kwargs = kwargs

        # @TODO - Remove this alias in a future release
        self.custom = self.request

        self.parameters = copy(parameters)

        logger.debug('(RESOURCE_ADD) Object: %s, chunk_size: %d' % (self, kwargs.get('chunk_size')))

    def __repr__(self):
        return '<%s [%s] at %s>' % (self.__class__.__name__, self.path, hex(id(self)))

    @property
    def path(self):
        """Get current path relative to base URL

        :return: resource path
        """

        return "%s" % self._base_path + self._api_path

    @property
    def attachments(self):
        """Clones self, performs some path modifications and passes along to :class:`Attachment`

        :return: Attachment object
        """

        resource = copy(self)
        resource._url_builder = URLBuilder(self._base_url, self._base_path, '/attachment')

        path = self._api_path.strip('/').split('/')

        if path[0] != 'table':
            raise InvalidUsage('The attachment API can only be used with the table API')

        return Attachment(resource, path[1])

    @property
    def _request(self):
        """Request wrapper

        :return: SnowRequest object
        """

        parameters = copy(self.parameters)

        return SnowRequest(url_builder=self._url_builder, parameters=parameters, parent=self, **self.kwargs)

    def get_record_link(self, sys_id):
        """Provides full URL to the provided sys_id

        :param sys_id: sys_id to generate URL for
        :return: full sys_id URL
        """

        return "%s/%s" % (self._url_builder.get_url(), sys_id)

    def get(self, query, limit=None, offset=None, fields=list()):
        """Queries the API resource

        :param query: Dictionary, string or :class:`QueryBuilder` object
        :param limit: (optional) Limits the number of records returned
        :param fields: (optional) List of fields to include in the response created_on in descending order.
        :param offset: (optional) Number of records to skip before returning records
        :return:
            - :class:`Response` object
        """

        return self._request.get(query, limit, offset, fields)

    def create(self, payload):
        """Creates a new record in the API resource

        :param payload: Dictionary containing key-value fields of the new record
        :return:
            - Dictionary of the inserted record
        """

        return self._request.create(payload)

    def update(self, query, payload):
        """Updates a record in the API resource

        :param query: Dictionary, string or :class:`QueryBuilder` object
        :param payload: Dictionary containing key-value fields of the record to be updated
        :return:
            - Dictionary of the updated record
        """

        return self._request.update(query, payload)

    def delete(self, query):
        """Deletes matching record

        :param query: Dictionary, string or :class:`QueryBuilder` object
        :return:
            - Dictionary containing information about deletion result
        """

        return self._request.delete(query)

    def request(self, method, path_append=None, headers=None, **kwargs):
        """Create a custom request

        :param method: HTTP method to use
        :param path_append: (optional) relative to :attr:`api_path`
        :param headers: (optional) Dictionary of headers to add or override
        :param kwargs: kwargs to pass along to :class:`requests.Request`
        :return:
            - :class:`Response` object
        """

        return self._request.custom(method, path_append=path_append, headers=headers, **kwargs)
