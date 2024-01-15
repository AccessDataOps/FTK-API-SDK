## /api/attributes.py

"""
Holds onto all possible attributes for use in filters and pagination.
"""

from enum import IntEnum
from numbers import Real
from typing import Any

from .extensions import attribute_list_ext
from .filters import (generate_string_filter, generate_number_filter,
	StringOperator, NumberOperator, )
from ..utilities import AttributeFinderMixin, AttributeMappedDict

## Declaring __all__

__all__ = ("Attributes", "Attribute", "AttributeType", )

##

class AttributeType(IntEnum):
	"""Contains the enumeration values regarding attribute data types.

	`INT32 = 7`

	`INT64 = 9`

	`STRING = 11`
	"""
	INT32 = 7
	INT64 = 9
	STRING = 11
	INT_ALL = INT32 | INT64

##

class Attribute(AttributeMappedDict):
	"""Attribute is a dictionary subclass used to maintain data about a backend
	attribute. This datatype supports comparisons against the object, generating
	API JSON filters when compared against. These filters are then used within
	the API calls to reduce a dataset during the call.
	"""

	__generation_map = {
		AttributeType.INT32: (generate_number_filter, NumberOperator),
		AttributeType.INT64: (generate_number_filter, NumberOperator),
		AttributeType.STRING: (generate_string_filter, StringOperator)
	}
	__generation_default_string = (generate_string_filter, StringOperator)
	__generation_default_int = (generate_string_filter, StringOperator)

	## Properties

	@property
	def name(self):
		"""The name of the attribute."""
		return self["attributeUniqueName"]

	@property
	def id(self):
		"""The ID of the attribute."""
		return self["columnID"]

	## Overrides

	def __repr__(self):
		return f"Attribute<{self.name=}, {self.id=}>"

	## Comparators

	def __eq__(self, other: Any):
		"""Generates a filter against the attribute where object is equal to.
		"""
		filter_func, op_enum = Attribute.__generation_map.get(
			self["dataType"],
			Attribute.__generation_default_string
		)
		return filter_func(self.name, op_enum.EqualTo, other)

	def __ne__(self, other: Any):
		"""Generates a filter against the attribute where object not equal to.
		"""
		filter_func, op_enum = Attribute.__generation_map.get(
			self["dataType"],
			Attribute.__generation_default_string
		)
		return filter_func(self.name, op_enum.NotEqualTo, other)

	def __lt__(self, other: Real):
		"""Generates a filter against the attribute where object less than."""
		if self["dataType"] == AttributeType.STRING:
			raise TypeError("Cannot use __lt__ comparator on String attribute.")

		filter_func, op_enum = Attribute.__generation_map.get(
			self["dataType"],
			Attribute.__generation_default_int
		)
		return filter_func(self.name, op_enum.LessThan, other)

	def __gt__(self, other: Real):
		"""Generates a filter against the attribute where object more than."""
		if self["dataType"] == AttributeType.STRING:
			raise TypeError("Cannot use __gt__ comparator on String attribute.")

		filter_func, op_enum = Attribute.__generation_map.get(
			self["dataType"],
			Attribute.__generation_default_int
		)
		return filter_func(self.name, op_enum.GreaterThan, other)

	def __le__(self, other: Real):
		"""Generates a filter against the attribute where object less than or
		equal to."""
		if self["dataType"] == AttributeType.STRING:
			raise TypeError("Cannot use __le__ comparator on String attribute.")

		filter_func, op_enum = Attribute.__generation_map.get(
			self["dataType"],
			Attribute.__generation_default_int
		)
		return filter_func(self.name, op_enum.LessThanEqualTo, other)

	def __ge__(self, other: Real):
		"""Generates a filter against the attribute where object more than or
		equal to."""
		if self["dataType"] == AttributeType.STRING:
			raise TypeError("Cannot use __ge__ comparator on String attribute.")

		filter_func, op_enum = Attribute.__generation_map.get(
			self["dataType"],
			Attribute.__generation_default_int
		)
		return filter_func(self.name, op_enum.GreaterThanEqualTo, other)

	def __contains__(self, other: str):
		"""Generates a filter against the attribute where object contains value.
		"""
		if self["dataType"] in (AttributeType.INT32, AttributeType.INT64):
			raise TypeError("Cannot use __contains__ comparator on Int attribute.")

		filter_func, op_enum = Attribute.__generation_map.get(
			self["dataType"],
			Attribute.__generation_default_string
		)
		return filter_func(self.name, op_enum.Contains, other)

	def within(self, other: list):
		"""Generates a filter against the attribute where object contains self.
		"""
		filter_func, op_enum = Attribute.__generation_map.get(
			self["dataType"],
			Attribute.__generation_default_int
		)
		return filter_func(self.name, op_enum.Includes, other)

	def startswith(self, other: str):
		"""Generates a filter against the attribute where object starts with.
		This function will raise TypeError upon running this function with an
		unsupported type, e.g. integer, float, array.

		:param other: The string that the object should start with.
		:type other: string"""
		if self["dataType"] in (AttributeType.INT32, AttributeType.INT64):
			raise TypeError("Cannot use startswith comparator on Int attribute.")

		filter_func, op_enum = Attribute.__generation_map.get(
			self["dataType"],
			Attribute.__generation_default_string
		)
		return filter_func(self.name, op_enum.StartsWith, other)

	def endswith(self, other: str):
		"""Generates a filter against the attribute where object ends with. This
		function will raise TypeError upon running this function with an
		unsupported type, e.g. integer, float, array.

		:param other: The string that the object should end with.
		:type other: string
		"""
		if self["dataType"] in (AttributeType.INT32, AttributeType.INT64):
			raise TypeError("Cannot use endswith comparator on Int attribute.")

		filter_func, op_enum = Attribute.__generation_map.get(
			self["dataType"],
			Attribute.__generation_default_string
		)
		return filter_func(self.name, op_enum.EndsWith, other)

	@classmethod
	def by_name(cls, value: str):
		"""Finds the attribute where the name matches the value supplied.

		:param value: Name to match against.
		:type value: string

		:return: The attribute found. None if not found.
		:rtype: :class:`~exterro.api.attributes.Attribute`
		"""
		return Attributes().first_matching_attribute(
			"attributeUniqueName", value)

##

class Singleton(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]

class Attributes(AttributeFinderMixin, metaclass=Singleton):
	"""Maintains a list of all attributes available within the platform. This
	class always returns the same object of attrbitues, known as a Singleton.
	This class supports lookup functions from
	:class:`~exterro.utilities.AttributeFinderMixin`.

	:param client: The client to send the request too.
	:type client: :class: ~`exterro.client.Client`
	
	:param update: Should the object automatically request, updating itself?
	:type update: bool, optional
	"""

	def __init__(self, client=None, update:bool = True):
		super().__init__()

		if client:
			self.client = client

		if update:
			self.update()

	def update(self):
		"""Updates the list to contain the list of attributes returned by the
		API service."""
		self.clear()
		request_type, ext = attribute_list_ext
		response = self.client.send_request(request_type, ext)
		self.extend(map(lambda x: Attribute(**x), response.json()))