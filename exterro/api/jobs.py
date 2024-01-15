## /api/jobs.py

"""
Job classes to hold onto multiple jobs and update job statuses upon request.
 Integrates into the Case class to provide seamless use of the Exterro FTK API.
"""

from enum import IntEnum
from json import loads
from typing import Any

from .extensions import job_status_ext
from ..logging import logger
from ..utilities import AttributeFinderMixin, AttributeMappedDict

## Declaring __all__

__all__ = ("Job", "Jobs", "JobState", )

## JobState enum construction

class JobState(IntEnum):
	"""Contains the enumeration values regarding job statuses.

	`Submitted = 0`

	`InProgress = 1`
	
	`Cancelled = 2`

	`Failed = 3`

	`Completed/Finished = 4`
	"""
	Submitted = 0
	InProgress = 1
	Cancelled = 2
	Failed = 3
	Completed = 4
	Finished = 4
	CompletedWithErrors = 6

## Job class construction

class Job(AttributeMappedDict):
	"""Job subclasses dict to maintain information about the
	relevant job within the platform. To retrieve most recent
	information about the job, simply call `update`.

	:param case: The parent case.
	:type case: :class:`~exterro.api.cases.Case`

	:param id: The id of the job.
	:type id: int
	"""

	def __init__(self, case, **kwargs):
		super().__init__()
		self.client = case.client
		self._case = case

		super().update(kwargs)
		self.update()

	def update(self):
		"""Updates the information about the job."""
		caseid = self._case.get("id", 0)
		jobid = self.get("id", 0)
		request_type, ext = job_status_ext
		response = self.client.send_request(request_type,
			ext.format(caseid=caseid, jobid=jobid))
		data = response.json()
		data["state"] = JobState.__getattr__(data["state"])
		data["resultData"] = loads(data["resultData"])
		super().update(data)

	@property
	def state(self):
		"""Property to get the state of the job.

		:rtype: :class:`~exterro.api.jobs.JobState`
		"""
		return self["state"]

	def __repr__(self):
		"""Return a string representation of the job.

		:rtype: string
		"""
		return f"Job<caseid={self._case.id}, id={self.id}, state={str(self.state)}>"

## Jobs class construction

class Jobs(AttributeFinderMixin):
	"""Jobs is a subclass of list maintaining all jobs within a case from 
	this session. This class supports lookup functions from
	:class:`~exterro.utilities.AttributeFinderMixin`.

	:param case: The parent case.
	:type case: :class:`~exterro.api.cases.Case`
	"""

	def __init__(self, case):
		super().__init__()
		self.client = case.client
		self._case = case

	def update(self):
		"""Refreshes the Jobs instance with the newest job information
		from the API service."""
		for job in self:
			job.update()