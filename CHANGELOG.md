# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/2.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security

## [2.2.0.dev0]
### Added
- Additional example projects.
    - Description of project a.
    - project b - a sequential low-feature and high-overlap optical microscopy data set.
    - project c - a looped and branched medium-feature and medium-overlap optical microscopy data set.
    - project d - a sequential irregular grid high-feature medium-overlap optical microscopy data set.
    - project e - two sequential linear high-feature medium-overlap backscattered electron(BSE) scanning electron microscope(SEM) data sets.
    - project f - a sequential grid high-feature medium-overlap backscattered electron(BSE) and secondary electron(SE) scanning electron microscope(SEM) data set.
- `MISImage` array filtering and `MISProject.set_image_filter(filter)` for adding filters to images. [#14](https://github.com/jess-garnett/MISalign/issues/14)
    - Enables simple cropping(i.e. remove information bar) and type conversion(i.e. 16 bit image to 8 bit)
- Added image boundary overlays and image label overlays to matplotlib-based canvas displays in `scale_bar.py`.
- Added save with 10 to 1 downscaling option to the matplotlib-based canvas display in `render.ipynb`.
### Changed
- `canvas_rectangular.py` render can work with 2D/grayscale and 3D image depths other than `depth=3`/RGB. [#12](https://github.com/jess-garnett/MISalign/issues/12)
    - Added handling for 2D/grayscale images in `scale_bar.py` and `interactive_manual.py`
### Deprecated
### Removed
### Fixed
- `file_contains` and `file_notcontains` updated to work properly with Path objects in `setup.ipynb`.

## [2.1.0] - 2026-06-26
Primarily docstring and documentation development but during that process some code fixes, or renamings for clarity, were done.

### Added
- Documentation with Sphinx and Read the Docs.
- Code of Conduct.
- Changelog.
- Contributing Guide.
- Added docstrings for modules, classes, and functions. Updated the few that were previously present but out of date.

## [2.0.0] - 2026-05-18
A major refactor of MISalign to decouple modules and make it easier to extend. Many of the refactors involved creating a standard interface/Protocol for an aspect of MISalign and then splitting previously interlinked functionality into separate implementations of the interface.

- **Breaking:** The vast majority of classes and functions were modified in some capacity which likely breaks existing code at least slightly.
- Note: This changelog was written after the 2.0.0 release was already completed so it may be incomplete. Many things where changed or renamed as part of the holistic refactor process.

### Added
- HDF5 support added both for using data sets from existing HDF5 files(with `MISImageHDF5`) as well as native HDF5 single file projects(with `MISProjectHDF5`).
- The new `MISProject`, `MISImage`, and `MISRelation` classes all include data passthrough of JSON-serializable information. This means notes, priorities, or any other added detail can be included and should not be affected by MISalign load/update/save cycles. This opens up a lot of extensibility and was a major reason for the refactoring as the previous `.mis` format did not have much if any flexibility for including new data fields.
- `..._project` variants of many of the solving and rendering workflow functions in `canvas/canvas_rectangular` were added to simplify the rendering process when rendering from a `MISProject`.
### Changed
- **Breaking:** `model/project`>`MISProject` protocol with `MISProjectJSON` and `MISProjectHDF5` implementations replaces the `model/mis_file`>`MisFile` class for storing project data. `MisFile` projects were JSON stored with `.mis` file extension, `MISProjectJSON` projects are differently formatted JSON stored with a `.mis.json` file extension & extension prefix. A conversion function from `.mis` to `.mis.json` is available in the project module `model/project`>`convert_mis_project_json`.
- **Breaking:** `model/image`>`MISImage` with `MISImageFile` and `MISImageHDF5` implementations replace `model/image`>`Image`. This change was primarily made to enable non-image file data sources.
- **Breaking:** `model/relation`>`MISRelation` with `MISRelationReference`, `MISRelationRectangular`, and `MISRelationPoints` implementations replace `model/relation`>`Relation`. This change splits the if/else logic of each type of relation into their own class.
- **Breaking:** `canvas/canvas_render` and `canvas/canvas_solve` modules were merged into `canvas/canvas_rectangular` module.
- **Breaking:** To enable `MISImageHDF5` usage the visualization and rendering functions in `canvas/canvas_rectangular` and `alignment/interactive_manual` were changed to use `np.asarray(MISImage)` rather than take image filepaths and manually open the images.
- **Breaking:** Distance from edge generation `Image.dfe_arr()` was moved into `canvas/canvas_rectangular` as `weight_dfe()`

## [1.0.0] - 2024-05-14
The initial full release of MISalign.