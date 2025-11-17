import pytest
from MISalign.model.image import Image, MISImage, MISImageFile, Path, setup_image
import numpy as np

class TestImage():
    def test_image_init(self):
        test_img_a01=r"example\data\set_a\a_myimages01.jpg"
        test_image=Image(test_img_a01)
        assert str(test_image)=="Image 'a_myimages01.jpg' with shape:(1600, 1200)"
    # def test_image_dfe_rect(self):
    #     test_img_a01=r"example\data\set_a\a_myimages01.jpg"
    #     test_image=Image(test_img_a01)
    #     test_dfe_arr_fp=r"example\expected_result\set_a\dfe_rectangular.npy"
    #     assert np.all(test_image.dfe_arr()==np.load(test_dfe_arr_fp))
    def test_image_img_rect(self):
        test_img_a01=r"example\data\set_a\a_myimages01.jpg"
        test_image=Image(test_img_a01)
        test_img_arr_fp=r"example\expected_result\set_a\img_a01.npy"
        assert np.all(test_image.img_arr()==np.load(test_img_arr_fp))

#TODO makes tests based on `test_files` not on examples.
class Test_setup_image():
    def test_setup_imagefile(self):
        assert type(setup_image(
            image_type="file",
            image_filepath=r"example\data\set_a\a_myimages01.jpg"
        ))==MISImageFile

class TestMISImageFile():
    def test_protocol_isinstance(self):
        assert isinstance(MISImageFile,MISImage)
    def test_image_init(self):
        test_img_a01=r"example\data\set_a\a_myimages01.jpg"
        test_image_data={
            "image_type":"file",
            "image_filepath":test_img_a01,

        }
        test_image=MISImageFile(**test_image_data)
        assert str(test_image)=="Image 'a_myimages01.jpg' with shape:(1600, 1200)"
    def test_image_save(self):
        test_img_a01=r"example\data\set_a\a_myimages01.jpg"
        test_image_data={
            "image_type":"file",
            "image_filepath":test_img_a01,
        }
        test_image=MISImageFile(**test_image_data)
        assert test_image.save_dict()=={"image_type":"file","image_filepath":test_img_a01,}
    def test_image_save_note(self):
        test_img_a01=r"example\data\set_a\a_myimages01.jpg"
        test_image_data={
            "image_type":"file",
            "image_filepath":test_img_a01,
            "note":"Test Note"
        }
        test_image=MISImageFile(**test_image_data)
        assert test_image.save_dict()=={"image_type":"file","image_filepath":test_img_a01,"note":"Test Note"}
    def test_image_save_change(self):
        test_img_a01=r"example\data\set_a\a_myimages01.jpg"
        test_image_data={
            "image_type":"file",
            "image_filepath":test_img_a01,
        }
        change_test_img_a01=r"example\data\a_myimages01.jpg"
        test_image=MISImageFile(**test_image_data)
        test_image.image_filepath=Path(change_test_img_a01)
        assert test_image.save_dict()=={"image_type":"file","image_filepath":change_test_img_a01}
    def test_image_img_rect(self):
        test_img_a01=r"example\data\set_a\a_myimages01.jpg"
        test_image_data={
            "image_type":"file",
            "image_filepath":test_img_a01,
        }
        test_image=MISImageFile(**test_image_data)
        test_img_arr_fp=r"example\expected_result\set_a\img_a01.npy"
        assert np.all(test_image.get_image_array()==np.load(test_img_arr_fp))