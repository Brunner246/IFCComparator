import unittest
import ifcopenshell
import ifcopenshell.geom
import numpy as np


class TestCompareGeometry(unittest.TestCase):
    def setUp(self):
        self.file1_path = './test_ifc_assembly_steel.ifc'
        self.file2_path = './test_ifc_assembly_steel_expected.ifc'

        self.model1 = ifcopenshell.open(self.file1_path)
        self.model2 = ifcopenshell.open(self.file2_path)

        self.settings = ifcopenshell.geom.settings()
        self.settings.set(self.settings.USE_WORLD_COORDS, True)

    def extract_brep_geometry(self, model):
        brep_geometry = {}
        for product in model.by_type("IfcBuildingElement"):
            try:
                shape = ifcopenshell.geom.create_shape(self.settings, product)
                if shape:
                    vertices = np.array(shape.geometry.verts).reshape(-1, 3)
                    faces = np.array(shape.geometry.faces).reshape(-1, 3)
                    attributes = product.get_info()
                    attributes["Geometry"] = {"vertices": vertices.tolist(), "faces": faces.tolist()}
                    brep_geometry[product.GlobalId] = {"vertices": vertices, "faces": faces}
            except Exception as e:
                print(f"Failed to extract geometry for {product.GlobalId}: {e}")
        return brep_geometry

    def test_compare_brep_geometry(self):
        geometry1 = self.extract_brep_geometry(self.model1)
        geometry2 = self.extract_brep_geometry(self.model2)

        self.assertEqual(set(geometry1.keys()), set(geometry2.keys()), "Mismatch in GlobalIds")

        for global_id in geometry1:
            vertices1 = geometry1[global_id]["vertices"]
            vertices2 = geometry2[global_id]["vertices"]
            faces1 = geometry1[global_id]["faces"]
            faces2 = geometry2[global_id]["faces"]

            self.assertEqual(vertices1.shape, vertices2.shape, f"Vertex count mismatch for {global_id}")
            self.assertEqual(faces1.shape, faces2.shape, f"Face count mismatch for {global_id}")

            np.testing.assert_allclose(vertices1, vertices2, atol=1e-6, err_msg=f"Vertex mismatch for {global_id}")
            np.testing.assert_array_equal(faces1, faces2, err_msg=f"Face connectivity mismatch for {global_id}")


if __name__ == '__main__':
    unittest.main()
