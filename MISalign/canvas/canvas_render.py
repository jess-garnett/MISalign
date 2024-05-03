""" Canvas Render
- Renders combined images.
"""
from PIL import Image as PILImage
# Rectangular Render
    # Uses solution from rectangular_solve

## Find Extents
    ### Image Sizes
def find_image_sizes(image_filepaths:dict) -> dict:
    """ Gets image size from a dictionary of image filepaths.
    - Takes a dictionary: {image_name:image_filepath}
    - Returns a dictionary of image sizes: {image_name:(width,height)}"""
    return {img_name:PILImage.open(img_fp).size for img_name,img_fp in image_filepaths.items()}
    ### Generate Points
def find_relative_extents(
        image_names:list,
        origin_relative_offsets:dict,
        image_sizes:dict):
    """ Gets minimum and maximum x and y extents relative to the origin.
    - Takes:
        - A list of image names
        - A dictionary of origin relative offsets {image_name:(x-offset,y-offset)}
        - A dictionary of image sizes: {image_name:(width,height)}
    - Returns a dictionary of origin relative extents with keys `minx`,`maxx`,`miny`, and `maxy`"""
    x=[]
    y=[]
    for img in image_names:
        img_corner=origin_relative_offsets[img] #top left corner
        img_size=image_sizes[img]
        x.append(-img_corner[0])#left side 
        x.append(-img_corner[0]+img_size[0])#right side
        y.append(img_corner[1])#top side
        y.append(img_corner[1]-img_size[1])#bottom side
        # Top to bottom is in the negative direction which is why the -img_size[1] is needed.
        #TODO make sure this is in-line with numpy coordinate system.
    origin_relative_extents=dict()
    origin_relative_extents["minx"]=min(x)
    origin_relative_extents["maxx"]=max(x)
    origin_relative_extents["miny"]=min(y)
    origin_relative_extents["maxy"]=max(y)
    return origin_relative_extents
    ### Resolve Extents

## Place In Canvas

## Rectangular Unblended Render

## Rectangular Blended Render

    ### Distance-From-Edge Weight

    ### Flat Weight

    ### Normalization Matrix Building
    
    ### Summation Blending