from exterro.client import Client

client = Client("http://localhost:4443/", "api-key-guid")

attributes = client.attributes

object_name = attributes.first_matching_attribute(
	"attributeUniqueName",
	"ObjectName"
)
print(object_name == "Test")
print(object_name.startswith("S"))