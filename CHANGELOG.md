# Changelog

## [2.2.0] - 2025-01-22

### Added

* Add corner connector command
* Add script to download translations from CrowdIn using API
* Add German, Greek, French, Italian, Polish and Swedish translations

### Changed

* Rename the icons following FreeCAD guidelines
* Match properties tooltips to wiki
* Update Spanish translations

### Fixed

* Show commands' translated tooltips when using custom tooltip with icon
* Show height in the units preferred by the user
* Use correct parameter on `ExtraBottomMaterial` check

## [2.1.1] - 2024-11-10

### Fixed

* Only disable `ExtraBottomMaterial` when it exists

## [2.1.0] - 2024-11-10

### Added

* Make boxes and holders attachable to grids.

### Changed

* Strings for translation.
* Disable `ExtraBottomMaterial` property when subtractive method is not selected

### Fixed

* Set limits on integer and length properties

## [2.0.1] - 2024-10-31

### Changed

* Clean icons' SVG files.

### Fixed

* Fix view provider that  was not using full path when using icon for tree view.

## [2.0.0] - 2024-09-23

🎉 Workbench release.

### Added

* Introduce to users the bit cartridge holder
* Add docstrings to methods.
* Add translation support.
* Add possibility to assign a random color at creation time.
* Add transaction at creation time.
* Add task panel to set sketch size.
* Add pre-commit hooks.
* Add preferences page and command to open preferences page.
* Add command to open about page.

### Changed

* Migrate from macro to workbench.
* Make created objects fully parametric, properties can be changed on Properties View panel.

### Fixed

* Fix issue when trying to create a storage box smaller than $10[mm]$. Useful to get a "floor".

## [1.3.0] - 2024-01-16

### Fixed

* Fix issue when copying dividers, now built-in `copy()` method is used.

### Changed

* Add forms to let users enter magnet parameters to both boxes and grids.
* Use FreeCAD Quantity parser for length dimensions.

## [1.2.1] - 2023-08-23

### Changed

* Objects generated by the macro are now refined to clean up edges and faces.
* A box can now have a height of zero, in which case a flat base with no walls will be created.
* Floor support generation is visible in the UI (thanks @johnsonm)

## [1.2.0] - 2022-08-26

### Added

* Add `set_param()` method to box and grid to make data-driven generation easier

## [1.1.1] - 2022-07-27

### Added

* Add test methods for quality assurance

### Changed

* Refactor length, width, depth for consistency with GUI

## [1.1.0] - 2022-07-26

### Added

* Add option to generate box with open front face.
* Add sketch generator for inside profile of a box.

### Fixed

* Fixed issue with box height computation.

## [1.0.2] - 2022-07-26

### Fixed

* Change "number of dividers" to "number of divisions" to reflect what actually happens.

## [1.0.1] - 2022-07-25

### Fixed

* Fix axis mix-up with magnet pads in grids.

## [1.0.0] - 2022-07-25

🌱 Initial release.

### Added

* Grids with or without magnets
* Boxes with options for magnets, a grip/label bar, and a front scoop.

[1.0.0]: https://github.com/instancezero/in3dca-freegrid/releases/tag/1.0.0
[1.0.1]: https://github.com/instancezero/in3dca-freegrid/releases/tag/1.0.1
[1.0.2]: https://github.com/instancezero/in3dca-freegrid/releases/tag/1.0.2
[1.1.0]: https://github.com/instancezero/in3dca-freegrid/releases/tag/1.1.0
[1.1.1]: https://github.com/instancezero/in3dca-freegrid/releases/tag/1.1.1
[1.2.0]: https://github.com/instancezero/in3dca-freegrid/releases/tag/1.2.0
[1.2.1]: https://github.com/instancezero/in3dca-freegrid/releases/tag/1.2.1
[1.3.0]: https://github.com/instancezero/in3dca-freegrid/releases/tag/1.3.2
[2.0.0]: https://github.com/instancezero/in3dca-freegrid/releases/tag/2.0.0
[2.0.1]: https://github.com/instancezero/in3dca-freegrid/releases/tag/2.0.1
[2.1.0]: https://github.com/instancezero/in3dca-freegrid/releases/tag/2.1.0
[2.1.1]: https://github.com/instancezero/in3dca-freegrid/releases/tag/2.1.1
[2.2.0]: https://github.com/instancezero/in3dca-freegrid/releases/tag/2.2.0
