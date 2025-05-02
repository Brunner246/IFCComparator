import logging
import sys
from typing import List

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util
import ifcopenshell.util.element
import numpy as np

from src.fuzzy_hashmap import FuzzyHashmap
from src.interfaces.differences_collector import DifferencesCollector
from src.interfaces.file_comparator import FileComparator

handler = logging.StreamHandler(sys.stdout)
frm = logging.Formatter("{asctime} {levelname}: {message}", "%d.%m.%Y %H:%M:%S", style="{")
handler.setFormatter(frm)

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def find_different_keys(dict1: dict, dict2: dict):
    keys1 = set(dict1.keys())
    keys2 = set(dict2.keys())

    keys_only_in_dict1 = keys1 - keys2
    keys_only_in_dict2 = keys2 - keys1

    return keys_only_in_dict1, keys_only_in_dict2


def get_entity_properties(element):
    return ifcopenshell.util.element.get_psets(element)


def get_entity_materials(element):
    if material := ifcopenshell.util.element.get_material(element):
        return material.get_info(recursive=True, include_identifier=False, ignore={"OwnerHistory"})
    return None


def get_entity_geometry(element):
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)
    shape = ifcopenshell.geom.create_shape(settings, element)
    if shape:
        # each vertex consists of 3 values (X, Y, Z), reshaping it into (-1, 3)
        # organizes it into an array where each row represents a vertex with three coordinates
        vertices = np.array(shape.geometry.verts).reshape(-1, 3)
        faces = np.array(shape.geometry.faces).reshape(-1, 3)
        return {"vertices": sorted(vertices.tolist()), "faces": sorted(faces.tolist())}
    return None


def get_entity_attributes(element, ignore_attributes):
    attributes = element.get_info(recursive=True, include_identifier=False,
                                  ignore=ignore_attributes)
    attributes["Properties"] = get_entity_properties(element)
    if element.is_a("IfcBuildingElement"):
        attributes["Materials"] = get_entity_materials(element)
        get_entity_geometry_handle_exception(attributes, element)

    return attributes


def get_entity_geometry_handle_exception(attributes, element):
    try:
        attributes["Geometry"] = get_entity_geometry(element)
    except RuntimeError as e:
        logger.error(f"Failed to extract geometry for {element.GlobalId}: {e}")


def get_entities_dict_from_file(file, entity_types: List[str]):
    entities = {}
    for entity_type in entity_types:
        entities.update({e.GlobalId: e for e in file.by_type(entity_type)})
    return entities


class IFCComparator(FileComparator):
    EXCLUDED_ENTITY_TYPES = ["IfcStair", "IfcDoor", "IfcWindow"]

    def __init__(self, file1_path, file2_path, collector: DifferencesCollector = None):
        self.file1 = ifcopenshell.open(file1_path)
        self.file2 = ifcopenshell.open(file2_path)
        logger.info(f"Opened files {file1_path} and {file2_path}")
        self.collector = collector

        entity_types = ['IfcSpace', 'IfcBuildingElement']

        self.old_file_entities = get_entities_dict_from_file(self.file1, entity_types)
        self.new_file_entities = get_entities_dict_from_file(self.file2, entity_types)

        self.keys_to_ignore: List[str] = []
        self.excluded_entity_types = self.EXCLUDED_ENTITY_TYPES

        self.added_in_new = set()
        self.deleted_from_old = set()
        self.unchanged_in_new = set()

    def compare_elements(self, entity_lhs, entity_rhs):
        attributes_to_ignore = {"OwnerHistory"}
        if self.keys_to_ignore:
            attributes_to_ignore.update(self.keys_to_ignore)

        fuzzy_attrs1 = self.create_fuzzy_hashmap(attributes_to_ignore, entity_lhs)
        fuzzy_attrs2 = self.create_fuzzy_hashmap(attributes_to_ignore, entity_rhs)

        keys_only_in_dict1, keys_only_in_dict2 = find_different_keys(self.old_file_entities, self.new_file_entities)

        return self.compare_fuzzy_hashmaps_and_validate_equality(entity_lhs,
                                                                 entity_rhs,
                                                                 fuzzy_attrs1,
                                                                 fuzzy_attrs2,
                                                                 keys_only_in_dict1,
                                                                 keys_only_in_dict2)

    def compare_fuzzy_hashmaps_and_validate_equality(self,
                                                     entity_lhs,
                                                     entity_rhs,
                                                     fuzzy_attrs1,
                                                     fuzzy_attrs2,
                                                     keys_only_in_dict1,
                                                     keys_only_in_dict2):
        if fuzzy_attrs1 != fuzzy_attrs2:
            logger.warning(f"Attributes differ between GUID {entity_lhs.GlobalId} and GUID {entity_rhs.GlobalId}")
            self.added_in_new.add(entity_rhs.GlobalId)
            return False

        entities_file_1 = [self.file1.by_guid(guid).is_a() for guid in keys_only_in_dict1]
        entities_file_2 = [self.file2.by_guid(guid).is_a() for guid in keys_only_in_dict2]
        if (all(entity in self.excluded_entity_types for entity in entities_file_1) and
                all(entity in self.excluded_entity_types for entity in entities_file_2)):
            # Stairs, doors, and windows are not compared - GUID is not consistent from cadwork
            return True

        if keys_only_in_dict1 - keys_only_in_dict2:
            logger.warning(f"Attributes missing in {entity_rhs.GlobalId}")
            self.added_in_new.add(entity_rhs.GlobalId)
            return False
        if keys_only_in_dict2 - keys_only_in_dict1:
            logger.warning(f"Attributes missing in {entity_lhs.GlobalId}")
            self.deleted_from_old.add(entity_lhs.GlobalId)
            return False
        return True

    def create_fuzzy_hashmap(self, attributes_to_ignore, entity_lhs):
        fuzzy_attrs1 = FuzzyHashmap(get_entity_attributes(entity_lhs, attributes_to_ignore), tolerance=1e-5,
                                    collector=self.collector)
        fuzzy_attrs1.set_parent_entity_guid(entity_lhs.GlobalId)
        return fuzzy_attrs1

    def compare_files(self):

        for global_id, element1 in self.old_file_entities.items():
            if global_id in self.new_file_entities:
                element2 = self.new_file_entities[global_id]
                if not self.compare_elements(element1, element2):
                    if not self.collector: break
                    self.collector.add_difference(
                        title=f"Attributes differ between GUID {element1.GlobalId} and GUID {element2.GlobalId}",
                        val1=element1.GlobalId,
                        val2=element2.GlobalId)
            else:
                # If the element is not in the new file, check if it is a stair, door, or window
                if element1.is_a() in self.excluded_entity_types:
                    pass
                else:
                    if not self.collector: break
                    self.collector.add_difference(
                        title=f"Element Name [{element1.Name}] with GUID [{global_id}] is missing in the second file",
                        val1=element1.GlobalId,
                        val2=None)

        for global_id in self.new_file_entities.keys():
            if (global_id not in self.old_file_entities and self.file2.by_guid(global_id).is_a()
                    not in self.excluded_entity_types):
                if not self.collector: break
                self.collector.add_difference(title=f"Element Name [{global_id}] is missing in the second file",
                                              val1=None,
                                              val2=global_id)

        return True if len(self.collector.get_differences()) == 0 else False

    def set_keys_to_ignore(self, keys: List[str]):
        self.keys_to_ignore = keys
