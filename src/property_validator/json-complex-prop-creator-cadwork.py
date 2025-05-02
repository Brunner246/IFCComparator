import json

import cadwork
import element_controller as ec
import geometry_controller as gc
import bim_controller as bc


class PropertyValue:
    def __init__(self, value, unit=None):
        self.value = value
        self.unit = unit

    def to_dict(self):
        return {
            "value": self.value,
            "unit": self.unit
        }


class ComplexPropertySet:
    def __init__(self, name, description, properties=None):
        self.name = name
        self.description = description
        self.properties = properties or {}

    def add_property(self, name, property):
        self.properties[name] = property

    def to_dict(self):
        return {
            "type": "complex",
            "description": self.description,
            "properties": {name: prop.to_dict() for name, prop in self.properties.items()}
        }


class Entity:
    def __init__(self, guid):
        self.guid = guid
        self.property_sets = {}

    def add_property_set(self, name, property_set):
        self.property_sets[name] = property_set

    def to_dict(self):
        return {self.guid: {name: prop_set.to_dict() for name, prop_set in self.property_sets.items()}}


if __name__ == "__main__":
    elements = ec.get_active_identifiable_element_ids()

    entities = []
    for element in elements:
        entity = Entity(bc.get_ifc_base64_guid(element))
        property_set = ComplexPropertySet("BIMWood_Common", "")

        location_x, location_y, location_z = gc.get_p1(element)

        location_properties = {
            "X": PropertyValue(location_x),
            "Y": PropertyValue(location_y),
            "Z": PropertyValue(location_z)
        }
        location = ComplexPropertySet("Location", "Location", location_properties)

        axis_x, axis_y, axis_z = gc.get_xl(element)
        axis_properties = {
            "X": PropertyValue(axis_x),
            "Y": PropertyValue(axis_y),
            "Z": PropertyValue(axis_z)
        }
        axis = ComplexPropertySet("Axis", "Axis", axis_properties)

        ref_zl_x, ref_zl_y, ref_zl_z = gc.get_zl(element)
        ref_direction_properties = {
            "X": PropertyValue(ref_zl_x),
            "Y": PropertyValue(ref_zl_y),
            "Z": PropertyValue(ref_zl_z)
        }
        ref_direction = ComplexPropertySet("RefDirection", "Reference Direction", ref_direction_properties)

        local_coordinate_system_properties = {
            "Location": location,
            "Axis": axis,
            "RefDirection": ref_direction
        }
        local_coordinate_system = ComplexPropertySet("Local coordinate system", "Local coordinate system",
                                                     local_coordinate_system_properties)

        property_set.add_property("Local coordinate system", local_coordinate_system)

        entity.add_property_set("BIMWood_Common", property_set)

        entities.append(entity)

    entities_dict = [entity.to_dict() for entity in entities]
    print(json.dumps(entities_dict, indent=2))

    with open("D:\\source\\Python\\IFCComparator\\entities.json", "w") as file:
        json.dump(entities_dict, file, indent=4)