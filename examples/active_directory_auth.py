from accessdata.client import Client
from accessdata.utilities import HttpNegotiateAuth

client = Client("http://localhost:4443/", None, validate=False)
client.session.auth = HttpNegotiateAuth()

print(client.cases)