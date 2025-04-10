# Changelog

All notable changes to this project will be documented in this file.

## [1.0.12](https://github.com/roihuvaara/greeclimate/compare/r1.0.11...r1.0.12) (2025-04-07)


### Bug Fixes

* Simplify property getter ([71b0351](https://github.com/roihuvaara/greeclimate/commit/71b03516e347537a5f877a30590d6d9b961a59fe))

## [1.0.11](https://github.com/roihuvaara/greeclimate/compare/r1.0.10...r1.0.11) (2025-04-07)


### Bug Fixes

* Update response handling ([58ae188](https://github.com/roihuvaara/greeclimate/commit/58ae1886318f616cbb068164b60536934f0ca81c))

## [1.0.10](https://github.com/roihuvaara/greeclimate/compare/r1.0.9...r1.0.10) (2025-04-07)


### Bug Fixes

* Change the property getter ([d18bd3b](https://github.com/roihuvaara/greeclimate/commit/d18bd3ba3c165638075a42b12068dfbc273e6843))

## [1.0.9](https://github.com/roihuvaara/greeclimate/compare/r1.0.8...r1.0.9) (2025-04-07)


### Bug Fixes

* Change state update ([41c03ec](https://github.com/roihuvaara/greeclimate/commit/41c03ec83973027321e6f19c0d1b358c99f18436))

## [1.0.8](https://github.com/roihuvaara/greeclimate/compare/r1.0.7...r1.0.8) (2025-03-27)


### Bug Fixes

* Add debug logging ([255fdf1](https://github.com/roihuvaara/greeclimate/commit/255fdf1c5db443d9b66da4aa44016fe2a1f8d77e))

## [1.0.7](https://github.com/roihuvaara/greeclimate/compare/r1.0.6...r1.0.7) (2025-03-27)


### Bug Fixes

* Wait for batch ([fe37024](https://github.com/roihuvaara/greeclimate/commit/fe37024149fb24449c14963a7a3964ff35c04f8f))

## [1.0.6](https://github.com/roihuvaara/greeclimate/compare/r1.0.5...r1.0.6) (2025-03-27)


### Bug Fixes

* Set drained when receiving response ([cf142c0](https://github.com/roihuvaara/greeclimate/commit/cf142c0c6bfaba66a91fea6763d67544692d8a12))

## [1.0.5](https://github.com/roihuvaara/greeclimate/compare/r1.0.4...r1.0.5) (2025-03-25)


### Bug Fixes

* Remove strict=False parameter from zip() calls to fix Python 3.13 compatibility ([03dfdb0](https://github.com/roihuvaara/greeclimate/commit/03dfdb0d55a1703cfd9665035b4b3a91753d3890))

## [1.0.4](https://github.com/roihuvaara/greeclimate/compare/r1.0.3...r1.0.4) (2025-03-24)


### Bug Fixes

* Fix binding timeout and properties retrieval ([c023a5b](https://github.com/roihuvaara/greeclimate/commit/c023a5b8f1d052d7cd0f7126894782db145779a7))

## [1.0.3](https://github.com/roihuvaara/greeclimate/compare/r1.0.2...r1.0.3) (2025-03-24)


### Bug Fixes

* Data fetching ([3eb470e](https://github.com/roihuvaara/greeclimate/commit/3eb470ef12d458fdbc32f9dbd9a43c638fb4d639))

## [1.0.2](https://github.com/roihuvaara/greeclimate/compare/r1.0.1...r1.0.2) (2025-03-24)


### Bug Fixes

* Binding ([64b01e5](https://github.com/roihuvaara/greeclimate/commit/64b01e5b2082216419c2b3ca1d979b2bf0d998f9))

## [1.0.1](https://github.com/roihuvaara/greeclimate/compare/r1.0.0...r1.0.1) (2025-03-20)


### Bug Fixes

* Add missing getters and tests with formatting ([dd4adbf](https://github.com/roihuvaara/greeclimate/commit/dd4adbf46f6d03d0000883f7dbfaf91397b208f9))
* Automatically update python package version ([454e979](https://github.com/roihuvaara/greeclimate/commit/454e9790d701b461d12c2b62ce251ec02550821b))

## 1.0.0 (2023-03-17)

Initial stable release of gree_versati with the following features:
- Support for Gree Versati series heat pumps
- Device discovery and communication
- Device control and monitoring capabilities

# [2.1.0](https://github.com/cmroche/greeclimate/compare/v2.0.0...v2.1.0) (2024-08-05)


### Features

* Support GCM encryption for Gree devices ([#92](https://github.com/cmroche/greeclimate/issues/92)) ([7122cdd](https://github.com/cmroche/greeclimate/commit/7122cdd82597af82109a17bc32dcbfb97c78073c))

# [2.0.0](https://github.com/cmroche/greeclimate/compare/v1.4.6...v2.0.0) (2024-07-02)


### Features

* Full async networking ([#90](https://github.com/cmroche/greeclimate/issues/90)) ([4587984](https://github.com/cmroche/greeclimate/commit/4587984df8d01a1bc7a0b20f01590f455e361a0b))


### BREAKING CHANGES

* API calls no longer block waiting for device response, use the add
handler to listen for updates from the device.

## [1.4.6](https://github.com/cmroche/greeclimate/compare/v1.4.5...v1.4.6) (2024-06-27)


### Bug Fixes

* Quiet mode to set value 2 not 1 ([#88](https://github.com/cmroche/greeclimate/issues/88)) ([129a190](https://github.com/cmroche/greeclimate/commit/129a1905940a0c723dce4890e6d567346967137c)), closes [#87](https://github.com/cmroche/greeclimate/issues/87)

## [1.4.5](https://github.com/cmroche/greeclimate/compare/v1.4.4...v1.4.5) (2024-06-27)


### Bug Fixes

* use of Queue where Event was expected ([#85](https://github.com/cmroche/greeclimate/issues/85)) ([9dfcdbb](https://github.com/cmroche/greeclimate/commit/9dfcdbb9ae65b2c5e2f4c753e1fe7e6fa7de70a3))

## [1.4.4](https://github.com/cmroche/greeclimate/compare/v1.4.3...v1.4.4) (2024-06-27)


### Bug Fixes

* twine upload error ([#84](https://github.com/cmroche/greeclimate/issues/84)) ([f097886](https://github.com/cmroche/greeclimate/commit/f097886cc39cca1beb20188cf8e762f121874cdf))

## [1.4.3](https://github.com/cmroche/greeclimate/compare/v1.4.2...v1.4.3) (2024-06-26)


### Bug Fixes

* Check for v4 temperature records ([#69](https://github.com/cmroche/greeclimate/issues/69)) ([#81](https://github.com/cmroche/greeclimate/issues/81)) ([f4882c1](https://github.com/cmroche/greeclimate/commit/f4882c1e6e3bbad5b62a5c6284ec6dbc26131d3d))

## [1.4.2](https://github.com/cmroche/greeclimate/compare/v1.4.1...v1.4.2) (2024-06-26)


### Bug Fixes

* Fahrenheit conversion inconsistencies ([#73](https://github.com/cmroche/greeclimate/issues/73)) ([f09f3f1](https://github.com/cmroche/greeclimate/commit/f09f3f1433968269027ea1d27259c09bc787df43))

## [1.4.1](https://github.com/cmroche/greeclimate/compare/v1.4.0...v1.4.1) (2023-02-05)


### Bug Fixes

* Allow socket reuse for discovery ([#64](https://github.com/cmroche/greeclimate/issues/64)) ([db819b4](https://github.com/cmroche/greeclimate/commit/db819b496c98f89330debd5668d3f0bfff729441))

# [1.4.0](https://github.com/cmroche/greeclimate/compare/v1.3.0...v1.4.0) (2022-12-03)


### Features

* Add device properties for dehumidifiers ([#62](https://github.com/cmroche/greeclimate/issues/62)) ([0e2a084](https://github.com/cmroche/greeclimate/commit/0e2a0846a2dd4ed5221c5861f5e5cd857a2dca2b))

# [1.3.0](https://github.com/cmroche/greeclimate/compare/v1.2.1...v1.3.0) (2022-08-06)


### Features

* Support manually passing bcast addresses to device scan ([b57dbd5](https://github.com/cmroche/greeclimate/commit/b57dbd50d95d92479550592378f61372754a6fe9))

## [1.2.1](https://github.com/cmroche/greeclimate/compare/v1.2.0...v1.2.1) (2022-06-05)


### Bug Fixes

* Bump semver-regex from 3.1.3 to 3.1.4 ([#54](https://github.com/cmroche/greeclimate/issues/54)) ([fdfa0f6](https://github.com/cmroche/greeclimate/commit/fdfa0f6a8eb362a2956cdc5d83eb7b61e93229e5))

# [1.2.0](https://github.com/cmroche/greeclimate/compare/v1.1.1...v1.2.0) (2022-05-22)


### Features

* Adding check and raise error when trying to convert out of range temp ([1bddf8b](https://github.com/cmroche/greeclimate/commit/1bddf8b7b34b7c1889812ff5c5e89128a1a365ce))

## [1.1.1](https://github.com/cmroche/greeclimate/compare/v1.1.0...v1.1.1) (2022-04-08)


### Bug Fixes

* Allow min temps down to 8C or 46F ([#52](https://github.com/cmroche/greeclimate/issues/52)) ([b957e0f](https://github.com/cmroche/greeclimate/commit/b957e0f33a2578f229f5e016b42349f561bd898e))
* Bump minimist from 1.2.5 to 1.2.6 ([#50](https://github.com/cmroche/greeclimate/issues/50)) ([95892e4](https://github.com/cmroche/greeclimate/commit/95892e4c8619daad72081b40f1c077149341cfbd))

# [1.1.0](https://github.com/cmroche/greeclimate/compare/v1.0.3...v1.1.0) (2022-03-06)


### Features

* Check firmware version from temperature report ([#49](https://github.com/cmroche/greeclimate/issues/49)) ([cd6a25f](https://github.com/cmroche/greeclimate/commit/cd6a25f9556e6fd3d4871ac86883d114fc1e9b9e))

## [1.0.3](https://github.com/cmroche/greeclimate/compare/v1.0.2...v1.0.3) (2022-02-13)


### Bug Fixes

* Add version from PyPI release to setup.cfg ([#47](https://github.com/cmroche/greeclimate/issues/47)) ([61e916a](https://github.com/cmroche/greeclimate/commit/61e916a9578bea2c5f100708ea208c823356ad94))

## [1.0.2](https://github.com/cmroche/greeclimate/compare/v1.0.1...v1.0.2) (2022-01-14)


### Bug Fixes

* Devices with NULL name use mac instead ([#44](https://github.com/cmroche/greeclimate/issues/44)) ([153cc32](https://github.com/cmroche/greeclimate/commit/153cc328dbfb2975f221bedc959e57754e993702))
* Handle undefined bcast or peer IPs from Wireshark ([#45](https://github.com/cmroche/greeclimate/issues/45)) ([e28eb83](https://github.com/cmroche/greeclimate/commit/e28eb83a3ec5a06f3b69affda5411de485f5ded2))

## [1.0.1](https://github.com/cmroche/greeclimate/compare/v1.0.0...v1.0.1) (2021-12-30)


### Bug Fixes

* Add overrides for MTK device IDs ([#41](https://github.com/cmroche/greeclimate/issues/41)) ([c036fd4](https://github.com/cmroche/greeclimate/commit/c036fd4c58703d152bee282d23caac6a81875a29))

# 1.0.0 (2021-11-21)


### Bug Fixes

* Support no "val" protocol variation ([f1993e1](https://github.com/cmroche/greeclimate/commit/f1993e1c6a582d701bf7b354f3b60e7e229f939a))
