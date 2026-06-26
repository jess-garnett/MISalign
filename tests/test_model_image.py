from pathlib import Path
import numpy as np

from misalign.model.image import MISImage, MISImageFile, MISImageHDF5, setup_image

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
        assert str(test_image)=="Image 'test_image_a01.png' with shape:(1200, 1600, 3)"
    def test_image_save(self):
        test_img_a01="tests/test_files/model_image/test_image_a01.png"
        test_image_data={
            "image_type":"file",
            "image_filepath":test_img_a01,
        }
        test_image=MISImageFile(**test_image_data)
        assert test_image.for_json()=={"image_type":"file","image_filepath":test_img_a01,}
    def test_image_save_note(self):
        test_img_a01="tests/test_files/model_image/test_image_a01.png"
        test_image_data={
            "image_type":"file",
            "image_filepath":test_img_a01,
            "note":"Test Note"
        }
        test_image=MISImageFile(**test_image_data)
        assert test_image.for_json()=={"image_type":"file","image_filepath":test_img_a01,"note":"Test Note"}
    def test_image_save_change(self):
        test_img_a01="tests/test_files/model_image/test_image_a01.png"
        test_image_data={
            "image_type":"file",
            "image_filepath":test_img_a01,
        }
        change_test_img_a01="tests/test_files/model_image/test_image_a02.png"
        test_image=MISImageFile(**test_image_data)
        test_image.image_filepath=Path(change_test_img_a01)
        assert test_image.for_json()=={"image_type":"file","image_filepath":change_test_img_a01}
    def test_image_img_rect(self):
        test_img_a01="tests/test_files/model_image/test_image_a01.png"
        test_image_data={
            "image_type":"file",
            "image_filepath":test_img_a01,
        }
        test_image=MISImageFile(**test_image_data)
        test_img_arr_fp="tests/test_files/model_image/test_image_a01.npy"
        assert np.all(np.asarray(test_image)==np.load(test_img_arr_fp))

    #TODO add tests for `check_image_path` and `find_image_path`

class Test_setup_image():
    def test_setup_imagefile(self):
        assert type(setup_image(
            image_name="image_a01.jpg",
            hdf5_filepath="tests/test_files/test_hdf5/test-project_a-rel-cal-comp.hdf5",
            hdf5path="/MISContainer0/MISDataContainer0/image_a01.jpg",
            image_type="hdf5",
            PIL_mode="RGB"
        ))==MISImageHDF5

class TestMISImageHDF5():
    def test_protocol_isinstance(self):
        assert isinstance(MISImageHDF5,MISImage)
    def test_image_init(self):
        test_image_data=dict(
            image_name="image_a01.jpg",
            hdf5_filepath="tests/test_files/test_hdf5/test-project_a-rel-cal-comp.hdf5",
            hdf5path="/MISContainer0/MISDataContainer0/image_a01.jpg",
            image_type="hdf5",
            PIL_mode="RGB")
        test_image=MISImageHDF5(**test_image_data)
        assert str(test_image)=="Image 'image_a01.jpg' with shape:(1200, 1600, 3)"
    def test_image_save(self):
        test_image_data=dict(
            image_name="image_a01.jpg",
            hdf5_filepath="tests/test_files/test_hdf5/test-project_a-rel-cal-comp.hdf5",
            hdf5path="/MISContainer0/MISDataContainer0/image_a01.jpg",
            image_type="hdf5",
            PIL_mode="RGB")
        test_image=MISImageHDF5(**test_image_data)
        assert test_image.for_json()==dict(
            image_name="image_a01.jpg",
            hdf5_filepath="tests/test_files/test_hdf5/test-project_a-rel-cal-comp.hdf5",
            hdf5path="/MISContainer0/MISDataContainer0/image_a01.jpg",
            image_type="hdf5",
            PIL_mode="RGB")
    def test_image_save_note(self):
        test_image_data=dict(
            image_name="image_a01.jpg",
            hdf5_filepath="tests/test_files/test_hdf5/test-project_a-rel-cal-comp.hdf5",
            hdf5path="/MISContainer0/MISDataContainer0/image_a01.jpg",
            image_type="hdf5",
            PIL_mode="RGB",
            note="Test note")
        test_image=MISImageHDF5(**test_image_data)
        assert test_image.for_json()==dict(
            image_name="image_a01.jpg",
            hdf5_filepath="tests/test_files/test_hdf5/test-project_a-rel-cal-comp.hdf5",
            hdf5path="/MISContainer0/MISDataContainer0/image_a01.jpg",
            image_type="hdf5",
            PIL_mode="RGB",
            note="Test note")
    def test_image_save_change_filepath(self):
        test_image_data=dict(
            image_name="image_a01.jpg",
            hdf5_filepath="tests/test_files/test_hdf5/test-project_a-rel-cal-comp.hdf5",
            hdf5path="/MISContainer0/MISDataContainer0/image_a01.jpg",
            image_type="hdf5",
            PIL_mode="RGB")
        test_image=MISImageHDF5(**test_image_data)
        change_test_img_a01="tests/test_files/test_hdf5/test-project_a-rel-cal-comp-change.hdf5"
        test_image.hdf5_filepath=Path(change_test_img_a01)
        assert test_image.for_json()==dict(
            image_name="image_a01.jpg",
            hdf5_filepath="tests/test_files/test_hdf5/test-project_a-rel-cal-comp-change.hdf5",
            hdf5path="/MISContainer0/MISDataContainer0/image_a01.jpg",
            image_type="hdf5",
            PIL_mode="RGB")
    def test_image_img_rect(self):
        test_image_data=dict(
            image_name="image_a01.jpg",
            hdf5_filepath="tests/test_files/test_hdf5/test-project_a-rel-cal-comp.hdf5",
            hdf5path="/MISContainer0/MISDataContainer0/image_a01.jpg",
            image_type="hdf5",
            PIL_mode="RGB")
        test_image=MISImageHDF5(**test_image_data)
        test_img_arr_fp="tests/test_files/model_image/test_image_a01.npy"
        assert np.all(np.asarray(test_image)==np.load(test_img_arr_fp))