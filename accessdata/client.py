## /client.py

"""
The client and credential handler to send requests
between the client python environment and the API
service.
"""

from .api.ftkconnect import FTKConnect
from requests import Session, Response
from typing import Union

from .api.attributes import Attributes
from .api.cases import Cases
from .api.extensions import status_check_ext, login_ext
from .logging import logger
from . import utilities

## Declaring __all__

__all__ = ("Client", )

## Build our URL path and headers for later use.

class Client:
	"""Instantiates the URL and Authentication against the API
	service. All extra arguments are passed to the session creator.

	By default the constructor will try to validate the API service's status.
	Supply `validate=False` as a keyword argument to stop this behaviour.

	:param url: The base url the API service is listening upon.
	:type url: string

	:param apikey: The API key to use to authenticate against the API service.
	:type apikey: string

	:param validate: Should the client check the service status upon construct? Default: True
	:type validate: bool, optional

	Making a HTTP Client:

	.. code-block:: python

		from accessdata.client import Client

		client = Client("http://localhost:4443/", "api-key-guid")
	
	Making a HTTPS Client:

	.. code-block:: python

		from accessdata.client import Client

		client = Client("https://localhost:4443/", "api-key-guid", validate=False)
		client.session.cert = "/path/to/cert/file"
	"""

	__request_types = ("delete", "get", "patch", "post", "put")

	def __init__(self, url: str, apikey: Union[str, None], validate: bool=True, *args, **kwargs):
		self.url = url

		self.session = Session()

		if apikey:
			# self.session.headers = {"EnterpriseApiKey": apikey}
			data = {"Username":kwargs["username"],"Password":kwargs["password"]}
			request_type, ext = login_ext
			response = self.send_request(request_type,ext,data=data)

		if validate:
			request_type, ext = status_check_ext
			response = self.send_request(request_type, ext)
			if response.json() != "Ok":
				raise ConnectionError("AccessData API responded with bad 'status'.")

		self._attributes = None
		self._cases = None
		self._connect = None
		self._fields = None
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
		return request_func(self.session, self.url + extension, *args, **kwargs)

	@property
	def attributes(self) -> Attributes:
		"""Maintains all attributes (columns) that can be used for filtering and viewing.

		:getter: A list of :class:`~accessdata.rest.attributes.Attribute` objects.
		:type: list[:class:`~accessdata.rest.attributes.Attribute`]
		"""
		if not self._attributes:
			self._attributes = Attributes(self)
		return self._attributes

	@property
	def cases(self) -> Cases:
		"""Maintains all cases available within the platform.

		:getter: A list of :class:`~accessdata.rest.cases.Case` objects.
		:type: :class:`~accessdata.rest.cases.Cases`
		"""
		if not self._cases:
			## Instantiating Attributes... without it case usage falls apart.
			self._attributes = Attributes(self)
			self._cases = Cases(self)
		return self._cases
	
	@property
	def users(self) -> list:
		"""Maintains all users available within the platform.

		:getter: A list of :class:`User` objects.
		:type: :class:`Users`
		"""
		raise NotImplementedError("Users sub-module is Not Implemented yet.")
		if not self._users:
			self._attributes = Users(self)
		return self._users

	@property
	def connect(self):
		"""

		"""

		if not self._connect:
			self._connect = FTKConnect(self)
		return self._connect
