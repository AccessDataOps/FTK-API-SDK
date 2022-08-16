## /api/cases.py

"""
The Case management system to handle all case information and sub-components.
"""

from os.path import join
from typing import Any, Optional

from .evidence import Evidence, ProcessedEvidence
from .extensions import case_create_ext, case_list_ext, server_setting_ext
from .jobs import Jobs
from .labels import Labels
from ..logging import logger
from ..utilities import AttributeFinderMixin, AttributeMappedDict

## Declaring __all__

__all__ = ("Cases", "Case", )

## Case class construction

class Case(AttributeMappedDict):
	"""Case is a dictionary subclass used to maintain data about a backend case.
	This class instantiates all required parameters for case creation through
	the API service removing extra requirements from the user.
	`ftkcasefolderpath` and `responsivefilepath` are both defaulted to their
	predefined locations within Enterprise or FTK Central, however can be
	overriden through supplication as parameters.

	:param client: The client to send the request too.
	:type client: :class: ~`accessdata.client.Client`

	:param name: The name of the case.
	:type name: string

	:param ftkcasefolderpath: Case related data folder. Supports UNC paths.
	:type ftkcasefolderpath: string, optional
	
	:param responsivefilepath: Job related data folder. Supports UNC paths.
	:type responsivefilepath: string, optional
	"""

	def __init__(self, client, name: str, ftkcasefolderpath: str=None,
			responsivefilepath: str=None, **kwargs):
		super().__init__()
		self.client = client

		if ftkcasefolderpath == None:
			ftkcasefolderpath = join(Cases.DIRECTORY, name)

		if responsivefilepath == None:
			responsivefilepath = join(Cases.DIRECTORY, name, "Jobs")

		super().update(
			{
				"name": name,
				"ftkcasefolderpath": ftkcasefolderpath,
				"responsivefilepath": responsivefilepath
			} | kwargs
		)

		self._evidence = None
		self._jobs = None
		self._labels = None
		self._processed_evidence = None
		
	def __repr__(self):
		name = self.get('name', None)
		id = self.get('id', 0)
		return f"Case<{name=}, {id=}>"

	@property
	def evidence(self):
		"""Property to target the evidence items within a case.

		:rtype: :class:`~accessdata.api.evidence.Evidence`
		"""
		if not self._evidence:
			self._evidence = Evidence(self)
		return self._evidence

	@property
	def jobs(self):
		"""Property to target the jobs created this session within a case.

		:rtype: :class:`~accessdata.api.jobs.Jobs`
		"""
		if not self._jobs:
			self._jobs = Jobs(self)
		return self._jobs
	
	@property
	def labels(self):
		"""Property to target the labels within a case.

		:rtype: :class:`~accessdata.api.labels.Labels`
		"""
		if not self._labels:
			self._labels = Labels(self)
		return self._labels

	@property
	def processed_evidence(self):
		"""Property to target the processed evidence items within a case.

		:rtype: :class:`~accessdata.api.evidence.ProcessedEvidence`
		"""
		if not self._processed_evidence:
			self._processed_evidence = ProcessedEvidence(self)
		return self._processed_evidence

	def update(self):
		"""Refreshes the Case instance with the newest case JSON object
		from the API service."""
		request_type, ext = case_list_ext
		response = self.client.send_request(request_type, ext)
		case = next(x for x in response.json() if x["id"] == self["id"])
		super().update(case)

	def export_portable_version(self, directory: str,
		include_ftkplus: Optional[bool] = True, filter: dict = None,
		foldername: str = None):
		"""Exports a portable version of the case to the target directory
		using the filter provided. Optional arguments include whether to
		export FTK Plus with the new case folder or not.
		
		:param directory: The directory to export too.
		:type directory: string

		:param include_ftkplus: Should export FTK+ to the directory?
		:type include_ftkplus: bool, optional

		:param filter: The filter to apply before exporting.
		:type filter: dict, optional

		:param foldername: The name of the parent folder.
		:type foldername: string
		"""

		request_type, ext = case_create_portable_ext
		response = self.client.send_request(request_type,
			ext.format(caseid=self.id),
			json={
				"uifilter": filter or {},
				"copyqview": include_ftkplus,
				"outputpath": directory,
				"foldername": foldername or f"Portable {self.name}"
			}
		)
		jobid = response.json()
		job = Job(self.case, id=jobid)
		return job

## Cases class construction

class Cases(AttributeFinderMixin):
	"""A subclass of list that maintains all cases within the platform. This 
	class supports lookup functions from
	:class:`~accessdata.utilities.AttributeFinderMixin`.

	:param client: The client to send the request too.
	:type client: :class: ~`accessdata.client.Client`
	
	:param update: Should the object automatically request, updating itself?
	:type update: bool, optional
	"""

	DIRECTORY = ""

	def __init__(self, client, update=True):
		super().__init__()
		self.client = client

		request_type, ext = server_setting_ext
		response = self.client.send_request(request_type,
			ext.format(setting="FTKDefaultPath"))
		Cases.DIRECTORY = response.json()

		if update:
			self.update()

	def create(self, case: Case=None, **kwargs):
		"""Creates a new case object using the case object and kwargs
		supplied. All kwargs are passed into the case object to then
		be passed to the request as parameters.

		:param case: The case object to instantiate the new case from.
		:type case: :class:`~accessdata.api.cases.Case`, optional

		:return: The new case object that was created prior to its creation.
		:rtype: :class:`~accessdata.api.cases.Case`
		"""
		if kwargs and case:
			case.update(kwargs)
		elif kwargs:
			case = Case(self.client, **kwargs)

		request_type, ext = case_create_ext
		response = self.client.send_request(request_type, ext, json=case)
		caseid = response.json()
		case["id"] = caseid

		self.append(case)
		return case

	def update(self):
		"""Refreshes the Cases instance with the newest case list
		from the API service."""
		self.clear()
		request_type, ext = case_list_ext
		response = self.client.send_request(request_type, ext)
		cases = map(lambda x: Case(self.client, **x), response.json())
		self.extend(cases)