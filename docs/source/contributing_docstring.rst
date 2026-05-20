.. _docstring:


========================
misalign docstring guide
========================

About docstrings
================

A documentation string(docstring) is a string used to document a module, class, function or method, so users can get information about what it does and how to use it without needing to read and understand the implementation. See :ref:`docstrings_references` for more information about how they are used in other projects.

`Sphinx <https://www.sphinx-doc.org>`_ is used to extract and convert docstrings into documentation HTML.

Template Function/Method Docstring
----------------------------------

.. code-block:: python

    def rectangular_solve_project(
        project:MISProject,
        image_names:list[str]|None=None,
        origin:str|None=None):
    """
    Solves a set of relations rectangularly given a MISProject
    - Input is a MISProject, optional: a list of image names(otherwise all images in project used), and optional: the image name of the origin(otherwise first image used).
    - Output is a dictionary of the form "image_name":(origin-relative x, origin-relative y)
    - Origin-relative x and y may be negative values.
    """

Template Class Docstring
------------------------

.. code-block:: python

    class MISImageFile():
        """
        Access image data and information from an image file.
        
        Initialization
        --------------
        **image_data : kwargs
            image_filepath : Path | str
                File path to an image file.
            Any other passed kwargs will be kept in `self._dict`.

        Attributes
        ----------
        shape : tuple[int, ...]
            Numpy shape of the image.
        name : str
            Name of the image.

        Methods
        -------
        __array__() : numpy.ndarray
            Get the array of the image.
        for_json() : dict
            Get a JSON compatible dict.
        """

Template Module Docstring
-------------------------

.. code-block:: python

    """
    Models for handling data organization, data access, and file I/O.

    Includes `Protocol` models: MISProject, MISImage, and MISRelation.
    """

Sections
========

1. Short Summary
-----------------

Single sentence description of what the object does.

2. Extended Summary
--------------------

Additional details on what the object does. Excludes parameters or implementation notes. A blank line is left between short and extended summaries. Should include details on why the object is useful and its use cases.

3. Parameters
--------------

The details of the parameters go in this section. Generally, the pandas docstring guide for `parameters <https://pandas.pydata.org/docs/development/contributing_docstring.html#section-3-parameters>`_ should be followed.

Class `__init__` parameters should go into the class description with the title `Initialization`

4. Returns Or Yields
---------------------

If a function or method returns(or yields) a value it should be document in this section. Generally, the pandas docstring guide for `returns or yields <https://pandas.pydata.org/docs/development/contributing_docstring.html#section-4-returns-or-yields>`_ should be followed.

5. Notes
---------

This is an optional section for additional information about the object. This could include implementation notes or counter-intuitive behavior.

6. Examples
------------

This section is for examples illustration the use of the object. Generally, the pandas docstring guide for `examples <https://pandas.pydata.org/docs/development/contributing_docstring.html#section-7-examples>`_ should be followed.

.. _docstrings_references:

References
==============================

This guide draws upon existing projects & documentation for direction including:

* `numpydoc docstring guide <https://numpydoc.readthedocs.io/en/latest/format.html>`_
* `pandas docstring guide <https://pandas.pydata.org/docs/development/contributing_docstring.html>`_
* `Sphinx reStructuredText Primer <https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`_
* `Quick reStructuredText reference <https://docutils.sourceforge.io/docs/user/rst/quickref.html>`_
* `Full reStructuredText specification <https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html>`_
