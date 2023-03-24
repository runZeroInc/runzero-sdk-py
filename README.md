# runZero Python SDK
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/runzero-sdk)
[![PyPI](https://img.shields.io/pypi/v/runzero-sdk)](https://pypi.org/project/runzero-sdk/)
[![License](https://img.shields.io/badge/License-BSD_2--Clause-lightgrey.svg)](https://opensource.org/license/bsd-2-clause/)

This project is currently in beta and subject to change.


## Overview

This is a Python API client for [runZero](https://www.runzero.com/) - a product that provides asset discovery and
network visibility to help you build and maintain a comprehensive inventory of your cyber assets. runZero customers can use this project to interact with their environment using runZero and Python.

Note: the APIs used with this client are only availble to customers of the [Professional and Enterprise editions](https://www.runzero.com/product/pricing/) of runZero.

This project seeks to do only what is necessary to make interactions with runZero in your own Python code feel more
like any other local, Pythonic API. It uses code generated from the runZero
[API](https://github.com/runZeroInc/runzero-api), lightly wraps parts of it, and makes Python objects and functions
discoverable, consistent, and easy to use. We want you to concentrate on working with runZero, not HTTP.


## Installation

This project is [published to PyPI](https://pypi.org) and can be installed using your local Python package manager.

```commandline
pip install runzero-sdk
```

## Usage

There are several examples of using the SDK for common tasks under the `/examples` directory in the repo.

General usage of the SDK involves creating a `runzero.Client()` for handling authentication, then passing that `Client`
to resource managers, such as the `runzero.CustomAssets()`, `runzero.Sites()`, `runzero.OrgsAdmin()`, and more.

A typical code flow would look like the following:

```python
import runzero

client = runzero.Client()
client.oauth_login(MY_CLIENT_ID, MY_CLIENT_SECRET)

orgs = runzero.OrgsAdmin(client=client).get_all()
print(f"retrieved {len(orgs)} from our runZero account")
```

## Custom Import Asset field mappings

The following fields are available to be set for custom source asset imports. Any field which matches the below field
names, either directly or via remapping, will be inserted into the corresponding `ImportAsset` field and validated to
ensure it meets the outlined constraints.

Any field which does not match the fields below will be placed under the `custom_attributes` field. Please see the
`ImportAsset` schema definition for more details: #/components/schemas/ImportAsset

* `id` - this `str` field is ***required*** to be set for all custom source assets and is the unique identifier for the asset. If your asset does not have a unique id then we recommend you create one using `uuid.uuid4()`.
* `network_interfaces` - this field is an array of objects representing the network interfaces of the asset. Please see the API Schema for details. #/components/schemas/ImportAsset/properties/networkInterfaces.
* `hostnames` - a `List[str]` field of all the hostnames associated with the asset. Each hostname has a maximum length of 260 characters and the `list` has a maximum of 100 hostnames.
* `domain` - a `str` field representing the domain associated with the asset. Maximum length of 260 characters.
* `first_seen_ts` - a `datetime.datetime` field representing the first time an asset was seen.
* `last_seen_ts` - a `datetime.datetime` field representing the last time an asset was seen.
* `os` - a `str` field which describes the operating system on the asset. Maximum length of 1024 characters.
* `os_version` - a `str` field which describes the version of the operating system running on the asset. Maximum length of 1024 characters.
* `manufacturer` - a `str` field which declares the manufacturer of the asset. Maximum length of 1024 characters.
* `model` - a `str` field which describes the manufacturers model of the asset. Maximum length of 1024 characters.
* `tags` - a `List[str]` field for all the tags to be associated with the asset in the runZero platform. Maximum of 100 tags and each tag has a maximum length of 1024 characters.
* `device_type` - a `str` field declaring the device type of the asset. Maximum length of 1024 characters.

## Feature requests and bug reports

To report a bug or request a new feature in the SDK, please open a support request using the in-product link. This will let us deduplicate and prioritize requests in parallel to already planned enhancements.

When preparing to report a bug, please try to determine whether it's related to the SDK or the runZero product itself. For improvements to or issues with the SDK, please include as much detail as possible about the problem you're looking to solve. For improvements to or issues with the runZero platform, please explore our [documentation](https://www.runzero.com/docs/) to see if there's related guidance or to verify that something isn't working as intended before opening a support request.


## Contributing a bug fix or feature

We look forward to being able to accept contributions from the community! However, until the project is stable enough, we'd rather you open an issue and have a discussion with the maintainers. Since we're actively working on this project, the fix may be forthcoming, or the area being improved may have a lot of change planned.


## Related Projects and Resources

This project does not currently support the full runZero API. The broader runZero API
[documentation](https://www.runzero.com/docs/leveraging-the-api/) includes both human- and machine-generated
API documentation.

runZero's OpenAPI [spec](https://github.com/runZeroInc/runzero-api) is updated as the platform is expanded. The
information published there can help you generate code if you have a need to use parts of the API not covered
in this project.
