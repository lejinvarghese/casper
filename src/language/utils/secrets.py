from google.cloud.secretmanager import SecretManagerServiceClient

PROJECT_ID = "projects-264723"


def get_secret(secret_id: str, project_id: str = None, version: str = "latest"):
    """
    Access a secret stored in Google Secret Manager
    """
    if not project_id:
        from os import getenv

        from dotenv import load_dotenv

        load_dotenv()
        return getenv(secret_id)
    else:
        try:
            client = SecretManagerServiceClient()
            name = client.secret_version_path(project_id, secret_id, version)
            response = client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            raise e
