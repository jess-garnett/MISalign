"""Helper functions for relation model:
- Relation tree visualizer
"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import PIL
from .relation import Relation

# from MISalign.model.relation import Relation


def relation_tree(rel_list,start,show_ion=False,return_fig_ax=False):
    """Function to generate a relation tree from a list of relations.
    
    - rel_list: A list of Relation objects.
    - start: String name of the reference to use as the origin.
    - show_ion: Show the interactive matplotlib plot of the relation tree.
    - return_fig_ax: Return the matplotlib figure and axes of the relation tree.
    """
    G=nx.from_edgelist([x.ref for x in rel_list])
    H=nx.bfs_tree(G,'img_a')
    distance=nx.shortest_path_length(H,start)
    max_distance=max(distance.values())
    colormap=[(0,1,(1-dist/max_distance)) for dist in distance.values()]
    def tree_step(G:nx.digraph,start:str,depth:int=-1,width:dict={0:0},pos:dict=None):
        if pos is None:
            pos={start:np.array([0,0])}
        if depth not in width:
            width[depth]=0
        for img in sorted(G.adj[start]):
            pos[img]=np.array([width[depth],depth])
            pos,width=tree_step(G,img,depth=depth-1,width=width,pos=pos)
            width[depth]+=1
        return pos,width

    func_pos,width_dict=tree_step(H,'img_a')
    max_width=max(width_dict.values())
    print(width_dict)
    print(func_pos)
    nx.draw_networkx(H,node_color=colormap,pos=func_pos,node_shape='s',arrowstyle="<->",font_size=6,node_size=600)
    plt.figure(num=plt.gcf(),figsize=[2,12])
    if show_ion is True:
        plt.gca().axis('off')
        plt.gcf().set_size_inches((max_width+1, max_distance+1))
        plt.show()
    if return_fig_ax is True:
        return [plt.gcf(),plt.gca()]
    else:
        return None


if __name__=="__main__":
    rel1=[#'over and down' pattern
    Relation('img_a','img_b'),
    Relation('img_b','img_c'),
    Relation('img_c','img_d'),
    Relation('img_a','img_aa'),
    Relation('img_aa','img_ab'),
    Relation('img_ab','img_ac'),
    Relation('img_b','img_ba'),
    Relation('img_ba','img_bb'),
    Relation('img_bb','img_bc'),
    Relation('img_c','img_ca'),
    Relation('img_ca','img_cb'),
    Relation('img_cb','img_cc'),
    Relation('img_d','img_da'),
    Relation('img_da','img_db'),
    Relation('img_da','img_de'),
    Relation('img_de','img_df'),
    Relation('img_de','img_dg'),
    Relation('img_db','img_dc')
    ]
    relation_tree(rel1,start='img_a',show_ion=True)