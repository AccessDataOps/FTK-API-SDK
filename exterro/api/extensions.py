## /api/extensions.py

"""
Maintains the API endpoint URI extensions.
"""

## Declaring __all__

__all__ = (
	"status_check_ext",
	"site_server_status_check_ext",
	"case_create_ext",
	"case_list_ext",
	"case_create_portable_ext",
	"evidence_list_ext",
	"evidence_processed_list_ext",
	"evidence_process_ext",
	"object_page_list_ext",
	"label_create_ext"
	"label_list_ext"
	"label_objects_job_ext"
	"label_objects_list_ext"
	"label_objects_count_ext"
	"label_objects_sync_ext"
	"search_report_ext",
	"export_natives_ext",
	"agent_push_ext",
	"agent_collection_ext",
	"agent_disk_acquisition_ext",
	"agent_memory_acquisition_ext",
	"agent_remediation_ext",
	"agent_software_inventory_ext",
	"agent_volatile_analysis_ext",
	"agent_volatile_import_ext",
	"job_status_ext",
	"attribute_list_ext",
	"attribute_list_by_case_ext",
	"child_file_categories_ext",
	"processing_case_ext",
	"server_setting_ext",
	"yara_ioc_rule_import_ext",
)

## Predefined Constants

DELETE = "delete"
GET = "get"
PATCH = "patch"
POST = "post"
PUT = "put"

## Status Extensions

base_ext 						= "api/v2/enterpriseapi"
status_check_ext				= GET, base_ext + "/statuscheck"
site_server_status_check_ext 	= GET, base_ext + "/agent/getsiteserverstatus"

## Case Management Extensions

case_create_ext					= POST, base_ext + "/core/createcase"
case_list_ext					= GET, base_ext + "/core/getcaselist"
case_create_portable_ext		= POST, base_ext + "/core/{caseid}/createportablecase"

## Evidence Management Extensions

evidence_list_ext				= GET, base_ext + "/core/{caseid}/getevidencelist"
evidence_processed_list_ext		= GET, base_ext + "/core/{caseid}/getprocessedevidencelist"
evidence_process_ext 			= POST, base_ext + "/core/{caseid}/processdata"

## Object Management Extensions

object_page_list_ext			= POST, base_ext + "/core/{caseid}/getobjectlist/{pagenumber}/{pagesize}"

## Label Management Extensions

label_create_ext				= POST, base_ext + "/core/{caseid}/createlabel"
label_list_ext					= GET, base_ext + "/core/{caseid}/getlabellist"
label_objects_job_ext			= POST, base_ext + "/jobs/{caseid}/labelobjects"
label_objects_list_ext			= GET, base_ext + "/core/cases/{caseid}/label/{labelid}/evidenceobjects"
label_objects_count_ext			= GET, base_ext + "/core/cases/{caseid}/label/{labelid}/objectscount"
label_objects_sync_ext			= POST, base_ext + "/{caseid}/labelobjectssync"

## Search Extensions

search_report_ext				= POST, base_ext + "/jobs/{caseid}/createsearchcountreport"

## Export Extenstions

export_natives_ext				= POST, base_ext + "/jobs/{caseid}/dumpnativeobjects"

## Agent Management Extensions

agent_push_ext					= POST, base_ext + "/agent/{caseid}/runagentpush"
agent_collection_ext			= POST, base_ext + "/agent/{caseid}/agentcollectionjob"
agent_disk_acquisition_ext		= POST, base_ext + "/agent/{caseid}/diskacquistion"
agent_memory_acquisition_ext	= POST, base_ext + "/agent/{caseid}/memoryacquistion"
agent_remediation_ext			= POST, base_ext + "/agent/{caseid}/remediate"
agent_software_inventory_ext	= POST, base_ext + "/agent/{caseid}/softwareinventory"
agent_volatile_analysis_ext		= POST, base_ext + "/agent/{caseid}/volatile"
agent_volatile_import_ext		= GET, base_ext + "/agent/{caseid}/importvolatile/{jobid}"

## Generic Job Extensions

job_status_ext					= GET, base_ext + "/core/{caseid}/getjobstatus/{jobid}"

## Utility Extensions

attribute_list_ext				= GET, base_ext + "/core/getallattributes"
attribute_list_by_case_ext		= GET, base_ext + "/core/{caseid}/getallattributesbycaseid"
child_file_categories_ext		= GET, base_ext + "/core/getchildrenfilecategories"
processing_case_ext				= GET, base_ext + "/processingcaseid"
server_setting_ext				= GET, base_ext + "/core/getserversetting/{setting}"
yara_ioc_rule_import_ext		= POST, base_ext + "/agent/importiocandyara"