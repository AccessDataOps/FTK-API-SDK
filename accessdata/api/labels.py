## /api/labels.py

"""
Label management and application endpoints enable usage of tagging evidence
 objects. Integrates into the Case class to provide seamless use of AccessData
 API.
"""

from dataclasses import dataclass
from typing import Any

from .extensions import (label_list_ext, label_create_ext,
	label_objects_job_ext, label_objects_list_ext)
from .jobs import Job
from .objects import Object
from ..logging import logger
from ..utilities import AttributeFinderMixin, AttributeMappedDict

## Declaring __all__

__all__ = ("Labels", "Label", )

## Label class construction

class Label(AttributeMappedDict):

	def __init__(self, case, **kwargs):
		super().__init__()

		self.client = case.client
		self._case = case

		self.update(kwargs)
		
	def __repr__(self):
		identifier = self.get('name', None)
		id = self.get('id', 0)
		return f"Label<{identifier}, {id}>"

	def apply(self, filter: dict = {}):
		"""Applies the label to the objects selected from the filter.

		:param filter: The filter to reduce the file objects around.
		:type filter: dict, optional
		"""
		caseid = self._case.get("id", 0)
		id = self.get('id', 0)
		request_type, ext = label_objects_job_ext
		response = self.client.send_request(request_type,
			ext.format(caseid=caseid),
			json={
				"folderAssignmentOptions": {
					"filterForFolder": {},
					"searchSessionID": None,
					"folderIDsForAssign": [ id, ]
				},
				"filter": filter
			}
		)
		return Job(self._case, id=response.json())

	@property
	def objects(self):
		"""Property to get all objects labelled by the label."""
		caseid = self._case.get("id", 0)
		id = self.get('id', 0)
		request_type, ext = label_objects_list_ext
		response = self.client.send_request(request_type,
			ext.format(caseid=caseid, labelid=id))
		return list(map(lambda id: Object(self._case, id=id), response.json()))

## Labels class construction

class Labels(AttributeFinderMixin):
	"""Labels is a subclass of list maintaining all labels within a
	case. This  class supports lookup functions from
	:class:`~accessdata.utilities.AttributeFinderMixin`.

	:param case: The parent case.
	:type case: :class:`~accessdata.api.cases.Case`
	"""

	def __init__(self, case, update=True):
		self.client = case.client
		self._case = case

		if update:
			self.update()

	def update(self):
		"""Refreshes the Labels instance with the newest evidence list
		from the API service."""
		self.clear()
		caseid = self._case.get("id", 0)
		request_type, ext = label_list_ext
		response = self.client.send_request(request_type,
			ext.format(caseid=caseid))
		labels = map(lambda x: Label(self._case, **x), response.json())
		self.extend(labels)

	def create(self, label: Label=None, **kwargs):
		"""Creates a new label using the label object and kwargs
		supplied. All kwargs are passed into the label object to then
		be passed to the request as parameters.

		:param label: The label object to instantiate the new label from.
		:type label: :class:`~accessdata.api.labels.Label`, optional

		:return: The new label object that was created prior to its creation.
		:rtype: :class:`~accessdata.api.labels.Label`"""
		if kwargs and label:
			label.update(kwargs)
		elif kwargs:
			label = Label(self._case, **kwargs)

		caseid = self._case.get("id", 0)
		request_type, ext = label_create_ext
		response = self.client.send_request(request_type,
			ext.format(caseid=caseid), json=label)

		label.update(response.json())
		self.append(label)

		return label
