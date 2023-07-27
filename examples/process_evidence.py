from exterro.api.evidence import EvidenceType
from exterro.api.jobs import JobState
from exterro.client import Client

from time import sleep

client = Client("http://localhost:4443/", "api-key-guid")

new_case = client.cases.create(name="New Case")
jobs = new_case.evidence.process(
	"/path/to/evidence",
	EvidenceType.IMAGE_FILE,
	completeprocessingoptions="<insert xml>"
)

job = jobs[0]
while job.state in (JobState.Submitted, JobState.InProgress):
	print("Evidence Job: ", str(job.state))
	sleep(5)
	job.update()

print("Evidence Job: ", str(job.state))