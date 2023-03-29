import uuid

import runzero
from runzero.api import Sites

# API keys are required for using the runZero sdk. See https://www.runzero.com/docs/leveraging-the-api/
MY_CLIENT_ID = ""  # OAuth client id. See https://console.runzero.com/account/api/clients
MY_CLIENT_SECRET = ""  # OAuth client secret. See https://console.runzero.com/account/api/clients
MY_ORG_ID = uuid.UUID("")  # Account level API key. See https://console.runzero.com/account


def main():
    """
    A common task in the runZero platform is to clean up sites which are no longer necessary.

    The code below gives an example of how delete all sites within an Org that have a certain prefix in the site name.
    """

    # create the runzero client
    c = runzero.Client()

    # log in using OAuth credentials
    c.oauth_login(MY_CLIENT_ID, MY_CLIENT_SECRET)
    print("login successful")

    # create the site api manager using the client to read and write sites
    site_manager = Sites(client=c)

    # retrieve all sites in your org
    sites = site_manager.get_all(MY_ORG_ID)
    print(f"retrieved data for {len(sites)} sites in org")

    # iterate over each of your sites in your org
    for site in sites:
        if site.name.startswith("Custom"):
            # use the api manager to delete the sites if the site name started with the "Custom" prefix
            site_manager.delete(MY_ORG_ID, site.id)
            print(f"deleted site: {site.name}")


if __name__ == "__main__":
    main()
