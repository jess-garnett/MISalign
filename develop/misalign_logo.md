---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.6
kernelspec:
  display_name: misalign
  language: python
  name: python3
---

```{code-cell} ipython3
import numpy as np
from PIL import Image as PILImage
from matplotlib import pyplot as plt
import misalign.canvas.canvas_rectangular as cr
%matplotlib widget
```

```{code-cell} ipython3
# reference: https://matplotlib.org/stable/users/explain/text/text_intro.html
# reference: https://jonathansoma.com/lede/data-studio/matplotlib/list-all-fonts-available-in-matplotlib-plus-samples/
plt.text(x=0,y=0.2,s="MIS",
    fontsize=100,
    color="black",
    # family='fantasy',
    font="Bahnschrift",
    )
plt.text(x=0.1,y=0.1,s="align",
    fontsize=80,
    color="green",
    # family='monospace',
    # font="Bahnschrift",
    # font="Arial",
    font="Verdana",
    )

plt.ylim(0,0.4)
plt.xlim(0,0.4)
plt.gca().set_axis_off()
plt.gca().set_aspect('equal', adjustable='box')
plt.tight_layout()
plt.gcf().set_size_inches(4, 4)

plt.savefig("misalign_logo/misalign_logo_r1.svg",dpi=300,transparent=True)
plt.savefig("misalign_logo/misalign_logo_r1.png",dpi=300,transparent=True)
plt.savefig("misalign_logo/misalign_logo_r1_small.png",dpi=75,transparent=True)
```

```{code-cell} ipython3
plt.figure()
logo_array=np.asarray(PILImage.open("misalign_logo/misalign_logo_r1.png"))
plt.imshow(logo_array)
xy_mis=(0,200)
xy_align=(225,550)
width=925
height=500 #450
plt.gca().add_artist(plt.Rectangle(xy_mis,width,height,edgecolor="red",fill=False))
plt.gca().add_artist(plt.Rectangle(xy_align,width,height,edgecolor="red",fill=False))

points=[(285,598),(325,598),(398,598),(438,598),(495,565),(600,600),(549,627)]
plt.scatter([point[0] for point in points],[point[1] for point in points],marker="x")

plt.xlim(xy_align[0]-5,xy_mis[0]+width+5)
plt.ylim(xy_mis[1]+height+5,xy_align[1]-5)
plt.show()
```

```{code-cell} ipython3
plt.figure()
plt.imshow(logo_array[xy_mis[1]:xy_mis[1]+height,xy_mis[0]:xy_mis[0]+width])
plt.figure()
plt.imshow(logo_array[xy_align[1]:xy_align[1]+height,xy_align[0]:xy_align[0]+width])
# plt.plot([pop[0][0],pop[1][0]],[pop[0][1],pop[1][1]+self._height],"x:")
plt.show()
```

```{code-cell} ipython3
image_arrays={
        "mis":logo_array[xy_mis[1]:xy_mis[1]+height,xy_mis[0]:xy_mis[0]+width,:-1],
        "align":logo_array[xy_align[1]:xy_align[1]+height,xy_align[0]:xy_align[0]+width,:-1]
    }
canvas_extents={"width":1200,"height":1200}

misalignment=np.array([40,30])

canvas_relative_offsets={
        "mis":xy_mis,
        "align":misalignment+xy_align # introduce intentional misalignment.
    }
normalizer=cr.build_normalization(
    image_arrays=image_arrays,  # ty:ignore[invalid-argument-type]
    canvas_relative_offsets=canvas_relative_offsets,
    canvas_extents=canvas_extents,
    weight=cr.weight_dfe,
    )
blended_canvas_dfe=cr.render_blended(
    image_arrays=image_arrays,  # ty:ignore[invalid-argument-type]
    canvas_relative_offsets=canvas_relative_offsets,
    canvas_extents=canvas_extents,
    weight=cr.weight_dfe,
    normalizer=normalizer
    )
blended_canvas_dfe+=np.repeat(255*(normalizer==0)[:,:,np.newaxis],repeats=3,axis=2) # Sets background to white as well.

alpha_image_arrays={
        "mis":np.repeat(logo_array[xy_mis[1]:xy_mis[1]+height,xy_mis[0]:xy_mis[0]+width,-1][:,:,np.newaxis],repeats=3,axis=2),
        "align":np.repeat(logo_array[xy_align[1]:xy_align[1]+height,xy_align[0]:xy_align[0]+width,-1][:,:,np.newaxis],repeats=3,axis=2)
    }
alpha_blended_canvas_dfe=cr.render_blended(
    image_arrays=alpha_image_arrays,  # ty:ignore[invalid-argument-type]
    canvas_relative_offsets=canvas_relative_offsets,
    canvas_extents=canvas_extents,
    weight=cr.weight_dfe,
    normalizer=normalizer
    )
combined_canvas=np.stack([
    np.asarray(blended_canvas_dfe)[:,:,0],
    np.asarray(blended_canvas_dfe)[:,:,1],
    np.asarray(blended_canvas_dfe)[:,:,2],
    np.asarray(alpha_blended_canvas_dfe)[:,:,0],
    ],axis=2)
plt.figure()
plt.imshow(combined_canvas)

for point in points:
    point_array=np.array([point,misalignment+point])
    plt.plot(point_array[:,0],point_array[:,1],marker=".",markersize=3,linestyle="--",linewidth=1)


plt.gca().set_axis_off()
plt.gca().set_aspect('equal', adjustable='box')
plt.tight_layout()
plt.gcf().set_size_inches(4, 4)
plt.savefig("misalign_logo/misalign_logo_r2.png",dpi=300,transparent=True)
plt.savefig("misalign_logo/misalign_logo_r2_small.png",dpi=75,transparent=True)
plt.ylim(1000,275)
plt.gcf().set_size_inches(4, 4*(750/1200))
plt.savefig("misalign_logo/misalign_logo_r2_wide.png",dpi=300,transparent=True)
```

```{code-cell} ipython3
misalignment=np.array([25,25])
```

#TODO make an all black and white variant that can be used for alpha channel setup.
#TODO make a "dark mode" variant.
