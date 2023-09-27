import pytest
from MISalign.model.image import Image
import numpy as np

class TestImage():
    def test_image_init(self):
        test_img_a01=r"example\data\set_a\a_myimages01.jpg"
        test_image=Image(test_img_a01)
        assert str(test_image)=="Image 'a_myimages01.jpg' with shape:(1200, 1600, 3)"
    def test_image_dfe_rect(self):
        test_img_a01=r"example\data\set_a\a_myimages01.jpg"
        test_image=Image(test_img_a01)
        test_dfe_arr_fp=r"example\expected_result\set_a\dfe_rectangular.npy"
        assert np.all(test_image.dfe_arr()==np.load(test_dfe_arr_fp))
    def test_image_img_rect(self):
        test_img_a01=r"example\data\set_a\a_myimages01.jpg"
        test_image=Image(test_img_a01)
        test_img_arr_fp=r"example\expected_result\set_a\img_a01.npy"
        assert np.all(test_image.img_arr()==np.load(test_img_arr_fp))