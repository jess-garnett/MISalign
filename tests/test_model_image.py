import pytest
from MISalign.model.image import Image, MISImage, MISImageFile, Path, setup_image
import numpy as np

class Test_setup_image():
    def test_setup_imagefile(self):
        assert type(setup_image(
            image_type="file",
            image_filepath="tests/test_files/model_image/test_image_a01.png"
        ))==MISImageFile

class TestMISImageFile():
    def test_protocol_isinstance(self):
        assert isinstance(MISImageFile,MISImage)
    def test_image_init(self):
        test_img_a01="tests/test_files/model_image/test_image_a01.png"
        test_image_data={
            "image_type":"file",
            "image_filepath":test_img_a01,

        }
        test_image=MISImageFile(**test_image_data)
        assert str(test_image)=="Image 'test_image_a01.png' with shape:(1600, 1200)"
    def test_image_save(self):
        test_img_a01="tests/test_files/model_image/test_image_a01.png"
        test_image_data={
            "image_type":"file",
            "image_filepath":test_img_a01,
        }
        test_image=MISImageFile(**test_image_data)
        assert test_image.save_dict()=={"image_type":"file","image_filepath":test_img_a01,}
    def test_image_save_note(self):
        test_img_a01="tests/test_files/model_image/test_image_a01.png"
        test_image_data={
            "image_type":"file",
            "image_filepath":test_img_a01,
            "note":"Test Note"
        }
        test_image=MISImageFile(**test_image_data)
        assert test_image.save_dict()=={"image_type":"file","image_filepath":test_img_a01,"note":"Test Note"}
    def test_image_save_change(self):
        test_img_a01="tests/test_files/model_image/test_image_a01.png"
        test_image_data={
            "image_type":"file",
            "image_filepath":test_img_a01,
        }
        change_test_img_a01="tests/test_files/model_image/test_image_a02.png"
        test_image=MISImageFile(**test_image_data)
        test_image.image_filepath=Path(change_test_img_a01)
        assert test_image.save_dict()=={"image_type":"file","image_filepath":change_test_img_a01}
    def test_image_img_rect(self):
        test_img_a01="tests/test_files/model_image/test_image_a01.png"
        test_image_data={
            "image_type":"file",
            "image_filepath":test_img_a01,
        }
        test_image=MISImageFile(**test_image_data)
        test_img_arr_fp="tests/test_files/model_image/test_image_a01.npy"
        assert np.all(test_image.get_image_array()==np.load(test_img_arr_fp))

    #TODO add tests for filepath checking.