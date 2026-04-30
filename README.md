# MISalign
A Metallography Image Software for Alignment.

## Still very much in development.
The `notebooks` folder is setup with example data.

The primary workflow is `setup.ipynb` > `align.ipynb` > `render.ipynb`

As of 4/30/2026 `misalign` is close to version 2.0
As of 5/14/2024 `misalign` is on version 1.0

## What does this project do?
This project seeks to make the process of going from many metallography images to a single sample image simpler. The two primary steps in this process is alignment and image composition and blending.
## Why is this project useful?
I found the process of assembling images to be very frustrating and time consuming while also leaving many assembly artifacts in the final image. After exploring existing solutions and not finding any I was happy with I started to develop this project to address that need.

One of the core issues I found with many existing alternatives is that they focused on automatic alignment and for the data sets I use that didn't work consistently. One of the core assumptions of misalign is that the user knows what they want in terms of alignment or image-image relationship and they should be able to efficiently communicate that to the program.
## How do I get started?
Requirements.txt includes everything you need for your virtual environment and the `notebooks` folder is configured with paths to the example data so you can explore how it works.
## Where can I get more help, if I need it?
Feel free to share issues on the Github(https://github.com/jess-garnett/misalign/issues). Documentation may also be developed which can be referenced.

## Python and NumPy version support
This project intends on following [NEP 29 — Recommend Python and NumPy version support as a community policy standard](https://numpy.org/neps/nep-0029-deprecation_policy.html) and [SPEC 0 — Minimum Supported Dependencies](https://scientific-python.org/specs/spec-0000/) for its Python version and core package dependency support.