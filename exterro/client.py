## /client.py

"""
The client and credential handler to send requests
between the client python environment and the API
service.
"""

from requests import Session, Response
from typing import Any, Union

from .api.attributes import Attributes
from .api.cases import Cases
from .api.collections import Collections
from .api.extensions import status_check_ext, group_list_ext, user_list_ext
from .logging import logger
from . import utilities

## Declaring __all__

__all__ = ("Client", )

## Build our URL path and headers for later use.

class Client:
	"""Instantiates the URL and Authentication against the API
	service. All extra arguments are passed to the session creator.

	The constructor will try to validate the API service's status.

	:param url: The base url the API service is listening upon.
	:type url: string

	:param apikey: The API key to use to authenticate against the API service.
	:type apikey: string

	:param auth: The auth method to be overriden on the session.
	:type auth: Any, optional

	:param cert: The cert attribute to be overriden on the session.
	:type cert: str/tuple, optional

	:param verify: The verify attribute to be overriden on the session.
	:type verify: str, optional

	Making a HTTP Client:

	.. code-block:: python

		from exterro.client import Client

		client = Client("http://localhost:4443/", "api-key-guid")
	
	Making a HTTPS Client:

	.. code-block:: python

		from exterro.client import Client

		client = Client("https://localhost:4443/", "api-key-guid", verify="/path/to/cert/file")
	"""

	__request_types = ("delete", "get", "patch", "post", "put")

	def __init__(self, url: str, apikey: Union[str, None]=None, auth: Any=None,
			cert: Union[str, tuple, None]=None, verify: Union[str, None]=None,
			ciphers: str="RSA+AES:RSA+AESGCM", *args, **kwargs):
		self.url = url

		self.session = Session(*args, **kwargs)

		if apikey:
			self.session.headers = {"EnterpriseApiKey": apikey}

		if auth:
			self.session.auth = auth

		if cert:
			self.session.cert = cert

		if verify:
			self.session.verify = verify

		self.session.mount("https://", utilities.CipherAdapter(ciphers))

		request_type, ext = status_check_ext
		response = self.send_request(request_type, ext)
		if response.json() != "Ok":
			raise ConnectionError("FTK API service responded with bad 'status'.")

		self._attributes = None
		self._cases = None
		self._collections = None
		self._fields = None
		self._groups = None
		self._users = None

	## Constructing all the functions required to make valid URL requests.

	def send_request(self, request_type: str, extension: str, *args, **kwargs) -> Response:
		"""Sends a HTTP request to the API service. All extra arguments are passed
		to the request function.

		:param request_type: The type of request. (get, post, patch, put, delete)
		:type request_type: string

		:param extension: The extension to append to the base url.
		:type extension: string
		"""
		if not request_type in self.__request_types:
			raise AttributeError(f"Client.send_request cannot access '{request_type}'.")
		request_func = getattr(utilities, request_type)
		response = request_func(self.session, self.url + extension, *args, **kwargs)
		if "Content-Type" in response.headers and response.headers["Content-Type"] == "text/html":
			raise RuntimeError("Permission denied.")
		return response

	@property
	def attributes(self) -> Attributes:
		"""Maintains all attributes (columns) that can be used for filtering and viewing.

		:getter: A list of :class:`~exterro.api.attributes.Attribute` objects.
		:type: list[:class:`~exterro.api.attributes.Attribute`]
		"""
		if not self._attributes:
			self._attributes = Attributes(self)
		return self._attributes

	@property
	def cases(self) -> Cases:
		"""Maintains all cases available within the platform.

		:getter: A list of :class:`~exterro.api.cases.Case` objects.
		:type: :class:`~exterro.api.cases.Cases`
		"""
		if not self._cases:
			## Instantiating Attributes... without it case usage falls apart.
			self._attributes = Attributes(self)
			self._cases = Cases(self)
		return self._cases
	
	@property
	def collections(self) -> Collections:
		"""Maintains all cases available within the platform.

		:getter: A list of :class:`~exterro.api.collections.Collection` objects.
		:type: :class:`~exterro.api.collections.Collections`
		"""
		if not self._collections:
			self._collections = Collections(self)
		return self._collections
	
	@property
	def custom_fields(self) -> list:
		"""Maintains all custom fields available within the platform.

		:getter: A list of :class:`Field` objects.
		:type: :class:`Fields`
		"""
		raise NotImplementedError("Custom-fields sub-module is Not Implemented yet.")
		if not self._fields:
			self._fields = None
		return self._fields
	
	@property
	def groups(self) -> list:
		"""Maintains all groups available within the platform.

		:getter: A list of :class:`Group` objects.
		:type: :class:`Groups`
		"""
		if not self._groups:
			request_type, ext = group_list_ext
			resp = self.send_request(request_type, ext)
			self._groups = utilities.AttributeFinderMixin(resp.json())
		return self._groups

	@property
	def users(self) -> list:
		"""Maintains all users available within the platform.

		:getter: A list of :class:`User` objects.
		:type: :class:`Users`
		"""
		if not self._users:
			request_type, ext = user_list_ext
			resp = self.send_request(request_type, ext)
			self._users = utilities.AttributeFinderMixin(resp.json())
		return self._users