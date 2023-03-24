import time
import uuid

import runzero
from runzero.client import AuthError
from runzero.types import NewAssetCustomSource

# API keys are required for using the runZero sdk. See https://www.runzero.com/docs/leveraging-the-api/
MY_CLIENT_ID = ""  # OAuth client id. See https://console.runzero.com/account/api/clients
MY_CLIENT_SECRET = ""  # OAuth client secret. See https://console.runzero.com/account/api/clients
MY_ORG_ID = uuid.UUID("")  # runZero organization ID. See https://console.runzero.com/organizations
WANTED_SITE_NAME = ""  # Name of site within the above Organization. See https://console.runzero.com/sites
MY_CSV = "/path/to/assets.csv"  # Path to a CSV with assets you want to upload


def main():
    """
    The code below gives an example of how to create a custom source and upload valid assets from a CSV to a site using
    the new custom source.
    """
    # create the runzero client
    c = runzero.Client()

    # try to log in using OAuth credentials
    try:
        c.oauth_login(MY_CLIENT_ID, MY_CLIENT_SECRET)
    except AuthError as e:
        print(f"login failed: {e}")
        return
    print("login successful")

    # create the site manager to get our site information
    site_mgr = runzero.Sites(c)
    site = site_mgr.get(MY_ORG_ID, WANTED_SITE_NAME)
    if not site:
        print(f"unable to find requested site")
        return
    print(f"got information for site {site.name}")

    # create the custom source manager and create a new custom source
    custom_source_mgr = runzero.CustomSourcesAdmin(c)
    my_asset_source = custom_source_mgr.create(name="my-custom-source2")
    print(f"created custom source: {my_asset_source.id}")

    # load some assets from our csv
    assets = runzero.assets_from_csv(MY_CSV)
    print(f"loaded {len(assets)} assets from csv")

    # create the import manager to upload custom assets
    import_mgr = runzero.CustomAssets(c)
    import_task = import_mgr.upload_assets(MY_ORG_ID, site.id, my_asset_source.id, assets)
    print(f"created an custom asset import task: {import_task.name}")

    # create a task manager, so we can monitor our custom asset import task
    task_mgr = runzero.Tasks(client=c)
    status = task_mgr.get_status(MY_ORG_ID, import_task.id)

    # keep polling until the task is completed or failed or 30 seconds have elapsed
    iters = 0
    while status not in ("processed", "failed", "error") and iters < 6:
        print("polling on status for custom source upload task....")
        time.sleep(5)
        iters += 1
        status = task_mgr.get_status(MY_ORG_ID, import_task.id)
        print(f"task status is {status}")

    # check that our task successfully completed
    assert status == "processed"
    print("success! custom assets are uploaded and available in the asset inventory")


if __name__ == "__main__":
    main()
