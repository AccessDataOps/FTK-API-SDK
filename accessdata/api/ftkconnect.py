from .extensions import trigger_workflow_ext

class FTKConnect():

    """
    A class that trigger the job using api call.

    :param client: The client to send the request too.
	:type client: :class: ~`accessdata.client.Client`

    """
    def __init__(self,client):
        self.client = client

    def parse_args(self,**args):

        """
        Creates workflow parameters required to be passed in api call from
        args received.

        return : workflowid and the workflow parameters 
        
        """
        workflow_details={}

        workflow_id = args["workflowid"]
        # Process in existing case ids
        if "caseids" in args:
            workflow_details["createCase"]={"CaseIds":args['caseids'].split(",") }
        # Process in new case
        elif "caseids" not in args and "casename" in args:
            workflow_details={ "createCase": {"CaseName":args['casename']}}
        # Raise runtime exception neither caseid nor casename is received.
        # elif 'caseids'not in args and 'casename' not in args:
        #     raise ValueError("Both caseid and casename are empty")

        if 'evidencepath'in args:
            workflow_details['AddEvidence']={'EvidencePath':args['evidencepath']}
        if 'searchandtagpath' in args:
            workflow_details['SearchAndTag']={"FileLocations":args['searchandtagpath']}
        if 'exportpath' in args:
            workflow_details['Export']={"ExportPath":args['exportpath']}
        if 'targetips' in args:
            agent_ips  = [ip.strip() for ip in args['targetips'].split(",")]
            workflow_details['Collection']={"targetips":agent_ips}

        return workflow_id, workflow_details

    def trigger(self,**args):

        """
        Triggers the workflow api call .
        
		:return: Status of the call invoke and the response of request
		:rtype: :dict

        """
        workflow_id, workflow_params = self.parse_args(**args)
        request_type, ext = trigger_workflow_ext
        ext = ext.format(workflowid=workflow_id)
        response = self.client.send_request(request_type, ext, json=workflow_params)
        status_flag = response.json()
        result = {"Status":"true",
                  "Result": status_flag
                 }
        return result