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
MY_ASSET_ID = "custom-asset-1"  # The "foreign ID" for the newly-created asset.


def main():
    """
    The code below gives an example of how to create a new asset in a custom integration.
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
    asset_id = my_integration.create_asset(
        MY_ORG_ID,
        MY_SITE_ID,
        ImportAsset(
            id=MY_ASSET_ID,
            hostnames=["example-hostname-1", "example-hostname-2"],
            domain="example.com",
            first_seen_ts=datetime.datetime.now(),
            os="Linux",
            os_version="3.11",
            manufacturer="Linux",
            model="Super Server",
            tags=[Tag("tag1=value1")],
            device_type="Server",
            custom_attributes={
                "custom.attr1": "custom.value1",
                "ipAddresses": "192.168.86.1\t10.10.10.1",
                "ipAddressesExtra": "10.10.10.4",
            },
        ),
    )
    print(f"created asset {asset_id}")


if __name__ == "__main__":
    main()
