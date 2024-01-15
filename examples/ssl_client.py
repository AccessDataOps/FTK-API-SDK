from exterro.client import Client

client = Client("https://<subjectname>/", verify="/path/to/ca-cert.cer", ciphers="RSA+AES:RSA+AESGCM")

print(client.cases)