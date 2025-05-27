import dataclasses
import os
import sys
from collections import defaultdict
from typing import Tuple, Dict

import ifcopenshell


def load_ifc_entities_by_type(ifc_path) -> dict:
    if not os.path.isfile(ifc_path):
        raise FileNotFoundError(f"File not found: {ifc_path}")

    ifc = ifcopenshell.open(ifc_path)
    entities = defaultdict(list)

    for entity in ifc:
        if hasattr(entity, "GlobalId"):
            entities[entity.is_a()].append(getattr(entity, "GlobalId"))
        else:
            entities[entity.is_a()].append(None)

    return entities


def compare_entity_counts(entities1, entities2) -> Dict[str, Tuple[int, int]]:
    all_types = union_entity_types(entities1, entities2)
    comparison: Dict[str, Tuple[int, int]] = {}

    for entity_type in sorted(all_types):
        count1 = len(entities1.get(entity_type, []))
        count2 = len(entities2.get(entity_type, []))
        if count1 != count2:
            comparison[entity_type] = (count1, count2)

    return comparison


def union_entity_types(entities1, entities2):
    all_types = set(entities1.keys()).union(entities2.keys())
    return all_types


@dataclasses.dataclass
class FileEntities:
    file_path: str
    entities: dict

    def __post_init__(self):
        # if not os.path.isfile(self.file_path):
        #     raise FileNotFoundError(f"File not found: {self.file_path}")
        pass


def compare_entity_ids(entities1: FileEntities, entities2: FileEntities):
    all_types = sorted(union_entity_types(entities1.entities, entities2.entities))

    for entity_type in all_types:
        ids1 = set(filter(lambda x: x != None, entities1.entities.get(entity_type, [])))
        ids2 = set(filter(None, entities2.entities.get(entity_type, [])))

        only_in_1 = ids1 - ids2
        only_in_2 = ids2 - ids1

        if only_in_1 or only_in_2:
            print(f"\nEntity Type: {entity_type}")
            if only_in_1:
                print(f"  - Present in File {entities1.file_path} only ({len(only_in_1)}):")
                for guid in sorted(only_in_1):
                    print(f"{'':12}{guid}")
            if only_in_2:
                print(f"  - Present in File {entities2.file_path} only ({len(only_in_2)}):")
                for guid in sorted(only_in_2):
                    print(f"{'':12}{guid}")


def main(file1, file2):
    print(f"Comparing:\n  File 1: {file1}\n  File 2: {file2}\n")
    print(f"Comparing:\n  File 1: {os.path.basename(file1)}\n  File 2: {os.path.basename(file2)}\n")

    entities1 = load_ifc_entities_by_type(file1)
    entities2 = load_ifc_entities_by_type(file2)

    print("=== Entity Count Differences ===")
    count_diffs = compare_entity_counts(entities1, entities2)
    for entity, (count1, count2) in count_diffs.items():
        print(f"{entity}: File1 = {count1}, File2 = {count2}")

    print("\n=== Entity GlobalId Differences ===")
    print("\n=== GlobalId Differences by Entity Type ===")
    compare_entity_ids(FileEntities(os.path.basename(file1), entities1),
                       FileEntities(os.path.basename(file2), entities2))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python compare_ifc_entities.py file1.ifc file2.ifc")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
