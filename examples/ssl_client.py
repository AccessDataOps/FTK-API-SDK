from accessdata.client import Client

## Only required if anon auth is disallowed.
client = Client("https://localhost:4443/", None, validate=False)
client.session.cert = "/path/to/cert"

print(client.cases)