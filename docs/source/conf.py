# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'misalign'
copyright = '2023, Jessica Garnett'
author = 'Jessica Garnett'
release = '2.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'numpydoc',
    'myst_nb'
]

autosummary_generate = True
numpydoc_show_class_members = False 

source_suffix = {
    '.rst': 'restructuredtext',
    '.ipynb': 'myst-nb',
    '.myst': 'myst-nb',
}
nb_execution_mode = "cache"


templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_logo = '../../develop/misalign_logo/misalign_logo_r2_wide.png'


# -- Copy Notebooks from Primary Folder ---------------------------------------------------
from pathlib import Path
from json import loads,dumps
notebook_source_path=Path("../../notebooks")
notebook_docs_path=Path("./_notebooks")
notebook_docs_path.mkdir(exist_ok=True)
example_path_find="../example/"
example_path_replace="../../../example/"
for notebook in [
    "align.ipynb",
    "calibrate.ipynb",
    "render.ipynb",
    "setup.ipynb"
    ]:
    with open(notebook_source_path.joinpath(notebook)) as f_s:
        notebook_text=f_s.read()

    notebook_text=notebook_text.replace(example_path_find,example_path_replace)
    notebook_text=notebook_text.replace("**Imports**",r"```{note}\n This notebook is modified from how it appears in the 'notebooks' directory so it can render properly in the documentation. Primarily, this includes changed paths and mocked user interactions.\n```\n\n**Imports**")

    match notebook:
        case "render.ipynb":
            # disable auto save renders in case it was accidentally left enabled.
            notebook_text.replace("auto_save_renders=True","auto_save_renders=False")
        case _:
            pass
    notebook_json=loads(notebook_text)
    # notebook_json["metadata"]["mystnb"]={'execution_mode':'inline'}
    match notebook:

        case "calibrate.ipynb":
            # notebook_json["metadata"]["mystnb"]={'execution_mode':'off'}
            mock_user_selection=[
                "\n\n### Code used to simulate user-input for documentation generation. ###\n",
                "# Replaces a user selecting feature points on the calibration image.\n",
                "class mock_event:\n","    def __init__(self, button, xdata, ydata):\n",
                "        self.button = button\n",
                "        self.xdata = xdata\n",
                "        self.ydata = ydata\n",
                "cm._calibrate_callback(mock_event(button=1, xdata=500, ydata=480))\n",
                "cm._calibrate_callback(mock_event(button=1, xdata=1099, ydata=480))\n",
                "cm._calibrate_callback(mock_event(button=1, xdata=498, ydata=690))\n",
                "cm._calibrate_callback(mock_event(button=1, xdata=1095, ydata=695))\n",
                "cm._calibrate_callback(mock_event(button=1, xdata=1095, ydata=695))\n",
                "cm.calibrate_resolve()\n",
                "from IPython.display import clear_output\n",
                "from matplotlib import pyplot as plt\n",
                "clear_output()\n",
                "plt.show()\n",
                "### End ###"
                ]
            mock_user_selection_index=[i for i,cell in enumerate(notebook_json["cells"])
                                                if "cm.calibrate_setup()" in str(cell["source"])][0]
            notebook_json["cells"][mock_user_selection_index]["source"].extend(mock_user_selection)
        case "render.ipynb":
            notebook_json["metadata"]["mystnb"]={'render_image_options':{"height":'1000px'}}
            mock_user_selection_index=[i for i,cell in enumerate(notebook_json["cells"])
                                                if 'loc="upper left")' in str(cell["source"])][0]
            mock_user_selection=[
                "\n\n### Code used to correct rendering for documentation generation. ###\n",
                "# Runs scale calibration code in the same cells as plotting code for figure generation.\n",
                "scale_bar_calibrate(scale_dpi=1000)\n",
                "from IPython.display import clear_output\n",
                "from matplotlib import pyplot as plt\n",
                "clear_output()\n",
                "plt.show()\n",
                "### End ###"
                ]
            notebook_json["cells"][mock_user_selection_index]["source"].extend(mock_user_selection)
        case "align.ipynb":
            mock_user_selection_index=[i for i,cell in enumerate(notebook_json["cells"])
                                                if 'imrc=IMRControls' in str(cell["source"])][0]
            mock_user_selection=[
                "\n\n### Code used to simulate user-input for documentation generation. ###\n",
                "# Replaces a user selecting matching points on the calibration image.\n",
                "class mock_event:\n","    def __init__(self, button, xdata, ydata):\n",
                "        self.button = button\n",
                "        self.xdata = xdata\n",
                "        self.ydata = ydata\n",
                "imrc.imr._relate_callback(mock_event(button=1, xdata=1325, ydata=1150))\n",
                "imrc.imr._relate_callback(mock_event(button=1, xdata=1335, ydata=1260))\n",
                "imrc.imr._relate_callback(mock_event(button=1, xdata=570, ydata=1170))\n",
                "imrc.imr._relate_callback(mock_event(button=1, xdata=580, ydata=1280))\n",
                "imrc.imr._relate_callback(mock_event(button=1, xdata=1080, ydata=1100))\n",
                "imrc.imr._relate_callback(mock_event(button=1, xdata=1090, ydata=1210))\n",
                "imrc._click_resolve('')\n",
                "from IPython.display import clear_output,display\n",
                "from matplotlib import pyplot as plt\n",
                "clear_output()\n",
                "display(imrc._full)\n"
                "plt.show()\n",
                "### End ###"
                ]
            notebook_json["cells"][mock_user_selection_index]["source"].extend(mock_user_selection)
        case _:
            pass
    skip_execution=False
    skip_execution_index=-1
    for i,cell in enumerate(notebook_json["cells"]):
        if cell["cell_type"]=="code":
            if "mis_project.save(mis_filepath)" in str(cell["source"]) and not skip_execution: # setup.ipynb end.
                skip_execution=True
                skip_execution_index=i
            if "imrc.get_mis" in str(cell["source"]) and not skip_execution: # align.ipynb end.
                skip_execution=True
                skip_execution_index=i
            if "scale_bar_calibrate(scale_dpi=scaled_dpi)" in str(cell["source"]) and not skip_execution: # render.ipynb end.
                skip_execution=True
                skip_execution_index=i
            
            if skip_execution:
                try:
                    cell["metadata"]["tags"].append("skip-execution")
                except KeyError:
                    cell["metadata"]["tags"]=["skip-execution"]
        notebook_json["cells"][i]=cell

    if skip_execution:
        notebook_json["cells"].insert(skip_execution_index,{
        "cell_type": "markdown",
        "metadata": dict(),
        "source": [
            "```{note}\nNo further cells are executed in this notebook in the documentation.\n```\n"
        ]
        })
                
        

    with open(notebook_docs_path.joinpath(notebook),mode='w') as f_d:
        f_d.write(dumps(notebook_json,indent=2))
        