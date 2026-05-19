# MISalign
A Metallography Image Software for Alignment.

[![SPEC 0 — Minimum Supported Dependencies](https://img.shields.io/badge/SPEC-0-green?labelColor=%23004811&color=%235CA038)](https://scientific-python.org/specs/spec-0000/)

## How to use MISalign
The `notebooks` folder has pre-configured Jupyter Notebooks that run through the process of using `misalign` on the example data in the `example` folder.

The primary workflow is `setup.ipynb` > `align.ipynb` > `render.ipynb`

As of 5/18/2026 `misalign` is on version 2.0

As of 5/14/2024 `misalign` is on version 1.0

## What does this project do?
This project seeks to make the process of going from many metallography images to a single sample image simpler. The two primary steps in this process is alignment and rendering (also knows as montaging, stitching, or compositing).
## Why is this project useful?
In 2022 at the start of my PhD, I found the process of assembling images to be very frustrating and time consuming while also leaving many assembly artifacts in the final image. After exploring existing solutions and not finding any I was happy with I started to develop this project to address that need.

One of the core issues I found with many existing alternatives is that they focused on automatic alignment and for the data sets I use that didn't work consistently. One of the core assumptions of `misalign` is that the user knows what they want in terms of alignment or image-image relationship and they should be able to efficiently communicate that to the program.
## How do I get started?
We're in the process of getting on PyPi so for now you will need to download(or clone) a copy of this repository.
We recommend using [uv](https://docs.astral.sh/uv/) for python package management. With uv installed you should be able to run `uv sync --all-extras` and then `misalign` will be installed in its own virtual environment and ready to use with the Jupyter Notebooks(`.ipynb`) in the `notebooks` folder which are configured with paths to the example data so you can explore how it works.
## Where can I get more help, if I need it?
Feel free to share issues on the Github(https://github.com/jess-garnett/misalign/issues).

Documentation is being developed following the 2.0 release: https://misalign.readthedocs.io/en/stable/

## Python and Package Version Support
This project follows [SPEC 0 — Minimum Supported Dependencies](https://scientific-python.org/specs/spec-0000/) for its Python version and package dependency support.

Note: Automated testing uses the `--resolution lowest-direct` option only on the oldest version of python supported. This gives some coverage of the specified oldest compatible packages while avoiding the issues that arise with using a python version released after a package version(i.e. missing wheels causing failed builds).