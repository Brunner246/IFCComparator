import ifcopenshell

class IFCComparator:
    def __init__(self, file1_path, file2_path):
        self.file1 = ifcopenshell.open(file1_path)
        self.file2 = ifcopenshell.open(file2_path)

    def get_attributes(self, element):
        attributes = {}
        for attribute_name in element.get_info().keys():
            attributes[attribute_name] = element.get_info()[attribute_name]
        return attributes

    def get_geometry_hash(self, element):
        # Placeholder for geometry processing logic
        # This function should return a hash value based on the geometry of the element
        return hash(str(element.Representation))

    def compare_elements(self, element1, element2):
        attrs1 = self.get_attributes(element1)
        attrs2 = self.get_attributes(element2)

        if attrs1 != attrs2:
            print(f"Attributes differ between {element1.GlobalId} and {element2.GlobalId}")
            return False

        geom_hash1 = self.get_geometry_hash(element1)
        geom_hash2 = self.get_geometry_hash(element2)

        if geom_hash1 != geom_hash2:
            print(f"Geometries differ between {element1.GlobalId} and {element2.GlobalId}")
            return False

        return True

    def compare_files(self):
        elements1 = {e.GlobalId: e for e in self.file1.by_type('IfcProduct')}
        elements2 = {e.GlobalId: e for e in self.file2.by_type('IfcProduct')}

        for global_id, element1 in elements1.items():
            if global_id in elements2:
                element2 = elements2[global_id]
                self.compare_elements(element1, element2)
            else:
                print(f"Element {global_id} is missing in the second file")

        for global_id in elements2.keys():
            if global_id not in elements1:
                print(f"Element {global_id} is missing in the first file")

# if __name__ == "__main__":
#     comparator = IFCComparator('file1.ifc', 'file2.ifc')
#     comparator.compare_files()