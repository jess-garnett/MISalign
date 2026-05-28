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

    def find_image_path(self,
            mis_fp:Path|str,
            update:bool=True
            )->Path|None:
        """
        Find, and optionally update, hdf5 filepaths.
        
        Checks stored location. Checks mis filepath folder for matching name.

        Parameters
        ----------
        mis_fp:Path|str,
            Filepath to MISProject, expected to be in the same folder as the hdf5 file.
        update:bool=True
            If true when a matching file is found it will replace `self.hdf5_filepath`.

        Returns
        -------
        return_path : Path | None
            If a matching path is found it is returned, else `None` is returned.
        """

Template Class Docstring
------------------------

.. code-block:: python

    class MISImageFile():
        """
        Access image data and information from an image file.
        """

Template Module Docstring
-------------------------

.. code-block:: python

    """
    Models for handling data organization, data access, and file I/O.

    Includes `Protocol` models: `MISProject`, `MISImage`, and `MISRelation`.
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

Notes
=====

`__init__` class methods are currently only documented on their respective class pages rather than in their own dedicated page.

References
==========

This guide draws upon existing projects & documentation for direction including:

* `numpydoc docstring guide <https://numpydoc.readthedocs.io/en/latest/format.html>`_
* `pandas docstring guide <https://pandas.pydata.org/docs/development/contributing_docstring.html>`_
* `Sphinx reStructuredText Primer <https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`_
* `Quick reStructuredText reference <https://docutils.sourceforge.io/docs/user/rst/quickref.html>`_
* `Full reStructuredText specification <https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html>`_
