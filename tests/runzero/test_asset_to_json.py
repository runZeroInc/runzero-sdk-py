import json

import pytest

from runzero.types import ImportAsset


def test_asset_to_json_direct():
    asset = ImportAsset(id="foo123", os="Debian", osVersion="123.456")

    result = asset.json(by_alias=True)
    result_dict = json.loads(result)

    assert result_dict["id"] == "foo123"
    assert result_dict["os"] == "Debian"
    assert result_dict["osVersion"] == "123.456"
    with pytest.raises(KeyError):
        _ = result_dict["os_version"]
