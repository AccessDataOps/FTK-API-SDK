from exterro.client import Client
from exterro.utilities import HttpNegotiateAuth

client = Client("http://localhost:4443/", auth=HttpNegotiateAuth())

print(client.cases)