import pprint
import logging
import sys

import ifcopenshell
import ifcopenshell.util.element

from src.fuzzy_hashmap import FuzzyHashmap
from src.interfaces.differences_collector import DifferencesCollector
from src.interfaces.file_comparator import FileComparator

handler = logging.StreamHandler(sys.stdout)
frm = logging.Formatter("{asctime} {levelname}: {message}", "%d.%m.%Y %H:%M:%S", style="{")
handler.setFormatter(frm)

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def find_different_keys(dict1, dict2):
    keys1 = set(dict1.keys())
    keys2 = set(dict2.keys())

    keys_only_in_dict1 = keys1 - keys2
    keys_only_in_dict2 = keys2 - keys1

    return keys_only_in_dict1, keys_only_in_dict2


def get_attributes(element):
    attributes = element.get_info(recursive=True, include_identifier=False, ignore={"OwnerHistory"})  # "GlobalId",

    attributes["Properties"] = ifcopenshell.util.element.get_psets(element)
    attributes["Materials"] = ifcopenshell.util.element.get_material(element).get_info(recursive=True,
                                                                                       ignore={
                                                                                           "OwnerHistory"})  # get_materials(element)

    return attributes


class IFCComparator(FileComparator):
    def __init__(self, file1_path, file2_path, collector: DifferencesCollector = None):
        self.file1 = ifcopenshell.open(file1_path)
        self.file2 = ifcopenshell.open(file2_path)
        logger.info(f"Opened files {file1_path} and {file2_path}")
        self.collector = collector
        self.old_file_entities = {e.GlobalId: e for e in self.file1.by_type('IfcBuildingElement')}
        self.new_file_entities = {e.GlobalId: e for e in self.file2.by_type('IfcBuildingElement')}

        self.added_in_new = set()
        self.deleted_from_old = set()
        self.unchanged_in_new = set()

    def compare_elements(self, entity_lhs, entity_rhs):
        attrs1 = FuzzyHashmap(get_attributes(entity_lhs), collector=self.collector)
        attrs2 = FuzzyHashmap(get_attributes(entity_rhs), collector=self.collector)

        keys_only_in_dict1, keys_only_in_dict2 = find_different_keys(self.old_file_entities, self.new_file_entities)

        if attrs1 != attrs2:
            logger.warning(f"Attributes differ between GUID {entity_lhs.GlobalId} and GUID {entity_rhs.GlobalId}")
            pprint.pprint(attrs1.get_differences())
            self.added_in_new.add(entity_rhs.GlobalId)
            return False

        if keys_only_in_dict1 - keys_only_in_dict2:
            logger.warning(f"Attributes missing in {entity_rhs.GlobalId}")
            self.added_in_new.add(entity_rhs.GlobalId)
            return False
        if keys_only_in_dict2 - keys_only_in_dict1:
            logger.warning(f"Attributes missing in {entity_lhs.GlobalId}")
            self.deleted_from_old.add(entity_lhs.GlobalId)

            return False
        return True

    def compare_files(self):
        differences = []

        for global_id, element1 in self.old_file_entities.items():
            if global_id in self.new_file_entities:
                element2 = self.new_file_entities[global_id]
                if not self.compare_elements(element1, element2):
                    differences.append(
                        f"Attributes differ between GUID {element1.GlobalId} and GUID {element2.GlobalId}")
            else:
                differences.append(
                    f"Element Name [{element1.Name}] with GUID [{global_id}] is missing in the second file")

        differences += [f"Element {global_id} is missing in the first file"
                        for global_id in self.new_file_entities.keys()
                        if global_id not in self.old_file_entities]

        return True if len(differences) == 0 else False
