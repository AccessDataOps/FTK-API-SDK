from accessdata.client import Client

client = Client("http://localhost:4443/", "api-key-guid")

cases = client.cases

case = cases.first_matching_attribute("name", "Test Case")

labels = case.labels

new_label = labels.create(name="Test Label", color="#00FFFFFF")