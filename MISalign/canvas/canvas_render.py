""" Canvas Render
- Renders combined images.
"""
from PIL import Image as PILImage
# Rectangular Render
    # Uses solution from rectangular_solve

## Find Extents
    ### Image Sizes
def find_image_size(image_filepaths:dict) -> dict:
    """ Gets image size from a dictionary of image filepaths.
    - Takes a dictionary: {image_name:image_filepath}
    - Returns a dictionary of image sizes: {image_name:(width,height)}"""
    return {img_name:PILImage.open(img_fp).size for img_name,img_fp in image_filepaths.items()}
    ### Generate Points

    ### Resolve Extents

## Place In Canvas

## Rectangular Unblended Render

## Rectangular Blended Render

    ### Distance-From-Edge Weight

    ### Flat Weight

    ### Normalization Matrix Building
    
    ### Summation Blending