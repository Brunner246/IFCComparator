import argparse
import json
import sys
from typing import TextIO

from src.differences_collector_factory import DifferencesCollectorFactory, CollectionType
from src.file_comparator_factory_impl import IfcFileComparatorFactoryImpl
from src.interfaces.file_comparator import FileComparator
from src.interfaces.file_comparator_factory import FileType


# os.environ['PYTHONPATH'] = os.pathsep.join([
#     os.path.join(os.path.dirname(__file__), '.venv', 'Lib', 'site-packages'),
#     os.path.join(os.path.dirname(__file__), 'src'),
#     os.path.join(os.path.dirname(__file__), 'interfaces'),
#     os.path.dirname(__file__),
# ])
#
# sys.path.extend(os.environ['PYTHONPATH'].split(os.pathsep))


def main():
    parser = set_up_arg_parser()
    args = parser.parse_args()

    output_path = f"{args.output_dir}/differences.json"

    factory = IfcFileComparatorFactoryImpl(args.file1_path, args.file2_path)
    differences_collector = DifferencesCollectorFactory.create(CollectionType.LIST)
    comparator: FileComparator = factory.create(FileType.IFC, differences_collector)

    if args.ignore:
        comparator.set_keys_to_ignore(args.ignore)
    result = comparator.compare_files()

    if not result:
        differences = list(differences_collector.get_differences())
        if not differences:
            print("No differences found.")
            return sys.exit(0)
        output_data = {"errors": differences}
        with open(output_path, 'w') as json_file:  # type: TextIO
            json.dump(output_data, json_file, indent=4)
        print(f"Differences written to {output_path}")
        return sys.exit(1)
    else:
        print("No differences found.")

    print("Done.")
    return sys.exit(0)


def set_up_arg_parser():
    parser = argparse.ArgumentParser(description="Compare two IFC files.")
    parser.add_argument("-f1", "--file1_path", type=str, required=True, help="Path to the first IFC file")
    parser.add_argument("-f2", "--file2_path", type=str, required=True, help="Path to the second IFC file")
    parser.add_argument("-dir", "--output_dir", type=str, required=True, help="Directory to save the output JSON file")
    parser.add_argument("-i", "--ignore", type=str,
                        choices=['CoordIndex', 'CoordList', 'Representation', 'ObjectPlacement',
                                 'Coordinates'], nargs='+',
                        required=False,
                        help="Keys to ignore during comparison")
    return parser


if __name__ == "__main__":
    # python .\main_complex_property.py
    # -f1
    # tests/test_ifc_assembly_steel.ifc
    # -f2
    # tests/test_ifc_assembly_steel_expected.ifc
    # -dir
    # tests
    # -s
    # Coordinates
    # CoordIndex
    # CoordList
    # -i
    # CoordIndex
    main()
