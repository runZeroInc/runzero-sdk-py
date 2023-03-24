import runzero


def main():
    """
    This SDK provides tooling to convert JSON from another external API, however there are some gotchas around mapping
    the fields from one source and getting it to conform to an ImportAsset.

    The below code provides a very simple example to convert JSON from one format into an ImportAsset
    """
    data_from_other_api = """\
[{"asset_id": "someId1", "asset_domain": "some.domain.com", "other_attribute": "small", "type": "Tablet"},\
{"asset_id": "someId2", "asset_domain": "other.domain.com", "other_attribute": "medium", "type": "Desktop"},\
{"asset_id": "someId3", "asset_domain": "another.domain.com", "other_attribute": "large", "type": "Server"}]\
"""

    # Given the data above from some other API - what if we wanted to map the "asset_id" to a runZero "id", the "type"
    #   to a runZero "device type", and the "asset_domain" to a runzero "domain"?
    #   To do this, we can use a dict to map the runZero ImportAsset fields to the fields from the other API.

    # If we tried to convert this data right now, we're going to have validation errors like below.
    try:
        runzero.assets_from_json(data_from_other_api)
    except runzero.ValidationError:
        print("sorry, couldn't convert data automatically")

    # Below we will define this mapping in the format of dict{runZero field: other api field}. Notice that we did not
    #   map the "other_attribute" field. This will get passed forward to runZero as a custom source specific attribute.
    mapping = {"id": "asset_id", "domain": "asset_domain", "device_type": "type"}

    assets = runzero.assets_from_json(data_from_other_api, mapper=mapping)
    print(f"created {len(assets)} ImportAssets from our API data")

    # here we iterate over the assets and confirm that the values were parsed correctly
    for asset in assets:
        print(f"id: {asset.id}")
        print(f"domain: {asset.domain}")
        print(f"device type: {asset.device_type}")
        print(f"additional attributes: {asset.custom_attributes}")


if __name__ == "__main__":
    main()
