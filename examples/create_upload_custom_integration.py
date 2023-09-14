import time
import uuid

import runzero
from runzero.api import CustomAssets, CustomIntegrationsAdmin, Sites, Tasks
from runzero.types import ImportAsset, ImportTask

# API keys are required for using the runZero sdk. See https://www.runzero.com/docs/leveraging-the-api/
MY_CLIENT_ID = ""  # OAuth client id. See https://console.runzero.com/account/api/clients
MY_CLIENT_SECRET = ""  # OAuth client secret. See https://console.runzero.com/account/api/clients
MY_ORG_ID = uuid.UUID("")  # runZero organization ID. See https://console.runzero.com/organizations
WANTED_SITE_NAME = ""  # Name of site within the above Organization. See https://console.runzero.com/sites


def build_example_assets():
    """
    This just creates bare minimum data for example purposes
    """
    return [ImportAsset(id="sample-1"), ImportAsset(id="sample-2")]


def main():
    """
    The code below gives an example of how to create a custom integration and upload assets to a site using the new custom
    source.
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

    # create the site api manager to get our site information
    site_mgr = Sites(c)
    site = site_mgr.get(MY_ORG_ID, WANTED_SITE_NAME)
    if not site:
        print(f"unable to find requested site")
        return
    print(f"got information for site {site.name}")

    # create the custom integration api manager and create a new custom integration
    custom_integration_mgr = CustomIntegrationsAdmin(c)
    my_asset_source = custom_integration_mgr.create(name="my-custom-source2")
    print(f"created custom integration: {my_asset_source.id}")

    # creates some example assets
    assets = build_example_assets()

    # create our named import task with 'exclude unknown' set to true
    task_options = ImportTask(name="my sdk task", exclude_unknown=True)

    # create the import api manager to upload custom assets
    import_mgr = CustomAssets(c)
    import_task = import_mgr.upload_assets(MY_ORG_ID, site.id, my_asset_source.id, assets, task_info=task_options)
    print(f"created an custom asset import task: {import_task.name}")

    # create a task api manager, so we can monitor our custom asset import task
    task_mgr = Tasks(client=c)
    status = task_mgr.get_status(MY_ORG_ID, import_task.id)

    # keep polling until the task is completed or failed or 30 seconds have elapsed
    iters = 0
    while status not in ("processed", "failed", "error") and iters < 6:
        print("polling on status for custom integration upload task....")
        time.sleep(5)
        iters += 1
        status = task_mgr.get_status(MY_ORG_ID, import_task.id)
        print(f"task status is {status}")

    # check that our task successfully completed
    assert status == "processed"
    print("success! custom assets are uploaded and available in the asset inventory")

    # gather statistics from the completed task
    task_data = task_mgr.get(MY_ORG_ID, task_id=import_task.id)
    new_assets = task_data.stats.get("change.newAssets")
    changed_assets = task_data.stats.get("change.changedAssets")
    total_assets = task_data.stats.get("change.totalAssets")

    print(f"new assets: {new_assets}, changed assets: {changed_assets}, total assets: {total_assets}")


if __name__ == "__main__":
    main()
