from google.cloud.secretmanager import SecretManagerServiceClient

PROJECT_ID = "projects-264723"


def get_secret(
    secret_id: str, project_id: str = PROJECT_ID, version: str = "latest"
):
    """
    Access a secret stored in Google Secret Manager
    """

    client = SecretManagerServiceClient()
    name = client.secret_version_path(project_id, secret_id, version)
    response = client.access_secret_version(request={"name": name})
    payload = response.payload.data.decode("UTF-8")

    return payload
