## /api/collections.py

"""
Collection management. Integrates into the Client, Case and Job
classes to provide seamless use of the Exterro FTK API.
"""

from datetime import datetime
from enum import IntEnum
from itertools import groupby

from .extensions import collection_task_list_ext, collection_execute_ext
from .jobs import Job
from ..logging import logger
from ..utilities import AttributeFinderMixin, AttributeMappedDict

## Declaring __all__

__all__ = ("Task", "Collection", "Collections", "CollectionState", )

##

class CollectionState(IntEnum):
	"""Contains the enumeration values for designating resultant collection states.
	"""
	Unknown = -1
	Blocked = 0
	Failed = 1
	InProgress = 2
	Completed = 3
	Finished = 3


class Task(AttributeMappedDict):
	def __init__(self, data):
		try:
			self.state = CollectionState[data["jobStatus"]]
		except:
			self.state = CollectionState.Unknown

		self.update(data)

	def __repr__(self):
		targetname = self.get("targetName", "")
		targetip = self.get("targetIP", "")
		state = self.state
		return f"Task<{targetname=}, {targetip=}, {state=}>"


class Collection(AttributeFinderMixin):
	"""Constructs a collection container for the underlying tasks """
	def __init__(self, caseid: int, tasks: list[Task]):
		self.caseid = caseid
		first = tasks[0]
		self.name = first["jobName"]
		self.id = first["jobId"]
		self.state = min(task.state for task in tasks)
		self.extend(tasks)

	def __repr__(self):
		caseid = self.caseid
		jobid = self.id
		name = self.name
		return f"Collection<{caseid=}, {jobid=}, {name=}>"
	
	@property
	def targets(self):
		return list(map(lambda task: task.targetName, self))
	
	@property
	def target_ips(self):
		return list(map(lambda task: task.targetIP, self))


class Collections(AttributeFinderMixin):
	"""Constructs an Collections container to prepare for collection and
	analysis jobs to be iterated and executed."""

	def __init__(self, client, update: bool=True):
		self.client = client

		if update:
			self.update()

	def update(self):
		self.clear()

		request_type, ext = collection_task_list_ext
		collections = self.client.send_request(request_type, ext)

		tasks = map(lambda taskobj: Task(taskobj), collections.json())
		groups = groupby(tasks, lambda task: task.get("jobId", 0))
		for key, group in groups:
			tasks = list(group)
			collection = Collection(tasks[0].get("caseId", 0), tasks)
			self.append(collection)

	def execute(self, case, templateid: str="", name: str="", targets: list[str]=[], custodians: list[str]=[]):
		caseid = case.id

		if not name:
			name = "API-Collection_" + datetime.now().isoformat()

		if not templateid:
			return None
		
		json = {
			"jobname": name,
			"case": str(caseid),
			"custodians": custodians,
			"targets": targets,
			"templateids": [templateid]
		}

		request_type, ext = collection_execute_ext
		resp = self.client.send_request(request_type, ext, json=json)

		return Job(case, id=resp.json())