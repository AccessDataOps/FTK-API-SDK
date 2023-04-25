## /api/agents.py

"""
Agent job management and endpoint management. Integrates into the Case
class to provide seamless use of AccessData API.
"""

from enum import IntEnum
from typing import Any

from .extensions import (agent_volatile_analysis_ext, agent_software_inventory_ext,
    agent_memory_acquisition_ext, agent_disk_acquisition_ext, agent_remediation_ext,
    agent_collection_ext)
from .jobs import Job
from ..logging import logger
from ..utilities import AttributeFinderMixin

## Declaring __all__

__all__ = ("Agent", "Agents", "ImageType", )

##

class ImageType(IntEnum):
    """Contains the enumeration values for designating resultant image
    collection types.

    `RAW = 0`

    `S01 = 1`

    `E01 = 2`

    `AFF = 3`
    """
    RAW = 0
    S01 = 1
    E01 = 2
    AFF = 3

class Agent:
    """Constructs an Agent container within a case to prepare for collection and
    analysis jobs to be carried out upon the targeted endpoint.

    :param case: The case object to prepare within.
    :type case: :class:`~accessdata.api.cases.Case`

    :param target: The address/netbios/fqdn of the endpoint.
    :type target: str
    """

    def __init__(self, case, target: str):
        self.client = case.client
        self._case = case

        self.target = target

    def analyse_volatile(self, **kwargs):
        """Runs a volatile memory analysis job on the endpoint and stores the
        resultant data as objects within the case. Any keyword arguments
        supplied are directly overriden in the body of the request.
        """
        return _analyse_volatile(
            self._case,
            [self.target, ],
            **kwargs
        )

    def acquire_disk(self, **kwargs):
        """Runs a disk collection on the endpoint and stores the
        resultant evidence file within the case folder. Any keyword arguments
        supplied are directly overriden in the body of the request.
        """
        return _acquire_disk(
            self._case,
            [self.target, ],
            **kwargs
        )

    def acquire_memory(self, **kwargs):
        """Runs a memory collection on the endpoint and stores the
        resultant evidence file within the case folder. Any keyword arguments
        supplied are directly overriden in the body of the request.
        """
        return _acquire_memory(
            self._case,
            [self.target, ],
            **kwargs
        )

    def software_inventory(self, **kwargs):
        """Runs a software inventory job on the endpoint and stores the
        resultant data is translated into case objects. Any keyword arguments
        supplied are directly overriden in the body of the request.
        """
        return _software_inventory(
            self._case,
            [self.target, ],
            **kwargs
        )

    def remediate(self, **kwargs):
        """Runs a remediation task on the endpoint. Any keyword arguments
        supplied are directly overriden in the body of the request.
        """
        return _remediate(
            self._case,
            [self.target, ],
            **kwargs
        )

    def collect(self, **kwargs):
        """Runs a collection task on the endpoint. Any keyword arguments
        supplied are directly overriden in the filter of the request.
        """
        return _collect_on_agent(
            self._case,
            [self.target, ],
            **kwargs
        )

##

class Agents(AttributeFinderMixin):
    """Constructs an Agents container within a case to prepare for collections
    and analysis jobs to be carried out upon the targeted endpoints.

    :param case: The case object to prepare within.
    :type case: :class:`~accessdata.api.cases.Case`

    :param agents: A list of Agent objects of the respective targets.
    :type agents: list[:class:`~accessdata.api.agents.Agent`]
    """

    def __init__(self, case, agents:list = [], *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.client = case.client
        self._case = case
        self.extend(agents)

    @classmethod
    def from_targets(cls, case, targets: list[str]):
        """A class method for building an `Agents` object from target addresses
        rather than supplying a list of `Agent` objects.

        :param case: The case object to prepare within.
        :type case: :class:`~accessdata.api.cases.Case`

        :param targets: A list of addresses/netbios names/fqdns of the targets.
        :type targets: list[str]
        """
        agents = list(map(lambda t: Agent(case, t), targets))
        instance = cls(case, agents)
        return instance

    def analyse_volatile(self, **kwargs):
        """Runs a volatile memory analysis job on the endpoints and stores the
        resultant data as objects within the case. Any keyword arguments
        supplied are directly overriden in the body of the request.
        """
        return _analyse_volatile(
            self._case,
            list(map(lambda agent: agent.target, self)),
            **kwargs
        )

    def acquire_disk(self, **kwargs):
        """Runs a disk collection on the endpoints and stores the
        resultant evidence file within the case folder. Any keyword arguments
        supplied are directly overriden in the body of the request.
        """
        return _acquire_disk(
            self._case,
            list(map(lambda agent: agent.target, self)),
            **kwargs
        )

    def acquire_memory(self, **kwargs):
        """Runs a memory collection on the endpoints and stores the
        resultant evidence file within the case folder. Any keyword arguments
        supplied are directly overriden in the body of the request.
        """
        return _acquire_memory(
            self._case,
            list(map(lambda agent: agent.target, self)),
            **kwargs
        )

    def software_inventory(self, **kwargs):
        """Runs a software inventory job on the endpoints and stores the
        resultant data is translated into case objects. Any keyword arguments
        supplied are directly overriden in the body of the request.
        """
        return _software_inventory(
            self._case,
            list(map(lambda agent: agent.target, self)),
            **kwargs
        )

    def remediate(self, **kwargs):
        """Runs a remediation task on the endpoint. Any keyword arguments
        supplied are directly overriden in the body of the request.
        """
        return _remediate(
            self._case,
            list(map(lambda agent: agent.target, self)),
            **kwargs
        )

    def collect(self, **kwargs):
        """Runs a collection task on the endpoint. Any keyword arguments
        supplied are directly overriden in the filter of the request.
        """
        return _collect_on_agent(
            self._case,
            list(map(lambda agent: agent.target, self)),
            **kwargs
        )

##

def _analyse_volatile(case, targets: list[str], **kwargs):
    caseid = case.get("id", 0)
    request_type, ext = agent_volatile_analysis_ext
    response = case.client.send_request(request_type,
        ext.format(caseid=caseid),
        json={
            "volatile": {
                "includeProcessTree": True,
                "processTreeOptions": {
                    "detectHiddenProcesses": False,
                    "includeDlls": True,
                    "dllOptions": {
                        "detectInjectedDlls": False
                    },
                    "includeSockets": True,
                    "includeHandles": True,
                    "includeJamScore": False,
                    "includeStaticAnalysis": False,
                    "mergeWithMemoryAnalysis": False
                },
                "includeServices": True,
                "includeJamServices": True,
                "includeDrivers": True,
                "includeJamDrivers": True,
                "includeUsers": True,
                "includeNICs": True,
                "includeSMBSessions": True,
                "includeArp": True,
                "includeRouting": True,
                "includeDNSCache": True,
                "includePrefetch": True,
                "includeVolume": True,
                "includeUsb": True,
                "includeLiveRegistry": False,
                "includeRegistryKeys": False,
                "includeTasks": True,
                "includeJamTasks": True,
                "includeCertificates": True
            } | kwargs,
            "ips": {
                "targets": targets
            }
        }
    )
    return Job(case, id=response.json())

def _acquire_disk(case, targets: list[str], **kwargs):
    caseid = case.get("id", 0)
    request_type, ext = agent_disk_acquisition_ext
    response = case.client.send_request(request_type,
        ext.format(caseid=caseid),
        json={
            "driveImage": {} | kwargs,
            "ips": {
                "targets": targets
            }
        }
    )
    return Job(case, id=response.json())

def _acquire_memory(case, targets: list[str], **kwargs):
    caseid = case.get("id", 0)
    request_type, ext = agent_memory_acquisition_ext
    response = case.client.send_request(request_type,
        ext.format(caseid=caseid),
        json={
            "memoryAcquistion": {},
            "ips": {
                "targets": targets
            }
        }
    )
    return Job(case, id=response.json())

def _software_inventory(case, targets: list[str]):
    caseid = case.get("id", 0)
    request_type, ext = agent_software_inventory_ext
    response = case.client.send_request(request_type,
        ext.format(caseid=caseid),
        json={
            "softwareInvJob": {},
            "ips": {
                "targets": targets
            }
        }
    )
    return Job(case, id=response.json())

def _remediate(case, targets: list[str], task: dict = {}):
    caseid = case.get("id", 0)
    request_type, ext = agent_remediation_ext
    response = case.client.send_request(request_type,
        ext.format(caseid=caseid),
        json={
            "agentRemediation": task,
            "ips": {
                "targets": targets
            }
        }
    )
    return Job(case, id=response.json())

def _collect_on_agent(case, targets: list[str], name: str, **kwargs):
    caseid = case.get("id", 0)
    request_type, ext = agent_collection_ext
    response = case.client.send_request(request_type,
        ext.format(caseid=caseid),
        json={
            "agentCollection": {
                "filter": kwargs,
                "baseName": name,
                "calculateSha1Hashes": True,
                "calculateMD5Hashes": True,
                "verifyAfterCreation": True,
            },
            "ips": {
                "targets": targets
            }
        }
    )
    return Job(case, id=response.json())