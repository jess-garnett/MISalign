# HDF5 Examples
Since MISalign 2.0, datasets in [HDF5 files](https://www.hdfgroup.org/solutions/hdf5/) are supported as an alternative data source to image files. The example folder of the git repository contains multiple examples showing how MISalign can be used with HDF5 files, both ones that it created as well as ones from other sources such as [NeXus](https://www.nexusformat.org/) and [Dream3D](https://www.bluequartz.net/software/dream3d-nx/).
## Native HDF5 Support

`/example/project_a0_hdf5` folder in the [git repository](https://github.com/jess-garnett/MISalign/tree/main/example/project_a0_hdf5).

The example `.ipynb` includes setting up a `MISProjectHDF5` by ingesting image files, adding relations from an existing project, and rendering from the `.hdf5` project file. The `.mis.hdf5` project file is included in the example folder.

Note: Rather than adding relations from an existing project, this file could be used with `notebooks/align.ipynb` by changing the `MISProjectJSON` in the align notebook to `MISProjectHDF5`.

## NeXus Format HDF5 Support

`/example/project_a1_nexus` folder in the [git repository](https://github.com/jess-garnett/MISalign/tree/main/example/project_a1_nexus).

The example `.ipynb` includes building a mock `.nxs` (using `nexusformat` and `pynxtools`) and then doing image dataset discovery from the mock `.nxs`, constructing a `MISProjectJSON` with the datasets in the HDF5, adding relations from an existing project, adding scale calibration, and then saving the `.mis.json`. This `.mis.json` is suitable for use in `notebooks/render.ipynb` for rendering from the `.nxs` file. The `.mis.json` project file and the `.nxs` data source are included in the example folder.

Note: Rather than adding relations from an existing project, this file could be used with `notebooks/align.ipynb`.

## Dream3D Format HDF5 Support

`/example/project_a2_dream3d` folder in the [git repository](https://github.com/jess-garnett/MISalign/tree/main/example/project_a2_dream3d).

The example `.ipynb` includes building a mock `.dream3d` (using `simplnx`) and then doing image dataset discovery from the mock `.dream3d`, constructing a `MISProjectJSON` with the datasets in the HDF5, adding relations from an existing project, adding scale calibration, and saving the `.mis.json`. This `.mis.json` is suitable for use in `notebooks/render.ipynb` for rendering from the `.dream3d` file. The `.mis.json` project file and the `.dream3d` data source are included in the example folder.

Note: Rather than adding relations from an existing project, this file could be used with `notebooks/align.ipynb`.