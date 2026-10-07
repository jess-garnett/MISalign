---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.6
kernelspec:
  display_name: .venv
  language: python
  name: python3
---

# Relation Viewer Prototype
Purpose: Explore options for viewing relations

```{code-cell} ipython3
import sys
import os
sys.path.insert(0, os.path.abspath("../.."))  # Repository directory relative to this file.
from misalign.model.relation import Relation
```

# Initial Prototyping

```{code-cell} ipython3
#setup test data 1
#basic split data set 
image_fps=['img_a','img_b','img_c','img_d','img_e','img_f']
rel1=[
    Relation('img_a','img_b'),
    Relation('img_b','img_c'),
    Relation('img_c','img_d'),
    Relation('img_a','img_e'),
    Relation('img_e','img_f')
]
display([x.ref for x in rel1])
```

```{code-cell} ipython3
%pip install networkx[default]
```

```{code-cell} ipython3
import networkx as nx
G = nx.Graph()
```

```{code-cell} ipython3
G.add_nodes_from(image_fps)
```

```{code-cell} ipython3
H=nx.Graph()
H.add_edges_from([x.ref for x in rel1])
```

```{code-cell} ipython3
display(G.nodes)
display(G.edges)
display(G.adj)
display(G.degree)
```

```{code-cell} ipython3
display(H.nodes)
display(H.edges)
display(H.adj)
display(H.degree)
```

```{code-cell} ipython3
L=nx.Graph([x.ref for x in rel1])
display(L.nodes)
display(L.edges)
display(L.adj)
display(L.degree)
```

```{code-cell} ipython3
G.add_edge(rel1[0].ref[0],rel1[0].ref[1],object=rel1[0])
#give object to edge!
```

```{code-cell} ipython3
H.add_edge("img_c","img_g")
H.add_edge("img_g","img_h")
H.add_node("img_a",color='red')
```

```{code-cell} ipython3
h_color=['b']*len(H.nodes)
h_color[0]='g'
```

```{code-cell} ipython3
import numpy as np

lay=nx.drawing.planar_layout(H)
lay['img_a']=np.array([0,0])
lay['img_b']=np.array([-1,-1])
lay['img_c']=np.array([-1,-2])
lay['img_d']=np.array([-1,-3])
lay['img_e']=np.array([1,-1])
lay['img_f']=np.array([1,-2])
nx.draw_networkx(H,node_color=h_color,pos=lay)
display(lay)
```

```{code-cell} ipython3
a1 = {'a':1, 'b':13, 'd':4, 'c':2, 'e':30}
a1_sorted_keys = sorted(a1, key=a1.get, reverse=True)
for r in a1_sorted_keys:
    print(r, a1[r])
```

```{code-cell} ipython3
nodes=list(H.nodes)
start='img_a'
adj={x:list(H.adj[x]) for x in H.adj}
adj_count={x:len(H.adj[x]) for x in H.adj}
chains=np.sum(np.asarray(list(adj_count.values()))<=1)
display(adj)
display(adj_count)
print("Chains:",chains)
v_spacing_dict=nx.shortest_path_length(H,None,start)
display(v_spacing_dict)
ordering=sorted(v_spacing_dict,key=v_spacing_dict.get,reverse=True)
h_spacing_dict={}
display(ordering)
# i=0
# for item in ordering:
#     if item==start:
#         h_spacing_dict[item]=0
#     if adj_count[item]<=2: #find children in linear chain and set them to have the same h-spacing
#         for x in adj[item]:
#             if x not in h_spacing_dict:
#                 h_spacing_dict[x]=h_spacing_dict[item]
#     else:
#         #deal with splitting?
#         pass
# display(h_spacing_dict)
```

```{code-cell} ipython3
[x for x in nx.chain_decomposition(H,root=start)]

nx.draw_networkx(nx.bfs_tree(H,'img_a'))
```

# Prototyping part 2

```{code-cell} ipython3
import networkx as nx
import numpy as np
```

```{code-cell} ipython3
#setup test data 1
#basic split data set 
image_fps=['img_a','img_b','img_c','img_d','img_e','img_f']
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
display([x.ref for x in rel1])
G=nx.from_edgelist([x.ref for x in rel1])
H=nx.bfs_tree(G,'img_a')
distance=nx.shortest_path_length(H,'img_a')
max_distance=max(distance.values())
colormap=[(0,1,(1-dist/max_distance)) for dist in distance.values()]
display(H.nodes)
pos=nx.planar_layout(H)
pos={x:pos[x]-np.array([0,5]) for x in pos}
display(pos)
pos['img_a']=np.array([0,0])
i=0
j=0
k=0
l=0
m=0
n=0
for img in H.adj['img_a']:
    pos[img]=[i,-1]
    i+=1
    for img_ in H.adj[img]:
        pos[img_]=[j,-2]
        j+=1
        for img__ in H.adj[img_]:
            pos[img__]=[k,-3]
            k+=1
            for img___ in H.adj[img__]:
                pos[img___]=[l,-4]
                l+=1
                for img____ in H.adj[img___]:
                    pos[img____]=[m,-5]
                    m+=1
                    for img_____ in H.adj[img____]:
                        pos[img_____]=[n,-6]
                        n+=1
nx.draw_networkx(H,node_color=colormap,pos=pos)
```

```{code-cell} ipython3
#goal: functionalize that giant for loop
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
display(width_dict)
display(func_pos)
nx.draw_networkx(H,node_color=colormap,pos=func_pos)
```

```{code-cell} ipython3
#https://networkx.org/documentation/stable/auto_examples/drawing/plot_custom_node_icons.html#sphx-glr-auto-examples-drawing-plot-custom-node-icons-py
#could use picture as node.
import PIL
from os.path import abspath
img=PIL.Image.open(abspath(r"..\..\example\data\set_a\a_myimages01.jpg"))
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
f_pos={x:i*np.array([1,2]) for x,i in func_pos.items()}
fig.set_figheight(6+1)
fig.set_figwidth(4+1)
nx.draw_networkx_edges(
    G,
    pos=f_pos,
    ax=ax,
    arrows=True,
    arrowstyle="-",
    min_source_margin=15,
    min_target_margin=15,
)
# Transform from data coordinates (scaled between xlim and ylim) to display coordinates
tr_figure = ax.transData.transform
# Transform from display to figure coordinates
tr_axes = fig.transFigure.inverted().transform

# Select the size of the image (relative to the X axis)
icon_size = 0.1#(ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.025
icon_center = icon_size / 2.0

# Add the respective image to each node
for node in H.nodes():
    xf, yf = tr_figure(f_pos[node])
    xa, ya = tr_axes((xf, yf))
    # get overlapped axes and plot icon
    a = plt.axes([xa - icon_center, ya - icon_center, icon_size, icon_size])
    a.imshow(img)
    a.axis("off")


nx.draw_networkx_labels(H,pos={x:i+np.array([0,0.8]) for x,i in f_pos.items()},ax=ax)
plt.show()
```
