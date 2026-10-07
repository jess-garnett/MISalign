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

# Sample Data Ingest

```{code-cell} ipython3
prototyping_datafolder=r"C:\Users\drago\Box\p_MIS-MISalign\data_AlignCV"
```

```{code-cell} ipython3
from os import listdir,path
import pandas as pd
```

```{code-cell} ipython3
data_set=dict()
for datafolder in listdir(prototyping_datafolder):
    for sample in listdir(path.join(prototyping_datafolder,datafolder)):
        entry=dict()
        entry["dataset"]=datafolder
        entry["path"]=path.join(prototyping_datafolder,datafolder,sample)
        data_set[sample]=entry
df=pd.DataFrame(data_set).T
df
```

```{code-cell} ipython3
print(df.iloc[0].path)
display(df[df.dataset=="data_nov"])
```

# Image opening

```{code-cell} ipython3
from PIL import Image as PILImage
```

```{code-cell} ipython3
PILImage.open(df.iloc[0].path).show()
```

# Package Setups

+++

## OpenCV

```{code-cell} ipython3
# https://docs.opencv.org/4.x/d5/de5/tutorial_py_setup_in_windows.html
# https://pypi.org/project/opencv-python/#manual-builds
# %pip install opencv-python
import cv2 as cv
```

```{code-cell} ipython3
# https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html
# https://docs.opencv.org/4.x/db/d27/tutorial_py_table_of_contents_feature2d.html
```

### SIFT

```{code-cell} ipython3
# SIFT https://docs.opencv.org/4.x/da/df5/tutorial_py_sift_intro.html
import numpy as np
import cv2 as cv
 
img = cv.imread(df.iloc[0].path)
gray= cv.cvtColor(img,cv.COLOR_BGR2GRAY)
 
sift = cv.SIFT_create()
kp = sift.detect(gray,None)
 
# img=cv.drawKeypoints(gray,kp,img)
img=cv.drawKeypoints(gray,kp,img,flags=cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
 
# cv.imshow('sift_keypoints',img)
PILImage.fromarray(img).show()
# display(PILImage.fromarray(img))
```

```{code-cell} ipython3
kp,des = sift.compute(gray,kp)
display(des.shape)
```

### ORB

```{code-cell} ipython3
# https://docs.opencv.org/4.x/d1/d89/tutorial_py_orb.html
img = cv.imread(df.iloc[-2].path)
gray= cv.cvtColor(img,cv.COLOR_BGR2GRAY)

# Initiate ORB detector
orb = cv.ORB_create(nfeatures=500,edgeThreshold=5)
 
# find the keypoints with ORB
kp = orb.detect(gray,None)
 
# compute the descriptors with ORB
kp, des = orb.compute(gray, kp)
 
# draw only keypoints location,not size and orientation
# img2 = cv.drawKeypoints(gray, kp, None, color=(0,255,0), flags=0)
img2=cv.drawKeypoints(gray,kp,img,flags=cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
PILImage.fromarray(img2).show()
# PILImage.fromarray(img2).save("241210_ORB_sem3_nf500_et5.png")
```

```{code-cell} ipython3
display(des.shape)
```

### Matcher

```{code-cell} ipython3
# https://docs.opencv.org/4.x/dc/dc3/tutorial_py_matcher.html
```

#### Brute-Force Matching w/ ORB

```{code-cell} ipython3
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
 
img1 = cv.imread(df.iloc[0].path,cv.IMREAD_GRAYSCALE)          # queryImage
img2 = cv.imread(df.iloc[1].path,cv.IMREAD_GRAYSCALE) # trainImage
 
# Initiate ORB detector
orb = cv.ORB_create()
 
# find the keypoints and descriptors with ORB
kp1, des1 = orb.detectAndCompute(img1,None)
kp2, des2 = orb.detectAndCompute(img2,None)
```

```{code-cell} ipython3
# create BFMatcher object
bf = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)
 
# Match descriptors.
matches = bf.match(des1,des2)
 
# Sort them in the order of their distance.
matches = sorted(matches, key = lambda x:x.distance)
 
# Draw first 10 matches.
img3 = cv.drawMatches(img1,kp1,img2,kp2,matches[:10],None,flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
 
plt.imshow(img3)
plt.show()
```

```{code-cell} ipython3
kp2[matches[0].trainIdx].pt
kp1[matches[0].queryIdx].pt
```

```{code-cell} ipython3
for i,match in enumerate(matches[:]):
    train_pt=kp2[match.trainIdx].pt
    query_pt=kp1[match.queryIdx].pt
    x_offset=train_pt[0]-query_pt[0]
    y_offset=train_pt[1]-query_pt[1]
    # print([x_offset],[y_offset])
    # plt.plot([0,x_offset],[0,y_offset],alpha=0.1)
    plt.plot([x_offset],[y_offset],"o",alpha=0.05,markersize=20)
    if i<50:
        plt.plot([0,x_offset],[0,y_offset],alpha=0.05)
plt.xlim([-1200,1200])
plt.ylim([-800,800])
plt.title("Matches Visualized - all matches dots - top 50 matches lines - 0.05 alpha")
plt.show()
```

## SimpleCV

```{code-cell} ipython3
# Paused to focus on moving forward with OpenCV
```

## Scikit-Image

```{code-cell} ipython3
# Paused to focus on moving forward with OpenCV
```

# Set Processing

```{code-cell} ipython3
# set_df=df[df.dataset=="data_hdf"].copy() # 2x2 high distinct feature set
set_df=df[df.dataset=="data_sem"].copy() # 4x1 low overlap set
set_df
```

```{code-cell} ipython3
orb_data=dict()
for name,sample in set_df.iterrows():
    # print(sample)
    img = cv.imread(sample.path, cv.IMREAD_GRAYSCALE)
    orb = cv.ORB_create(edgeThreshold=5)
    kp, des = orb.detectAndCompute(img,None)
    orb_data[name]={"img":img,"kp":kp,"des":des}
orb_df=pd.DataFrame(orb_data).T
orb_df
```

```{code-cell} ipython3
from itertools import combinations
```

```{code-cell} ipython3
img_width=2560
img_height=1672
match_combs=combinations(set_df.index.to_list(),2)
# print(list(match_combs))
match_data=dict()
for m1,m2 in match_combs:
    print(m1,m2)
    bf = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)
    matches = bf.match(orb_df["des"][m1],orb_df["des"][m2])
    matches = sorted(matches, key = lambda x:x.distance)
    img3 = cv.drawMatches(orb_df["img"][m1],orb_df["kp"][m1],orb_df["img"][m2],orb_df["kp"][m2],matches[:10],None,flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    plt.imshow(img3)
    plt.savefig(f"241211_OCV_MOSet_{m1[7:11]}-{m2[10:11]}-matches.png",bbox_inches="tight",dpi=300)
    plt.show()
    for i,match in enumerate(matches[:]):
        train_pt=orb_df["kp"][m2][match.trainIdx].pt
        query_pt=orb_df["kp"][m1][match.queryIdx].pt
        x_offset=train_pt[0]-query_pt[0]
        y_offset=train_pt[1]-query_pt[1]
        plt.plot([x_offset],[y_offset],"o",alpha=0.05,markersize=20)
        if i<50:
            plt.plot([0,x_offset],[0,y_offset],alpha=0.05)
    plt.xlim([-img_width,img_width])
    plt.ylim([-img_height,img_height])
    plt.savefig(f"241211_OCV_MOSet_{m1[7:11]}-{m2[10:11]}-offsets.png",bbox_inches="tight")
    plt.show()
```

# Offset Determination

+++

## Prototyping
- lro2-3 for clean-defined
- lro0-2 for fuzzy rotated
- lro1-2 for similar feature but no match
- hdf0-2 for corner barely match
- hdf0-1 for clean-defined
- hdf1-3 for clean-defined
- lov2-3 for fuzzy match
- lov1-2 for fuzzy match
- ldf0-3 for clean match w/ noise
- ldf2-3 for clean match w/ noise

```{code-cell} ipython3
samples_short=["sem0","sem1","sem2","sem3","sem4","sem5"]#["lro0","lro1","lro2","lro3","hdf0","hdf1","hdf2","hdf3","lov1","lov2","lov3","ldf0","ldf2","ldf3"]
samples=pd.DataFrame([df[df.index.str.contains(x)].iloc[0] for x in samples_short])
samples
```

```{code-cell} ipython3
orb_data=dict()
for name,sample in samples.iterrows():
    # print(sample)
    img = cv.imread(sample.path, cv.IMREAD_GRAYSCALE)
    orb = cv.ORB_create(nfeatures=500,edgeThreshold=5)
    kp, des = orb.detectAndCompute(img,None)
    orb_data[name]={"img":img,"kp":kp,"des":des}
orb_df=pd.DataFrame(orb_data).T
orb_df
```

```{code-cell} ipython3
from scipy import ndimage
```

```{code-cell} ipython3
# match_combs=combinations(orb_df.index.to_list(),2)
# match_combs=(("lro2","lro3"),("lro0","lro2"),("lro1","lro2"),("hdf0","hdf2"),("hdf0","hdf1"),("hdf1","hdf3"),("lov2","lov3"),("lov1","lov2"),("ldf0","ldf3"),("ldf2","ldf3"))
# match_combs=(("sem0","sem1"),("sem2","sem3"),("sem3","sem4"),("sem4","sem5"),("sem3","sem5"))
match_combs=(("sem0","sem1"),("sem2","sem3"),("sem3","sem4"),("sem4","sem5"),("sem3","sem5"))
match_combs=[(df.index[df.index.str.contains(x[0])][0],df.index[df.index.str.contains(x[1])][0]) for x in match_combs]

match_combs
```

```{code-cell} ipython3
img_width=2560
img_height=1672
for m1,m2 in match_combs:
    bf = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)
    matches = bf.match(orb_df["des"][m1],orb_df["des"][m2])
    matches = sorted(matches, key = lambda x:x.distance)
    print([m.distance for m in matches])
    offset_grid=np.zeros((2*img_width,2*img_height),dtype=float) # change this to match 2x image distance.(3200,2400)
    for i,match in enumerate(matches[:]):
        train_pt=orb_df["kp"][m2][match.trainIdx].pt
        query_pt=orb_df["kp"][m1][match.queryIdx].pt
        x_offset_adj=int(train_pt[0]-query_pt[0]+img_width) #1600/1200 centers in numpy array/image.
        y_offset_adj=int(train_pt[1]-query_pt[1]+img_height)
        offset_grid[x_offset_adj,y_offset_adj]+=1000/(match.distance**2)
    offset_grid=ndimage.gaussian_filter(offset_grid,10)
    print(m1,m2,"Offset:",np.array(np.unravel_index(np.argmax(offset_grid),offset_grid.shape))-np.array([img_width,img_height]))
    plt.title(" ".join([m1,m2,str(tuple(np.array(np.unravel_index(np.argmax(offset_grid),offset_grid.shape))-np.array([img_width,img_height]))),f"{offset_grid.max():.5f}"]))
    plt.imshow(offset_grid.T)
    plt.colorbar()
    plt.savefig(f"241210_OffsetMap_{m1[7:11]}-{m2[10:11]}-offmap-1000imds-g10_nf500_et5.png",bbox_inches="tight",dpi=300)
    plt.show()
    # img3 = cv.drawMatches(orb_df["img"][m1],orb_df["kp"][m1],orb_df["img"][m2],orb_df["kp"][m2],matches[:10],None,flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    # plt.imshow(img3)
    # plt.savefig(f"240815_OCV_MOSet_{m1[7:11]}-{m2[10:11]}-matches.png",bbox_inches="tight",dpi=300)
    # plt.show()
    # for i,match in enumerate(matches[:]):
    #     train_pt=orb_df["kp"][m2][match.trainIdx].pt
    #     query_pt=orb_df["kp"][m1][match.queryIdx].pt
    #     x_offset=train_pt[0]-query_pt[0]
    #     y_offset=train_pt[1]-query_pt[1]
    #     plt.plot([x_offset],[y_offset],"o",alpha=0.05,markersize=20)
    #     if i<50:
    #         plt.plot([0,x_offset],[0,y_offset],alpha=0.05)
    # plt.xlim([-1600,1600])
    # plt.ylim([-1200,1200])
    # plt.savefig(f"240815_OCV_MOSet_{m1[7:11]}-{m2[10:11]}-offsets.png",bbox_inches="tight")
    # plt.show()
```

```{code-cell} ipython3
# testing way to get/compare local maxima. Code from `https://stackoverflow.com/questions/9111711/get-coordinates-of-local-maxima-in-2d-array-above-certain-value`
import numpy as np
import scipy.ndimage as ndimage
import matplotlib.pyplot as plt


neighborhood_size = 50
threshold = 0.0005

data = offset_grid.T

data_max = ndimage.maximum_filter(data, neighborhood_size)
maxima = (data == data_max)
data_min = ndimage.minimum_filter(data, neighborhood_size)
diff = ((data_max - data_min) > threshold)
maxima[diff == 0] = 0

labeled, num_objects = ndimage.label(maxima)
xy = np.array(ndimage.center_of_mass(data, labeled, range(1, num_objects+1)))

plt.imshow(data)

plt.autoscale(False)
plt.plot(xy[:, 1], xy[:, 0], 'rx')
```

# Non-array/blended match>offset

```{code-cell} ipython3
len(matches)
```

```{code-cell} ipython3
# image_from="sample_sem0.tif"
# image_to="sample_sem1.tif"
# sem 0 to sem 1: [48 1101] from offset map
# image_from="sample_sem3.tif"
# image_to="sample_sem5.tif"
# sem 3 to sem 5: No real relation
image_from="sample_sem3.tif"
image_to="sample_sem4.tif"
# 3>4 has distinct relation in offset map

matches = bf.match(orb_df["des"][image_from],orb_df["des"][image_to])
matches = sorted(matches, key = lambda x:x.distance)

pts_from=np.array([orb_df["kp"][image_from][match.queryIdx].pt for match in matches])
pts_to=np.array([orb_df["kp"][image_to][match.trainIdx].pt for match in matches])
```

```{code-cell} ipython3
eAP2D=cv.estimateAffinePartial2D(pts_from,pts_to)
```

```{code-cell} ipython3
print("X,Y:",eAP2D[0][:,2])
#cos^2 + sin^2 = 1 >> rotation/scale component of matrix =s^2
print("Rotation & Scale Matrix:",eAP2D[0][:,:2])
eAP2D_scalex=(eAP2D[0][0,0]**2+eAP2D[0][0,1]**2)**0.5
eAP2D_scaley=(eAP2D[0][1,1]**2+eAP2D[0][1,0]**2)**0.5
print("Scale X,Y:",[eAP2D_scalex,eAP2D_scaley])
eAP2D_rotation=np.arctan(eAP2D[0][0,1]/eAP2D[0][1,1])
print("Rotation(Rad/Deg):",eAP2D_rotation,"/",eAP2D_rotation*180/np.pi)
```

```{code-cell} ipython3
print("Inliers:",np.sum(eAP2D[1]))
for pt_from,pt_to,in_out in zip(pts_from,pts_to,eAP2D[1]):
    if in_out:
        print("X,Y:",pt_to[0]-pt_from[0],pt_to[1]-pt_from[1])
```

# Set implementation
Also grabbing all need coded/imports/etc.

```{code-cell} ipython3
import pandas as pd
import cv2 as cv
from math import dist
import numpy as np
from matplotlib import pyplot as plt
```

Run data import from first section to setup `df`

```{code-cell} ipython3
samples_short=["sem0","sem1","sem2","sem3","sem4","sem5"]#
# samples_short=["lro0","lro1","lro2","lro3","hdf0","hdf1","hdf2","hdf3","lov1","lov2","lov3","ldf0","ldf2","ldf3"]
samples=pd.DataFrame([df[df.index.str.contains(x)].iloc[0] for x in samples_short])
samples
```

```{code-cell} ipython3
# match_combs=combinations(orb_df.index.to_list(),2)
match_combs=(("sem0","sem1"),("sem2","sem3"),("sem3","sem4"),("sem4","sem5"),("sem3","sem5"))
# match_combs=(("lro2","lro3"),("lro0","lro2"),("lro1","lro2"),("hdf0","hdf2"),("hdf0","hdf1"),("hdf1","hdf3"),("lov2","lov3"),("lov1","lov2"),("ldf0","ldf3"),("ldf2","ldf3"))
# match_combs=(("lov2","lov3"),("lov1","lov2"),("ldf0","ldf3"))
match_combs=[(df.index[df.index.str.contains(x[0])][0],df.index[df.index.str.contains(x[1])][0]) for x in match_combs]
```

```{code-cell} ipython3
orb_data=dict()
for name,sample in samples.iterrows():
    # print(sample)
    img = cv.imread(sample.path, cv.IMREAD_GRAYSCALE)
    orb = cv.ORB_create(nfeatures=4000,edgeThreshold=5)
    kp, des = orb.detectAndCompute(img,None)
    orb_data[name]={"img":img,"kp":kp,"des":des}
orb_df=pd.DataFrame(orb_data).T
orb_df
```

```{code-cell} ipython3
match_refs={#values for offset from offsetmap
    ("sem0","sem1"):[48, 1101],
    ("sem2","sem3"):[84, 1192],
    ("sem3","sem4"):[14, 682],
    ("sem4","sem5"):[1,1558],
    ("sem3","sem5"):[673,-538]
}
```

```{code-cell} ipython3
from scipy import ndimage
```

```{code-cell} ipython3

```

```{code-cell} ipython3
for m1,m2 in match_combs:
    print(m1,m2)
    bf = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)
    
    matches = bf.match(orb_df["des"][m1],orb_df["des"][m2])
    matches = sorted(matches, key = lambda x:x.distance)
    matches = matches[:int(len(matches)*(1/8))]
    # matches = matches[:10]

    pts_from=np.array([orb_df["kp"][m1][match.queryIdx].pt for match in matches])
    pts_to=np.array([orb_df["kp"][m2][match.trainIdx].pt for match in matches])

    eAP2D=cv.estimateAffinePartial2D(pts_from,pts_to)

    eAP2D_translationx=eAP2D[0][0,2]
    eAP2D_translationy=eAP2D[0][1,2]
    print(f"X,Y:{eAP2D_translationx:0.1f}, {eAP2D_translationy:0.1f}")
    print("Rotation & Scale Matrix: \n",eAP2D[0][:,:2])
    eAP2D_scalex=(eAP2D[0][0,0]**2+eAP2D[0][0,1]**2)**0.5
    eAP2D_scaley=(eAP2D[0][1,1]**2+eAP2D[0][1,0]**2)**0.5
    print(f"Scale X,Y: {eAP2D_scalex:0.3f}, {eAP2D_scaley:0.3f}")
    eAP2D_rotation=np.arctan(eAP2D[0][0,1]/eAP2D[0][1,1])
    print(f"Rotation(Rad/Deg): {eAP2D_rotation:0.3f} /{eAP2D_rotation*180/np.pi:0.1f}")
    print("Inliers:",np.sum(eAP2D[1]))
    for pt_from,pt_to,in_out in zip(pts_from,pts_to,eAP2D[1]):
        if in_out:
            print(f"X,Y:{pt_from[0]-pt_to[0]:0.1f}, {pt_from[1]-pt_to[1]:0.1f}")
    
    distances_inlier=np.array([(i,match.distance) for i,(match,in_out) in enumerate(zip(matches,eAP2D[1])) if in_out])
    distances_outlier=np.array([(i,match.distance) for i,(match,in_out) in enumerate(zip(matches,eAP2D[1])) if not in_out])
    plt.figure()
    plt.plot(distances_inlier[:,0],distances_inlier[:,1],"gx")
    try:
        plt.plot(distances_outlier[:,0],distances_outlier[:,1],"r.")
    except IndexError:
        print("No Outliers")
    plt.xlabel("match index")
    plt.ylabel("match distance")
    plt.title(f"{m1}-{m2} in/out distances")
    plt.show()

    # ### Sanity check with offset map
    # img_width=1600#2560
    # img_height=1200#1672
    # offset_grid=np.zeros((2*img_width,2*img_height),dtype=float) # change this to match 2x image distance.(3200,2400)
    # for i,match in enumerate(matches[:]):
    #     train_pt=orb_df["kp"][m2][match.trainIdx].pt
    #     query_pt=orb_df["kp"][m1][match.queryIdx].pt
    #     x_offset_adj=int(train_pt[0]-query_pt[0]+img_width) #1600/1200 centers in numpy array/image.
    #     y_offset_adj=int(train_pt[1]-query_pt[1]+img_height)
    #     offset_grid[x_offset_adj,y_offset_adj]+=1000/(match.distance**2)
    # offset_grid=ndimage.gaussian_filter(offset_grid,10)
    # print(m1,m2,"Offset:",np.array(np.unravel_index(np.argmax(offset_grid),offset_grid.shape))-np.array([img_width,img_height]))
    # plt.title(" ".join([m1,m2,str(tuple(np.array(np.unravel_index(np.argmax(offset_grid),offset_grid.shape))-np.array([img_width,img_height]))),f"{offset_grid.max():.5f}"]))
    # plt.imshow(offset_grid.T)
    # plt.colorbar()
    # # plt.savefig(f"241210_OffsetMap_{m1[7:11]}-{m2[10:11]}-offmap-1000imds-g10_nf500_et5.png",bbox_inches="tight",dpi=300)
    # plt.show()
    # match_refs[(m1[7:11],m2[7:11])]=list(np.array(np.unravel_index(np.argmax(offset_grid),offset_grid.shape))-np.array([img_width,img_height]))
    # ###

    top10_offsets=np.array([(pt_to[0]-pt_from[0],pt_to[1]-pt_from[1]) for pt_from,pt_to in zip(pts_from[:int(len(matches)*(1/10))],pts_to[:int(len(matches)*(1/10))])])
    top50_offsets=np.array([(pt_to[0]-pt_from[0],pt_to[1]-pt_from[1]) for pt_from,pt_to in zip(pts_from[int(len(matches)*(1/10)):int(len(matches)*(1/2))],pts_to[int(len(matches)*(1/10)):int(len(matches)*(1/2))])])
    remaining_offsets=np.array([(pt_to[0]-pt_from[0],pt_to[1]-pt_from[1]) for pt_from,pt_to in zip(pts_from[int(len(matches)*(1/2)):],pts_to[int(len(matches)*(1/2)):])])
    plt.figure()
    plt.plot(top10_offsets[:,0],top10_offsets[:,1],"gx",alpha=0.1)
    plt.plot(top50_offsets[:,0],top50_offsets[:,1],"yx",alpha=0.1)
    plt.plot(remaining_offsets[:,0],remaining_offsets[:,1],"rx",alpha=0.1)
    plt.xlabel("x offset")
    plt.ylabel("y offset")
    plt.title(f"{m1}-{m2} match offsets top 10%/top 50%/remaining")
    plt.show()


    distances_metric_ref=np.array([(dist((pt_to[0]-pt_from[0],pt_to[1]-pt_from[1]),match_refs[(m1[7:11],m2[7:11])]),match.distance) for match,pt_from,pt_to in zip(matches,pts_from,pts_to)])
    plt.figure()
    plt.plot(distances_metric_ref[:,0],distances_metric_ref[:,1],"x")
    plt.xlabel("ref distance")
    plt.ylabel("match distance")
    plt.xscale("log")
    plt.title(f"{m1}-{m2} ref/match distances")
    plt.show()



    # plt.title(" ".join([m1,m2,str(tuple(np.array(np.unravel_index(np.argmax(offset_grid),offset_grid.shape))-np.array([img_width,img_height]))),f"{offset_grid.max():.5f}"]))
    # plt.imshow(offset_grid.T)
    # plt.colorbar()
    # plt.savefig(f"241210_OffsetMap_{m1[7:11]}-{m2[10:11]}-offmap-1000imds-g10_nf500_et5.png",bbox_inches="tight",dpi=300)
    # plt.show()
```

# Functionalizing process

```{code-cell} ipython3
import pandas as pd
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
```

```{code-cell} ipython3
from os.path import abspath
from sys import path
path.insert(0, abspath("../.."))  # Repository directory relative to this file.
from MISalign.model.mis_file import MisFile,load_mis
from MISalign.model.relation import Relation
```

```{code-cell} ipython3
mis_filepath=r"..\\..\example\data\set_a\mymis_calibrated.mis"
mis_project=load_mis(mis_filepath)
```

```{code-cell} ipython3
mis_project.get_image_paths()
```

```{code-cell} ipython3
list(mis_project.get_image_paths().keys())
```

```{code-cell} ipython3
class ImageManager():
    def __init__(self,image_names_paths:dict):
        self.image_dict={name:{"path":filepath} for name,filepath in image_names_paths.items()}
    
    def get_names(self)->list[str]:
        return list(self.image_dict.keys())
    def get_path(self,name:str)->str:
        return self.image_dict[name]["path"]
    def lookup_name(self,short_name:str)->str:
        name_matches=[name for name in self.image_dict.keys() if short_name in name]
        if len(name_matches)==1:
            return name_matches
        elif len(name_matches)==0:
            raise ValueError(f"short_name '{short_name}' matched no image names.")
        elif len(name_matches)>1:
            raise ValueError(f"short_name '{short_name}' matched {len(name_matches)} image names: {name_matches}")

class ORBManager():
    def __init__(self,
            ImageM:ImageManager,
            precompute_default=True,
            store_compute=True,
            default_ORB_parameters={"nfeatures":500,"edgeThreshold":5}):
        self.ImageM=ImageM
        self.default_ORB_parameters=default_ORB_parameters
        self.store_compute=store_compute
        if store_compute:
            self.computed=dict()
            if precompute_default:
                for image_name in ImageM.get_names():
                    self.computed[image_name]=dict()
                    self.computed[image_name][self.get_parameter_hashable(default_ORB_parameters)]=self.compute_orb(image_name,default_ORB_parameters)

    def compute_orb(self,image_name,ORB_parameters):
        img = cv.imread(self.ImageM.get_path(image_name), cv.IMREAD_GRAYSCALE)
        orb = cv.ORB_create(**ORB_parameters)
        kp, des = orb.detectAndCompute(img,None)
        return {"kp":kp,"des":des}
    def get_parameter_hashable(self,ORB_parameters:dict)->tuple:
        return tuple((k,ORB_parameters[k]) for k in sorted(ORB_parameters))
    def get_orb(self,image_name,ORB_parameters=None):
        if ORB_parameters is None:
            ORB_parameters=self.default_ORB_parameters
        ORB_parameter_hashable=self.get_parameter_hashable(ORB_parameters)
        if self.store_compute:
            if image_name in self.computed.keys():
                if ORB_parameter_hashable in self.computed[image_name].keys():
                    return self.computed[image_name][ORB_parameter_hashable]
            else:
                self.computed[image_name]=dict()
        computed_orb=self.compute_orb(image_name,ORB_parameters)
        if self.store_compute:
            self.computed[image_name][ORB_parameter_hashable]=computed_orb
        return computed_orb

def generate_match_combinations(strategy,**kwargs)-> list[list]: 
    if strategy=="order":
        return generate_match_combinations_in_order(kwargs["order"])
    elif strategy=="short_pairs":
        return generate_match_combinations_from_short_pairs(kwargs["short_pairs"],kwargs["short_lookup"])
    elif strategy=="all":
        return generate_match_combinations_all_combinations(kwargs["all"])
    elif strategy=="search":
        return generate_match_combinations_all_combinations(kwargs["search"],kwargs["all"])
    else:
        raise ValueError(f"'{strategy}' is not a valid strategy.")
def generate_match_combinations_in_order(order:list):
    return [[a,b] for a,b in zip(order[:-1],order[1:])]
def generate_match_combinations_from_short_pairs(short_pairs:list[list],short_lookup:ImageManager.lookup_name):
    pass #TODO
def generate_match_combinations_all_combinations(items:list):
    pass #TODO
def generate_match_combinations_search(search:str,items:list):
    pass #TODO

def generate_match_bf(
        image1:str,
        image2:str,
        match_reduction_ratio:float,
        OrbM:ORBManager,
        ORB_parameters:dict=None)->list[cv.DMatch]:
    brute_force_matcher = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)
    orb1=OrbM.get_orb(image1,ORB_parameters)
    orb2=OrbM.get_orb(image2,ORB_parameters)
    matches = brute_force_matcher.match(orb1["des"],orb2["des"])
    sorted_matches = sorted(matches, key = lambda x:x.distance)
    reduced_matches = matches[:int(len(sorted_matches)*(match_reduction_ratio))]
    return reduced_matches,orb1,orb2

def estimate_translation(
        matches,
        orb1,
        orb2,
        limit_affine_rotation=0.01, #maximum affine rotation without correction i.e. -0.01rad to +0.01rad rotations are acceptable.
        limit_affine_scale=0.01, #maximum affine scale without correction i.e. 0.99 scale to 1.01 scale are acceptable.
        limit_minimum_points=5, #minimum number of matched points for succesful translation estimate.
        limit_inlier_consistency=0.5 #minimum fraction of matched points that must be consistent
    )->list[list,bool]:
    
    pts_1=np.array([orb1["kp"][match.queryIdx].pt for match in matches])
    pts_2=np.array([orb2["kp"][match.trainIdx].pt for match in matches])
    eAP2D_matrix,eAP2D_in_out=cv.estimateAffinePartial2D(pts_1,pts_2)

    eAP2D_translationx=eAP2D_matrix[0,2]
    eAP2D_translationy=eAP2D_matrix[1,2]
    # print(f"X,Y:{eAP2D_translationx:0.1f}, {eAP2D_translationy:0.1f}")
    # print("Rotation & Scale Matrix: \n",eAP2D_matrix[:,:2])
    eAP2D_scalex=(eAP2D_matrix[0,0]**2+eAP2D_matrix[0,1]**2)**0.5
    eAP2D_scaley=(eAP2D_matrix[1,1]**2+eAP2D_matrix[1,0]**2)**0.5
    # print(f"Scale X,Y: {eAP2D_scalex:0.3f}, {eAP2D_scaley:0.3f}")
    eAP2D_rotation=np.arctan(eAP2D_matrix[0,1]/eAP2D_matrix[1,1])
    # print(f"Rotation(Rad/Deg): {eAP2D_rotation:0.3f} /{eAP2D_rotation*180/np.pi:0.1f}")
    # print("Inliers:",np.sum(eAP2D[1]))
    eAP2D_inliers=[(tuple(pt1),tuple(pt2)) for pt1,pt2,in_out in zip(pts_1,pts_2,eAP2D_in_out) if in_out]
    eAP2D_inliers_count=len(eAP2D_inliers)
    # for pt_from,pt_to,in_out in zip(pts_from,pts_to,eAP2D[1]):
    #     if in_out:
    #         print(f"X,Y:{pt_from[0]-pt_to[0]:0.1f}, {pt_from[1]-pt_to[1]:0.1f}")
    #TODO verify based on limits
    valid={"overall":True,"individual":[True for match in eAP2D_inliers]}
    return eAP2D_inliers, valid


class AlignCVManager():
    def __init__(self,ImageM:ImageManager,OrbM:ORBManager):
        self.ImageM=ImageM
        self.OrbM=OrbM
        self.alignments=[]
    def run_alignment(self,match_combinations,match_reduction_ratio=1/2,ORB_parameters=None):
        alignment_data={"alignment_parameters":{"match_combinations":match_combinations,"match_reduction_ratio":match_reduction_ratio,"ORB_parameters":ORB_parameters},"alignment_data":dict()}
        for image1,image2 in match_combinations:
            image_set=(image1,image2)
            matches,orb1,orb2=generate_match_bf(
                image1=image1,
                image2=image2,
                match_reduction_ratio=match_reduction_ratio,
                OrbM=self.OrbM,
                ORB_parameters=ORB_parameters
                )
            estimated_translation_inliers, estimated_translation_validity = estimate_translation(matches,orb1,orb2)
            alignment_data["alignment_data"][image_set]={
                "matches":matches,
                "estimated_translation_inliers":estimated_translation_inliers,
                "estimated_translation_validity":estimated_translation_validity
                }
        self.alignments.append(alignment_data)
        return len(self.alignments)-1
    def get_alignment(self,alignment_id):
        return self.alignments[alignment_id]
    #TODO valid results to mis
    #TODO merging valid results
    def update_mis(self,
            mis_project:MisFile,
            alignment_id,
            valid_only=True)->MisFile:
        alignment_results=self.alignments[alignment_id]
        match_combinations=alignment_results["alignment_parameters"]["match_combinations"]
        for mc in match_combinations:
            mc_alignment_result=alignment_results["alignment_data"][tuple(mc)]
            if valid_only and not mc_alignment_result["estimated_translation_validity"]["overall"]:
                print(f"Warning: Match {mc} not valid. No relation saved.")
                continue
            mis_project._relations.append(Relation(
                mc[0],
                mc[1],
                'p',
                [([int(x) for x in pt1],[int(x) for x in pt2]) for (pt1,pt2),individual_valid in zip(mc_alignment_result['estimated_translation_inliers'],mc_alignment_result["estimated_translation_validity"]["individual"])] ))

```

```{code-cell} ipython3
ImageM=ImageManager(mis_project.get_image_paths())

OrbM=ORBManager(ImageM,default_ORB_parameters={"nfeatures": 2000,"edgeThreshold": 5 })

AlignCVM=AlignCVManager(ImageM,OrbM)

match_combinations=generate_match_combinations(strategy="order",order=sorted(mis_project.get_image_names()))

alignment_id=AlignCVM.run_alignment(match_combinations)
alignment_result=AlignCVM.get_alignment(alignment_id)
```

```{code-cell} ipython3
# len(alignment_result["alignment_data"][tuple(match_combinations[0])]["estimated_translation_validity"]["individual"])
# len(alignment_result["alignment_data"][tuple(match_combinations[0])]['estimated_translation_inliers'])
```

```{code-cell} ipython3
match_combinations
```

```{code-cell} ipython3
for mc in match_combinations:
    print([(int(pt1[0]-pt2[0]),int(pt1[1]-pt2[1])) for pt1,pt2 in alignment_result["alignment_data"][tuple(mc)]['estimated_translation_inliers']])
for mc in match_combinations:
    print([(list(pt1),list(pt2)) for pt1,pt2 in alignment_result["alignment_data"][tuple(mc)]['estimated_translation_inliers']])
```

```{code-cell} ipython3
mis_project.get_rels("r")
```

```{code-cell} ipython3
mis_project_copy=load_mis(mis_filepath)
mis_project_copy._relations=[]
# for mc in match_combinations:
#     mis_project_copy._relations.append(Relation(
#         mc[0],
#         mc[1],
#         'p',
#         [([int(x) for x in pt1],[int(x) for x in pt2]) for pt1,pt2 in alignment_result["alignment_data"][tuple(mc)]['estimated_translation_inliers']]))
AlignCVM.update_mis(mis_project_copy,alignment_id)
#TODO add an update relation option?
mis_project_copy.get_rels("r")
```

# Module setup

```{code-cell} ipython3
from os.path import abspath
from sys import path
path.insert(0, abspath("../.."))  # Repository directory relative to this file.
from MISalign.model.mis_file import load_mis,save_mis
from MISalign.alignment.align_cv import ImageManager, ORBManager, AlignCVManager, generate_match_combinations
```

```{code-cell} ipython3
mis_filepath=r"..\\..\example\data\set_a\mymis_calibrated.mis"
mis_project=load_mis(mis_filepath)
```

```{code-cell} ipython3
ImageM=ImageManager(mis_project.get_image_paths())

OrbM=ORBManager(ImageM,default_ORB_parameters={"nfeatures": 500,"edgeThreshold": 5 })

AlignCVM=AlignCVManager(ImageM,OrbM)

match_combinations=generate_match_combinations(strategy="order",order=sorted(mis_project.get_image_names()))

alignment_id=AlignCVM.run_alignment(match_combinations)
alignment_result=AlignCVM.get_alignment(alignment_id)
print(alignment_result)
```

```{code-cell} ipython3
mis_project_copy=load_mis(mis_filepath)
mis_project_copy._relations=[]

AlignCVM.update_mis(mis_project_copy,alignment_id)
#TODO add an update relation option?
print("Prior Alignments")
display(mis_project.get_rels("r"))
print("Computer Vision Alignments")
display(mis_project_copy.get_rels("r"))
```

```{code-cell} ipython3
# save_mis(r"..\\..\example\data\set_a\mymis_aligncv.mis",mis_project_copy)
```

```{code-cell} ipython3
parameter_progression_step=1
alignment_id1=AlignCVM.run_alignment(AlignCVM.get_invalid_match_combinations(alignment_id),**AlignCVM.alignment_parameter_progression(step=parameter_progression_step))
print(AlignCVM.get_invalid_match_combinations(alignment_id1))
alignment_result1=AlignCVM.get_alignment(alignment_id1)
print(alignment_result1)
```

```{code-cell} ipython3
parameter_progression_step=2
alignment_id2=AlignCVM.run_alignment(AlignCVM.get_invalid_match_combinations(alignment_id1),**AlignCVM.alignment_parameter_progression(step=parameter_progression_step))
print(AlignCVM.get_invalid_match_combinations(alignment_id2))
alignment_result2=AlignCVM.get_alignment(alignment_id2)
print(alignment_result2)
```

```{code-cell} ipython3
alignment_id_0_2=AlignCVM.merge_alignments([alignment_id,alignment_id2])
print(AlignCVM.get_invalid_match_combinations(alignment_id_0_2))
```

```{code-cell} ipython3
mis_project_copy=load_mis(mis_filepath)
mis_project_copy._relations=[]

AlignCVM.update_mis(mis_project_copy,alignment_id_0_2)
#TODO add an update relation option?
print("Prior Alignments")
display(mis_project.get_rels("r"))
print("Computer Vision Alignments")
display(sorted(mis_project_copy.get_rels("r")))
```
