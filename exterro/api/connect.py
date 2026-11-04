## /api/connect.py

"""
Playbook controller for FTK Connect enabling triggering of
    these Playbooks from the SDK.
"""

from typing import Any, Union

from .extensions import (trigger_workflow_ext, )
from ..logging import logger

## Declaring __all__

__all__ = ("Connect", "Playbook", )

##

class Playbook:
    """
    A class that maintains Playbook information.

    :param connect: The Connect object which stores all Playbooks.
    :type connect: :class: ~`exterro.api.connect.Connect`
    """

    def __init__(self, plid: int, connect):
        self.id = plid
        self.connect = connect

    def __repr__(self):
        id = self.get('id', 0)
        return f"Playbook<{id=}>"

    def execute(self,
        casedetails: Union[dict, None],
        evidencedetails: Union[dict, None],
        searchdetails: Union[dict, None],
        exportdetails: Union[dict, None],
        collectiondetails: Union[dict, None]
    ):
        """
        Executes the Playbook with the provided details.

        :param casedetails: The dict of details about the case for the playbook.
            Formatted as a dictionary with a key named 'casename' or 'caseids'.
        :type casedetails: dict 

        :param evidencedetails: The dict of details about the evidence path for
            the playbook. Formatted as a dictionary with a single key named
            'evidencepath'.
        :type evidencedetails: dict 

        :param searchdetails: The dict of details about the search keywords for
            the playbook. Formatted as a dictionary with single key named
            'folderlocation' whose value is a path to the keyword TXT file.
        :type searchdetails: dict 

        :param exportdetails: The dict of details about the export path(s) for
            the playbook. Formatted as a dictionary with a single key named
            'exportpath'.
        :type exportdetails: dict 

        :param collectiondetails: The dict of details about the target IPs or
            FQDNs for the playbook. Formatted as a dictionary with a single key
            named 'targetips' whose value is a list of the addresses.
        :type collectiondetails: dict 
        """
        params = {
            "createcase": casedetails,
            "addevidence": evidencedetails,
            "searchandtag": searchdetails,
            "export": exportdetails,
            "collection": collectiondetails
        }
        request_type, ext = trigger_workflow_ext

        response = self.client.send_request(request_type,
            ext.format(workflowid=self.id), json=params)

        return response.json()
    
    def update(self):
        """
        Updates the current stored playbook information by querying FTK.
        """
        raise NotImplementedError(
            "Connect Playbook listing not currently supported."
        )

class Connect:
    """
    A class that triggers the job using API endpoint.

    :param client: The client to send the request too.
    :type client: :class: ~`exterro.client.Client`

    """
    
    def __init__(self, client, update: bool=True):
        self.client = client
        self.playbooks = list()

    def update(self):
        """
        Updates the current stored list of playbooks by querying FTK.
        """
        for playbook in self.playbooks:
            playbook.update()