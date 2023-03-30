import uuid

import runzero
from runzero.api import CustomSources, CustomSourcesAdmin

# API keys are required for using the runZero sdk. See https://www.runzero.com/docs/leveraging-the-api/
MY_CLIENT_ID = ""  # OAuth client id. See https://console.runzero.com/account/api/clients
MY_CLIENT_SECRET = ""  # OAuth client secret. See https://console.runzero.com/account/api/clients
MY_ORG_ID = uuid.UUID("")  # Account level API key. See https://console.runzero.com/account


def main():
    """
    With the release of this SDK - there is certain to be a lot of experimentation with the new Custom Sources feature.

    The code below gives an example of how to delete all custom sources from an account. This will also remove any
    assets which are tied to the custom source.
    """

    # create the runzero client
    c = runzero.Client()

    # log in using OAuth credentials
    c.oauth_login(MY_CLIENT_ID, MY_CLIENT_SECRET)
    print("login successful")

    # create the custom source api manager using the client for reading custom sources
    source_manager = CustomSources(client=c)

    # create the admin custom sources api manager using the client for reading and writing custom sources
    admin_manager = CustomSourcesAdmin(client=c)

    # retrieve all sources using the source api manager
    custom_sources = source_manager.get_all(MY_ORG_ID)
    print(f"found {len(custom_sources)} in org")

    # iterate over each custom source
    for source in custom_sources:
        # delete those custom sources using the admin api manager
        admin_manager.delete(source.id)
        print(f"Deleted custom source: {source.name}")


if __name__ == "__main__":
    main()
