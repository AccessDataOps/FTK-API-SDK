from accessdata.client import Client
from accessdata.utilities import HttpNegotiateAuth

client = Client("http://localhost:4443/", auth=HttpNegotiateAuth())

print(client.cases)