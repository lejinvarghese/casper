# import tensorflow as tf

# print(tf.sysconfig.get_build_info())

# print(tf.config.list_physical_devices("GPU"))

from google.cloud import secretmanager
project_id = "projects"
secret_id = "COMET_API_KEY"
client = secretmanager.SecretManagerServiceClient()

response = client.access_secret_version(request={"name": secret_id})

# Print the secret payload.
#
# WARNING: Do not print the secret in a production environment - this
# snippet is showing how to access the secret material.
payload = response.payload.data.decode("UTF-8")
print("Plaintext: {}".format(payload))