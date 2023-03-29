# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.1.1] - 2023-03-29

- Require the latest version of transitive dependency 'certifi'.
- Simplified and restructured the imports for the runzero sdk so that all type definitions come from the `runzero.types` module, all API managers come from the `runzero.api` module, and only named exceptions and the client come from the root `runzero` module.
- Improved the ergonomics of the `Tag`, `Hostname`, and `CustomAttributes` types.
- Removed the `asset_from_json` and `asset_from_csv` functions. In place of those functions, we are now providing an example of how to transform your data into an `ImportAsset` for uploading. This enables users to handle converting their own data much more accurately than an abstracted function ever could.


## [0.1.0] - 2023-03-24

Initial beta release

### Major features

- Authentication and connection
- Crud operations on sites, tasks, organizations, custom asset data sources
- Custom asset data transformation
- Uploadable custom assets

