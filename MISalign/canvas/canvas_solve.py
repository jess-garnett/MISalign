""" Canvas Solve
- Converts a set of relations into relative and absolute coordinate positions.
"""
import json
from os.path import split
from MISalign.model.relation import Relation

def rectangular_solve(relations:Relation,origin:str):
    """Solves a set of relations rectangularly
    - Input is a Relation object and the image name of the origin.
    - Output is a dictionary of the form "image_name":(origin-relative x, origin-relative y)
    - Origin-relative x and y may be negative values.
    """
    pass