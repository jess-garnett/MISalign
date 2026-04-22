from MISalign.model.project import MISProjectJSON
import MISalign.canvas.canvas_rectangular as cr
import numpy as np

class TestSolveRender():
    def test_vertical(self):
        reference_image_path="tests/test_files/canvas_rectangular/test_image_a01.npy"
        reference_image=np.load(reference_image_path)
        mis_filepath="tests/test_files/canvas_rectangular/test_project_a01_v.json"
        mis_project=MISProjectJSON.load(mis_filepath)
        origin=mis_project.get_image_names()[0]
        origin_relative_offsets=cr.rectangular_solve(
            relations=mis_project.get_relations(),
            image_names=mis_project.get_image_names(),
            origin=origin
        )
        origin_relative_extents=cr.find_relative_extents_project(
            project=mis_project,
            origin_relative_offsets=origin_relative_offsets,)
        canvas_extents, canvas_offsets=cr.resolve_extents(origin_relative_extents)
        canvas_relative_offsets=cr.place_in_canvas(
            image_names=mis_project.get_image_names(),
            origin_relative_offsets=origin_relative_offsets,
            canvas_extents=canvas_extents,
            canvas_offsets=canvas_offsets)
        unblended_canvas=cr.render_unblended(
            project=mis_project,
            canvas_relative_offsets=canvas_relative_offsets,
            canvas_extents=canvas_extents)
        assert np.all(np.asarray(unblended_canvas)==reference_image) # all pixels perfectly match their reference value in the unblended image
        dfe_normalizer=cr.build_normalization(
            project=mis_project,
            canvas_relative_offsets=canvas_relative_offsets,
            canvas_extents=canvas_extents,
            weight=cr.weight_dfe)
        blended_canvas_dfe=cr.render_blended(
            project=mis_project,
            canvas_relative_offsets=canvas_relative_offsets,
            canvas_extents=canvas_extents,
            weight=cr.weight_dfe,
            normalizer=dfe_normalizer)
        # print(np.max(np.asarray(blended_canvas_dfe)-reference_image))
        # print(np.min(np.asarray(blended_canvas_dfe)-reference_image))
        # print(np.unique(np.asarray(blended_canvas_dfe,dtype=np.int16)-reference_image,return_counts=True))
        # focus_slice=(slice(550,650),slice(0,200))
        # cr.PILImage.fromarray(np.asarray(blended_canvas_dfe)[focus_slice]).save("tests/test_files/canvas_rectangular/test_results/vertical_blended.png")
        # cr.PILImage.fromarray(reference_image[focus_slice]).save("tests/test_files/canvas_rectangular/test_results/vertical_reference.png")
        # cr.PILImage.fromarray(np.abs(np.asarray(blended_canvas_dfe,dtype=np.int16)-reference_image).astype(np.uint8)[focus_slice]).save("tests/test_files/canvas_rectangular/test_results/vertical_blended_diff.png")
        assert np.all(np.abs(np.asarray(blended_canvas_dfe,dtype=np.int16)-reference_image)<=1) # all pixels are within 1 of their reference value in the blended image
    def test_horizontal(self):
        reference_image_path="tests/test_files/canvas_rectangular/test_image_a01.npy"
        reference_image=np.load(reference_image_path)
        mis_filepath="tests/test_files/canvas_rectangular/test_project_a01_h.json"
        mis_project=MISProjectJSON.load(mis_filepath)
        origin=mis_project.get_image_names()[0]
        origin_relative_offsets=cr.rectangular_solve(
            relations=mis_project.get_relations(),
            image_names=mis_project.get_image_names(),
            origin=origin
        )
        origin_relative_extents=cr.find_relative_extents_project(
            project=mis_project,
            origin_relative_offsets=origin_relative_offsets,)
        canvas_extents, canvas_offsets=cr.resolve_extents(origin_relative_extents)
        canvas_relative_offsets=cr.place_in_canvas(
            image_names=mis_project.get_image_names(),
            origin_relative_offsets=origin_relative_offsets,
            canvas_extents=canvas_extents,
            canvas_offsets=canvas_offsets)
        unblended_canvas=cr.render_unblended(
            project=mis_project,
            canvas_relative_offsets=canvas_relative_offsets,
            canvas_extents=canvas_extents)
        assert np.all(np.asarray(unblended_canvas)==reference_image)
        dfe_normalizer=cr.build_normalization(
            project=mis_project,
            canvas_relative_offsets=canvas_relative_offsets,
            canvas_extents=canvas_extents,
            weight=cr.weight_dfe)
        blended_canvas_dfe=cr.render_blended(
            project=mis_project,
            canvas_relative_offsets=canvas_relative_offsets,
            canvas_extents=canvas_extents,
            weight=cr.weight_dfe,
            normalizer=dfe_normalizer)
        assert np.all(np.abs(np.asarray(blended_canvas_dfe,dtype=np.int16)-reference_image)<=1) # all pixels are within 1 of their reference value in the blended image
    def test_quadrants(self):
        reference_image_path="tests/test_files/canvas_rectangular/test_image_a01.npy"
        reference_image=np.load(reference_image_path)
        mis_filepath="tests/test_files/canvas_rectangular/test_project_a01_q.json"
        mis_project=MISProjectJSON.load(mis_filepath)
        origin=mis_project.get_image_names()[0]
        origin_relative_offsets=cr.rectangular_solve(
            relations=mis_project.get_relations(),
            image_names=mis_project.get_image_names(),
            origin=origin
        )
        origin_relative_extents=cr.find_relative_extents_project(
            project=mis_project,
            origin_relative_offsets=origin_relative_offsets,)
        canvas_extents, canvas_offsets=cr.resolve_extents(origin_relative_extents)
        canvas_relative_offsets=cr.place_in_canvas(
            image_names=mis_project.get_image_names(),
            origin_relative_offsets=origin_relative_offsets,
            canvas_extents=canvas_extents,
            canvas_offsets=canvas_offsets)
        unblended_canvas=cr.render_unblended(
            project=mis_project,
            canvas_relative_offsets=canvas_relative_offsets,
            canvas_extents=canvas_extents)
        assert np.all(np.asarray(unblended_canvas)==reference_image)
        dfe_normalizer=cr.build_normalization(
            project=mis_project,
            canvas_relative_offsets=canvas_relative_offsets,
            canvas_extents=canvas_extents,
            weight=cr.weight_dfe)
        blended_canvas_dfe=cr.render_blended(
            project=mis_project,
            canvas_relative_offsets=canvas_relative_offsets,
            canvas_extents=canvas_extents,
            weight=cr.weight_dfe,
            normalizer=dfe_normalizer)
        assert np.all(np.abs(np.asarray(blended_canvas_dfe,dtype=np.int16)-reference_image)<=1) # all pixels are within 1 of their reference value in the blended image