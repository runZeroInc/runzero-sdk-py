import uuid

import runzero
from runzero.api import CustomIntegrations, CustomIntegrationsAdmin

# API keys are required for using the runZero sdk. See https://www.runzero.com/docs/leveraging-the-api/
MY_CLIENT_ID = ""  # OAuth client id. See https://console.runzero.com/account/api/clients
MY_CLIENT_SECRET = ""  # OAuth client secret. See https://console.runzero.com/account/api/clients
MY_ORG_ID = uuid.UUID("")  # Account level API key. See https://console.runzero.com/account


def main():
    """
    With the release of this SDK - there is certain to be a lot of experimentation with the new custom integrations feature.

    The code below gives an example of how to delete all custom integrations from an account. This will also remove any
    assets which are tied to the custom integration.
    """

    # create the runzero client
    c = runzero.Client()

    # log in using OAuth credentials
    c.oauth_login(MY_CLIENT_ID, MY_CLIENT_SECRET)
    print("login successful")

    # create the custom integration api manager using the client for reading custom integrations
    source_manager = CustomIntegrations(client=c)

    # create the admin custom integrations api manager using the client for reading and writing custom integrations
    admin_manager = CustomIntegrationsAdmin(client=c)

    # retrieve all integrations using the source api manager
    custom_integrations = source_manager.get_all(MY_ORG_ID)
    print(f"found {len(custom_integrations)} in org")

    # iterate over each custom integration
    for source in custom_integrations:
        # delete those custom integrations using the admin api manager
        admin_manager.delete(source.id)
        print(f"Deleted custom integration: {source.name}")


if __name__ == "__main__":
    main()
