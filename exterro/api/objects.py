## /api/objects.py

"""

"""

from typing import Any

from ..logging import logger
from ..utilities import AttributeMappedDict

## Declaring __all__

__all__ = ("Object", )

## Object construction

class Object(AttributeMappedDict):
	"""Maintains information about a entry within the case. To
	access any attributes, perform a __getitem__ call to the
	attribute name.
	"""
	def __init__(self, case, **kwargs):
		super().__init__()
		self._case = case
		self._labels = None

		self.update(kwargs)
		
	def __repr__(self):
		id = self.get('id', 0)
		return f"Object<{id=}>"

	def __getitem__(self, item):
		if not super().__contains__(item):
			for attribute_obj in self["metaData"]:
				if attribute_obj["staticAttributeUniqueName"] == item:
					return attribute_obj["value"]
		return super().__getitem__(item)

	@property
	def labels(self):
		if not self._labels:
			self._labels = self._case.labels
		applied_labels = self["appliedLabelIds"]
		labels = tuple()
		if not applied_labels:
			return labels
		for label_id in applied_labels:
			label = self._labels.first_matching_attribute("labelID", label_id)
			if label:
				labels += (label, )
		return labels