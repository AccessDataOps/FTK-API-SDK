## /api/evidence.py

"""
Evidence management and processing endpoint management. Integrates into the Case
class to provide seamless use of the Exterro FTK API.
"""

from enum import IntEnum
from math import ceil, floor
from time import sleep
from typing import Any, Union

from .attributes import Attribute
from .extensions import (evidence_list_ext, evidence_process_ext,
	evidence_processed_list_ext, object_page_list_ext, export_natives_ext,
	search_report_ext)
from .filters import and_
from .jobs import Job, JobState
from .objects import Object
from ..logging import logger
from ..utilities import AttributeFinderMixin, AttributeMappedDict

## Declaring __all__

__all__ = ("Evidence", "EvidenceObject", "EvidenceType", )

## EvidenceType enum construction

class EvidenceType(IntEnum):
	"""Contains the enumeration values regarding evidence data types.

	`FILE = 0`

	`DIRECTORY = 1`
	
	`IMAGE_FILE = 2`
	"""
	FILE = 0
	DIRECTORY = 1
	IMAGE_FILE = 2

## EvidenceObject class construction

class EvidenceObject(AttributeMappedDict):

	def __init__(self, case, **kwargs):
		super().__init__()

		self._case = case

		self.update(kwargs)
		
	def __repr__(self):
		path = self.get('filePath', None)
		id = self.get('evidenceId', 0)
		return f"EvidenceObject<{path=}, {id=}>"

	def browse(self, pagenumber: int, pagesize: int, filter: dict = {},
			attributes: list = []):
		"""Browses through objects in the evidence items in a paged system,
		similar to a catalog. The objects to browse can be reduced using a filter
		before reading the page information. Alongside this, to view specific
		attributes of these objects, supply the attributes within the attributes
		iterable parameter.

		:param pagenumber: The number of the page to view.
		:type pagenumber: int

		:param pagesize: The amount of objects to return in the page.
		:type pagesize: int

		:param filter: The filter to apply before paging.
		:type filter: dict, optional

		:param attributes: The attributes to retrieve about the objects.
		:type attributes: list[:class:`~exterro.api.attributes.Attribute`], optional
		"""
		evidence_id = Attribute.by_name("EvidenceID")
		if filter:
			return _browse(self._case, pagenumber, pagesize,
				and_(filter, evidence_id == self.get("evidenceId", 0)), attributes)
		return _browse(self._case, pagenumber, pagesize,
			evidence_id == self.get("evidenceId", 0), attributes)

	def iterate(self, pagesize=100, filter: dict = {}, attributes: list = []):
		"""Iterates through all objects in the evidence items in a paged system.
		The objects to iterate through can be reduced using a filter. Alongside
		this, to view specific attributes of these objects, supply the
		attributes within the attributes iterable parameter.

		:param pagesize: The amount of objects to return in a single page.
		:type pagesize: int, optional

		:param filter: The filter to apply before iterating.
		:type filter: dict, optional

		:param attributes: The attributes to retrieve about the objects.
		:type attributes: list[:class:`~exterro.api.attributes.Attribute`], optional

		:return: A list of Objects.
		:rtype: list[:class:`~exterro.api.objects.Object`]
		"""
		evidence_id = Attribute.by_name("EvidenceID")
		if filter:
			return _iterate(self._case, pagesize,
				and_(filter, evidence_id == self.get("evidenceId", 0)), attributes)
		return _iterate(self._case, pagesize,
			evidence_id == self.get("evidenceId", 0), attributes)


	def search_keywords(self, keywords, filter: dict = {}, attributes: list = [], labels: Union[list, None]=None, **kwargs):
		"""Runs a keyword search against the case evidence and iterates
		through the objects that flag against the keywords. Filters can be specified
		to reduce the content searched and attribute lists can be specified
		to get relevant information. This function will await for the search job to
		complete.

		:param keywords: The list of keywords to search for.
		:type keywords: list[string]

		:param filter: The filter to apply before iterating.
		:type filter: dict, optional

		:param attributes: The attributes to retrieve about the objects.
		:type attributes: list[:class:`~exterro.api.attributes.Attribute`], optional

		:param labels: The list of labels to apply to the objects.
		:type labels: list[string], optional

		:return: A list of Objects.
		:rtype: list[:class:`~exterro.api.objects.Object`]
		"""
		evidence_id = Attribute.by_name("EvidenceID")
		if filter:
			return _search_keywords(self._case, keywords,
				and_(filter, evidence_id == self.get("evidenceId", 0)), attributes, labels, **kwargs)
		return _search_keywords(self._case, keywords,
				evidence_id == self.get("evidenceId", 0), attributes, labels, **kwargs)


	def export_natives(self, path: str, filter: dict = {}, *args, **kwargs):
		"""Exports objects from the evidence to the supplied path. The exported
		objects can be reduced by supplying a filter. By default the export
		will export files and folder in the path they appear within the
		evidence item. Exporting from a lower level EvidenceObject will
		automatically filter specifically for this evidences child objects
		(using this evidence's ID).

		:param path: The path to export objects too.
		:type path: string

		:param filter: The filter to apply before exporting.
		:type filter: dict, optional

		:return: The job created.
		:rtype: :class:`~exterro.api.jobs.Job`
		"""
		evidence_id = Attribute.by_name("EvidenceID")
		if filter:
			return _export_natives(self._case, path,
				filter=and_(filter, evidence_id == self.get("evidenceId", 0)), *args, **kwargs)
		return _export_natives(self._case, path,
			filter=evidence_id == self.get("evidenceId", 0), *args, **kwargs)
		

	@classmethod
	def process_and_create(cls, case, evidencepath: str,
			evidencetype: EvidenceType,  **kwargs):
		"""Processes a new evidence object using the case object and kwargs
		supplied. The kwargs are passed directly into the parameters for the
		evidence process API call.

		:param case: The case to process within.
		:type case: :class:`~exterro.api.cases.Case`

		:param evidencepath: The path directly to the evidence to handle.
		:type evidencepath: string

		:param evidencetype: The type of evidence to process.
		:type evidencetype: :class:`~exterro.api.evidence.EvidenceType`

		:return: The new evidence object and the jobs created.
		:rtype: tuple[:class:`~exterro.api.evidence.EvidenceObject`, list[int]]
		"""
		process_json = {
			"evidencetocreate": {
				"evidencepath": evidencepath,
				"evidencetype": evidencetype
			}
		} | kwargs

		kwargs["filePath"] = evidencepath
		kwargs["evidenceType"] = evidencetype

		caseid = case.get("id", 0)
		request_type, ext = evidence_process_ext
		response = case.client.send_request(request_type,
			ext.format(caseid=caseid), json=process_json)
		
		return cls(case, **kwargs), response.json()

## Evidence class construction

class Evidence(AttributeFinderMixin):
	"""Evidence is a subclass of list maintaining all evidence items within a
	case. The class provides support for processing files/images as well as
	browsing, iterating, and exporting of objects within processed items. This 
	class supports lookup functions from
	:class:`~exterro.utilities.AttributeFinderMixin`.

	:param case: The parent case.
	:type case: :class:`~exterro.api.cases.Case`

	:param update: Should the object automatically request, updating itself?
	:type update: bool, optional
	"""

	def __init__(self, case, update=True):
		super().__init__()
		self.client = case.client
		self._case = case

		if update:
			self.update()

	def update(self):
		"""Refreshes the Evidence instance with the newest evidence list
		from the API service."""
		self.clear()
		caseid = self._case.get("id", 0)
		request_type, ext = evidence_list_ext
		response = self.client.send_request(request_type,
			ext.format(caseid=caseid))
		evidenceobjects = map(lambda x: EvidenceObject(self._case, **x),
			response.json())
		self.extend(evidenceobjects)

	def process(self, evidencepath: str, evidencetype: EvidenceType, **kwargs):
		"""Processes a new evidence object using the case object and kwargs
		supplied. The kwargs are passed directly into the parameters for the
		evidence process API call.

		:param evidencepath: The path directly to the evidence to handle.
		:type evidencepath: string

		:param evidencetype: The type of evidence to process.
		:type evidencetype: :class:`~exterro.api.evidence.EvidenceType`
		"""
		evidenceobject, jobids = EvidenceObject.process_and_create(self._case,
			evidencepath, evidencetype, **kwargs)

		self.append(evidenceobject)

		jobs = list(map(lambda jobid: Job(self._case, id=jobid), jobids))

		self._case.jobs.extend(jobs)

		return jobs

	def browse(self, pagenumber: int, pagesize: int, filter: dict = {},
			attributes: list = []):
		"""Browses through objects in the evidence items in a paged system,
		similar to a catalog. The objects to browse can be reduced using a filter
		before reading the page information. Alongside this, to view specific
		attributes of these objects, supply the attributes within the attributes
		iterable parameter.

		:param pagenumber: The number of the page to view.
		:type pagenumber: int

		:param pagesize: The amount of objects to return in the page.
		:type pagesize: int

		:param filter: The filter to apply before paging.
		:type filter: dict, optional

		:param attributes: The attributes to retrieve about the objects.
		:type attributes: list[:class:`~exterro.api.attributes.Attribute`], optional
		"""
		return _browse(self._case, pagenumber, pagesize, filter, attributes)

	def iterate(self, pagesize=100, filter: dict = {}, attributes: list = []):
		"""Iterates through all objects in the evidence items in a paged system.
		The objects to iterate through can be reduced using a filter. Alongside
		this, to view specific attributes of these objects, supply the
		attributes within the attributes iterable parameter.

		:param pagesize: The amount of objects to return in a single page.
		:type pagesize: int, optional

		:param filter: The filter to apply before iterating.
		:type filter: dict, optional

		:param attributes: The attributes to retrieve about the objects.
		:type attributes: list[:class:`~exterro.api.attributes.Attribute`], optional

		:return: A list of Objects.
		:rtype: list[:class:`~exterro.api.objects.Object`]
		"""
		return _iterate(self._case, pagesize, filter, attributes)

	def search_keywords(self, keywords, filter: dict = {}, attributes: list = [], labels: Union[list, None]=None, **kwargs):
		"""Runs a keyword search against the case evidence and iterates
		through the objects that flag against the keywords. Filters can be specified
		to reduce the content searched and attribute lists can be specified
		to get relevant information. This function will await for the search job to
		complete.

		:param keywords: The list of keywords to search for.
		:type keywords: list[string]

		:param filter: The filter to apply before iterating.
		:type filter: dict, optional

		:param attributes: The attributes to retrieve about the objects.
		:type attributes: list[:class:`~exterro.api.attributes.Attribute`], optional

		:param labels: The list of labels to apply to the objects.
		:type labels: list[string], optional

		:return: A list of Objects.
		:rtype: list[:class:`~exterro.api.objects.Object`]
		"""
		return _search_keywords(self._case, keywords, filter, attributes, labels, **kwargs)

	def export_natives(self, path: str, filter: dict = {}, **kwargs):
		"""Exports objects from the evidence to the supplied path. The exported
		objects can be reduced by supplying a filter. By default the export
		will export files and folder in the path they appear within the
		evidence item.

		:param path: The path to export objects too.
		:type path: string

		:param filter: The filter to apply before exporting.
		:type filter: dict, optional

		:return: The job created.
		:rtype: :class:`~exterro.api.jobs.Job`
		"""
		return _export_natives(self._case, path, filter, **kwargs)


def _browse(case, pagenumber: int, pagesize: int, filter: dict = {},
		attributes: list = []):
	"""Browses through objects in the evidence items in a paged system,
	similar to a catalog. The objects to browse can be reduced using a filter
	before reading the page information. Alongside this, to view specific
	attributes of these objects, supply the attributes within the attributes
	iterable parameter.

	:param pagenumber: The number of the page to view.
	:type pagenumber: int

	:param pagesize: The amount of objects to return in the page.
	:type pagesize: int

	:param filter: The filter to apply before paging.
	:type filter: dict, optional

	:param attributes: The attributes to retrieve about the objects.
	:type attributes: list[:class:`~exterro.api.attributes.Attribute`], optional
	"""
	caseid = case.get("id", 0)
	columns = list(map(lambda attr: {"attribute": attr}, attributes))
	request_type, ext = object_page_list_ext
	response = case.client.send_request(request_type,
		ext.format(caseid=caseid, pagenumber=pagenumber, pagesize=pagesize),
		json={
			"columns": columns,
			"filter": filter
		}
	)
	return list(
		map(
			lambda obj: Object(case, **obj),
			response.json()["entities"]
		)
	)


def _iterate(case, pagesize=100, filter: dict = {}, attributes: list = []):
	caseid = case.get("id", 0)
	columns = list(map(lambda attr: {"attribute": attr}, attributes))

	pagenumber = 1
	request_type, ext = object_page_list_ext
	response = case.client.send_request(request_type,
		ext.format(caseid=caseid, pagenumber=pagenumber, pagesize=pagesize),
		json={
			"columns": columns,
			"filter": filter
		}
	)
	objects = response.json()
	yield from map(
		lambda obj: Object(case, **obj),
		objects["entities"]
	)

	total_objects = int(objects["totalCount"])
	total_pages = floor(total_objects / pagesize) + 1
	while pagenumber < total_pages:
		pagenumber += 1
		response = case.client.send_request(request_type,
			ext.format(caseid=caseid, pagenumber=pagenumber, pagesize=pagesize),
			json={
				"columns": columns,
				"filter": filter
			}
		)
		objects = response.json()
		yield from map(
			lambda obj: Object(case, **obj),
			objects["entities"]
		)


def _search_keywords(case, keywords, filter: dict = {}, attributes: list = [], labels: Union[list, None]=None, **kwargs):
	caselabels = case.labels
	caseid = case.get("id", 0)

	if labels:
		labels_len = len(labels)
		if labels_len != len(keywords):
			raise ValueError("Keywords and Labels list must be of same length.")
	else:
		labels = list(map(lambda x: "API-Search " + x, keywords))

	labelids = []
	for label in labels:
		label = caselabels.first_matching_attribute("name", label) or caselabels.create(name=label)
		labelids.append(label.id)

	searchdata = {
		"name": "API-Search " + '-'.join(keywords),
		"assignlabel": True,
		"fulltextsearchonly": True,
		"criteria": {
			"terms": keywords,
			"searchParameters": kwargs
		},
		"searchterms": [
			{
				"label": labels[i],
				"term": keywords[i]
			} for i in range(0, len(labels))
		]
	}

	request_type, ext = search_report_ext
	response = case.client.send_request(request_type,
		ext.format(caseid=caseid), json=searchdata
	)

	job = Job(case, id=response.json())
	while job.state in (JobState.Submitted, JobState.InProgress):
		sleep(1)
		job.update()
	if job.state in (JobState.Failed, JobState.CompletedWithErrors):
		return []

	labelid = case.client.attributes.first_matching_attribute(
		"attributeUniqueName",
		"LabelID"
	)
	if filter:
		yield from _iterate(
			case,
			filter=and_(labelid.within(labelids), filter),
			attributes=attributes
		)
	else:
		yield from _iterate(
			case,
			filter=labelid.within(labelids),
			attributes=attributes
		)


def _export_natives(case, path, filter, *args, **kwargs):
	caseid = case.get("id", 0)
	request_type, ext = export_natives_ext
	response = case.client.send_request(request_type,
		ext.format(caseid=caseid),
		json={
			"checkprocessedobjectflag": False,
			"insertdata": False,
			"insertexternaldataonly": False,
			"runparser": False,
			"inputfolder": path,
			"uiFilter": filter
		} | kwargs
	)
	return Job(case, id=response.json())


class ProcessedEvidence(Evidence):

	def update(self):
		"""Refreshes the Evidence instance with the newest evidence list
		from the API service."""
		self.clear()
		caseid = self._case.get("id", 0)
		request_type, ext = evidence_processed_list_ext
		response = self.client.send_request(request_type,
			ext.format(caseid=caseid))
		evidenceobjects = map(lambda x: EvidenceObject(self._case, **x),
			response.json())
		self.extend(evidenceobjects)
