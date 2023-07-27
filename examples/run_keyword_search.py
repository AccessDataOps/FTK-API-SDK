from exterro.client import Client

client = Client("http://localhost:4443/", "api-key-guid")

attributes = client.attributes
cases = client.cases

object_name = attributes.first_matching_attribute("attributeUniqueName", "ObjectName")

case = cases.first_matching_attribute("name", "Test Case")

evidence = case.evidence

entry_iter = evidence.search_keyword(
	keywords=["guns"],
	attributes=[object_name]
)

print("The following entries contain the keyword \"guns\":")
for entry in entry_iter:
	print("\\t", entry[object_name.name])