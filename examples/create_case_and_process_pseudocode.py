from exterro.api.evidence import EvidenceType
from exterro.api.jobs import JobState
from exterro.client import Client

client = Client("http://localhost:4443", "api-key-guid")

processingprofiles = [
	"",
	"",
	""
]

new_case = client.cases.create(name="Test Case")
jobs = new_case.evidence.process(
	"/path/to/evidence",
	EvidenceType.IMAGE_FILE,
	completeprocessingoptions=processingprofiles[2]
)

job = jobs[0]
while job.state in (JobState.Submitted, JobState.InProgress):
	sleep(5)
	print("Job in State:", job.state)
	job.update()

## continue as required upon job finish