import argparse
import json
from typing import TextIO

from src.differences_collector import DifferencesCollector
from src.file_comparator_factory_impl import IfcFileComparatorFactoryImpl
from src.interfaces.file_comparator import FileComparator
from src.interfaces.file_comparator_factory import FileType


def main():
    parser = argparse.ArgumentParser(description="Compare two IFC files.")
    parser.add_argument("-f1", "--file1_path", type=str, required=True, help="Path to the first IFC file")
    parser.add_argument("-f2", "--file2_path", type=str, required=True, help="Path to the second IFC file")
    parser.add_argument("-dir", "--output_dir", type=str, required=True, help="Directory to save the output JSON file")
    args = parser.parse_args()

    output_path = f"{args.output_dir}/differences.json"

    factory = IfcFileComparatorFactoryImpl(args.file1_path, args.file2_path)
    differences_collector = DifferencesCollector()
    comparator: FileComparator = factory.create(FileType.IFC, differences_collector)
    result = comparator.compare_files()

    if not result:
        differences = list(differences_collector.get_differences())
        with open(output_path, 'w') as json_file:  # type: TextIO
            json.dump(differences, json_file, indent=4)
        print(f"Differences written to {output_path}")
    else:
        print("No differences found.")

    print("Done.")

if __name__ == "__main__":
    # python .\main.py -f1 .\tests\materialLayer1.ifc -f2 .\tests\materialLayer2.ifc -dir .
    main()