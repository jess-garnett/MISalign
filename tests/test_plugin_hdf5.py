from MISalign.plugin.hdf5 import MISProjectHDF5, MISImageHDF5,load_mis_project_hdf5
from MISalign.model.project import MISProject
from MISalign.model.image import MISImage, setup_image
from pathlib import Path
import numpy as np

class TestMISProjectHDF5():
    # def test_protocol_isinstance(self):
    #     assert isinstance(MISProjectHDF5,MISProject)
    def test_load_str(self):
        test_filepath="tests/test_files/plugin_hdf5/mytestfile1.hdf5"
        mp=load_mis_project_hdf5(test_filepath)
        expected_result=f"""A MISalign project with:
Images:
    a_myimages01.jpg
    a_myimages02.jpg
    a_myimages03.jpg
Relations:
    ('a_myimages01.jpg', 'a_myimages02.jpg')
    ('a_myimages02.jpg', 'a_myimages03.jpg')
Calibration:
    pixel : 599.006361608906
    length : 1
    length_unit : mm
Project Path:
    {Path(test_filepath)}"""
        assert str(mp)==expected_result

class Test_setup_image():
    def test_setup_imagefile(self):
        assert type(setup_image(
            image_name="a_myimages01.jpg",
            hdf5_filepath="tests/test_files/plugin_hdf5/mytestfile1.hdf5",
            image_type="hdf5",
            PIL_mode="RGB"
        ))==MISImageHDF5

class TestMISImageHDF5():
    def test_protocol_isinstance(self):
        assert isinstance(MISImageHDF5,MISImage)
    def test_image_init(self):
        test_image_data=dict(
            image_name="a_myimages01.jpg",
            hdf5_filepath="tests/test_files/plugin_hdf5/mytestfile1.hdf5",
            image_type="hdf5",
            PIL_mode="RGB")
        test_image=MISImageHDF5(**test_image_data)
        assert str(test_image)=="Image 'a_myimages01.jpg' with shape:(1600, 1200)"
    def test_image_save(self):
        test_image_data=dict(
            image_name="a_myimages01.jpg",
            hdf5_filepath="tests/test_files/plugin_hdf5/mytestfile1.hdf5",
            image_type="hdf5",
            PIL_mode="RGB")
        test_image=MISImageHDF5(**test_image_data)
        assert test_image.save_dict()==dict(
            image_name="a_myimages01.jpg",
            hdf5_filepath="tests/test_files/plugin_hdf5/mytestfile1.hdf5",
            image_type="hdf5",
            PIL_mode="RGB")
    def test_image_save_note(self):
        test_image_data=dict(
            image_name="a_myimages01.jpg",
            hdf5_filepath="tests/test_files/plugin_hdf5/mytestfile1.hdf5",
            image_type="hdf5",
            PIL_mode="RGB",
            note="Test note")
        test_image=MISImageHDF5(**test_image_data)
        assert test_image.save_dict()==dict(
            image_name="a_myimages01.jpg",
            hdf5_filepath="tests/test_files/plugin_hdf5/mytestfile1.hdf5",
            image_type="hdf5",
            PIL_mode="RGB",
            note="Test note")
    def test_image_save_change(self):
        test_image_data=dict(
            image_name="a_myimages01.jpg",
            hdf5_filepath="tests/test_files/plugin_hdf5/mytestfile1.hdf5",
            image_type="hdf5",
            PIL_mode="RGB")
        test_image=MISImageHDF5(**test_image_data)
        change_test_img_a01="tests/test_files/plugin_hdf5/mytestfile2.hdf5"
        test_image.hdf5_filepath=Path(change_test_img_a01)
        assert test_image.save_dict()==dict(
            image_name="a_myimages01.jpg",
            hdf5_filepath="tests/test_files/plugin_hdf5/mytestfile2.hdf5",
            image_type="hdf5",
            PIL_mode="RGB")
    def test_image_img_rect(self):
        test_image_data=dict(
            image_name="a_myimages01.jpg",
            hdf5_filepath="tests/test_files/plugin_hdf5/mytestfile1.hdf5",
            image_type="hdf5",
            PIL_mode="RGB")
        test_image=MISImageHDF5(**test_image_data)
        test_img_arr_fp="tests/test_files/model_image/test_image_a01.npy"
        assert np.all(test_image.get_image_array()==np.load(test_img_arr_fp))