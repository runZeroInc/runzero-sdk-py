import datetime
import time
import uuid

import runzero
from runzero.api import CustomIntegrationsAdmin
from runzero.types import ImportAsset, Tag

# API keys are required for using the runZero sdk. See https://www.runzero.com/docs/leveraging-the-api/
MY_CLIENT_ID = ""  # OAuth client id. See https://console.runzero.com/account/api/clients
MY_CLIENT_SECRET = ""  # OAuth client secret. See https://console.runzero.com/account/api/clients
MY_ORG_ID = uuid.UUID("")  # runZero organization ID. See https://console.runzero.com/organizations
MY_SITE_ID = uuid.UUID("")  # runZero site ID. See https://console.runzero.com/sites
MY_INTEGRATION_ID = uuid.UUID("")  # ID of the custom integration to use.
MY_ASSET_ID = uuid.UUID("")  # the runZero ID of the asset to update.


def main():
    """
    The code below gives an example of how to update asset attributes.
    """

    # create the runzero client
    c = runzero.Client()

    # try to log in using OAuth credentials
    try:
        c.oauth_login(MY_CLIENT_ID, MY_CLIENT_SECRET)
    except runzero.AuthError as e:
        print(f"login failed: {e}")
        return
    print("login successful")

    integrations = CustomIntegrationsAdmin(client=c)
    my_integration = integrations.get_asset_admin_handle(MY_INTEGRATION_ID)
    count = my_integration.update_custom_attributes(
        MY_ORG_ID,
        site=MY_SITE_ID,
        asset_id=MY_ASSET_ID,
        attributes={
            "machineCheck": "super-server",
            "attributeToDelete": "",
        },
    )
    print(f"updated {count} asset(s)")


if __name__ == "__main__":
    main()
