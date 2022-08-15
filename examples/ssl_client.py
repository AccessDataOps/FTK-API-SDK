from accessdata.client import Client

client = Client("https://<subjectname>/", verify="/path/to/ca-cert.cer")

print(client.cases)