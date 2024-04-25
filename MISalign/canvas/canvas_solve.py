""" Canvas Solve
- Converts a set of relations into relative and absolute coordinate positions.
"""
from MISalign.model.relation import Relation

def rectangular_solve(relations:list[Relation],image_names:list,origin:str):
    """Solves a set of relations rectangularly
    - Input is a list of rectangular relations, a list of image names, and the image name of the origin.
    - Output is a dictionary of the form "image_name":(origin-relative x, origin-relative y)
    - Origin-relative x and y may be negative values.
    """
    relation_map=_relation_map(relations,image_names,origin)
    orig_rel_position={origin:(0,0)}
    solving=[origin]
    cansolve=[]
    solved=[]
    while len(solving)>0:
        for s in solving:
            for image_name,rel in relation_map[s]:
                cansolve.append(image_name)
                if rel[0][0]==s:
                    direction=1
                else:
                    direction=-1
                orig_rel_position[image_name]=(orig_rel_position[s][0]+direction*rel[1][0],orig_rel_position[s][1]+direction*rel[1][1])
        solved+=solving
        solving=cansolve
        cansolve=[]
    return orig_rel_position

def _relation_map(relations:list[Relation],image_names:list,origin:str):
    """Identify a map from origin to other images in a list of relations.
    - Input is a list of relations, a list of image names, and the image name of the origin.
    - Output is a dictionary of the form "image_name":[images that reference to this image]
    """
    found=[image_names.index(origin)]
    matched=[]
    resolved=[]
    relation_map=dict({x:[] for x in image_names})

    while len(resolved)<len(relations):
        for i in found:
            for ii,x in enumerate(image_names):
                if (ii not in found) & (ii not in resolved) & (ii not in matched):
                    i_match=[image_names[i] in r[0] for r in relations]
                    ii_match=[image_names[ii] in r[0] for r in relations]
                    full_match=[im&iim for im,iim in zip(i_match,ii_match)]
                    if any(full_match):
                        relation_map[image_names[i]].append((image_names[ii],relations[full_match.index(True)]))
                        matched.append(ii)
            resolved.append(i)
        found=matched
        matched=[]
        #break if stuck
        if found==[]:
            break
    return relation_map
