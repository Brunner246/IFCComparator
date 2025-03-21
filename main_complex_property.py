# ifc_property_validator/src/main.py
import argparse
import json
import logging
import os
import sys
from typing import Dict, List, Optional, Set

# Import our modules
from src.property_validator.services.ifc_reader import IfcReader
from src.property_validator.services.json_reader import JsonReader
from src.property_validator.services.comparator import PropertyComparator
from src.property_validator.models.comparison_result import ComparisonSummary
from src.property_validator.utils.logger import setup_logger

# Set up logging
logger = setup_logger("ifc_property_validator", logging.INFO)


def parse_args():
    parser = argparse.ArgumentParser(description="Compare IFC complex properties with reference JSON")
    parser.add_argument("--ifc", required=True, help="Path to IFC file")
    parser.add_argument("--json", required=True, help="Path to reference JSON file")
    parser.add_argument("--output", help="Path to output JSON file with results")
    parser.add_argument("--tolerance", type=float, default=0.0001,
                        help="Tolerance for floating-point comparisons")
    parser.add_argument("--filter", help="Filter by specific entity GUID(s), comma-separated")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--show-matches", action="store_true", help="Show details for matched properties as well")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Check if files exist
    if not os.path.isfile(args.ifc):
        logger.error(f"IFC file not found: {args.ifc}")
        return 1

    if not os.path.isfile(args.json):
        logger.error(f"JSON file not found: {args.json}")
        return 1

    # Filter GUIDs if specified
    filter_guids = None
    if args.filter:
        filter_guids = set(args.filter.split(','))

    # Initialize readers and comparator
    ifc_reader = IfcReader(args.ifc)
    json_reader = JsonReader(args.json)
    comparator = PropertyComparator(float_tolerance=args.tolerance)

    # Get entities with complex properties from IFC
    ifc_entities = ifc_reader.get_entities_with_complex_properties()
    logger.info(f"Found {len(ifc_entities)} entities with complex properties in IFC")

    # Get entities from JSON
    json_entities = json_reader.get_entities()
    logger.info(f"Found {len(json_entities)} entities in JSON")

    # Combine and filter entities
    ifc_guids = set(guid for guid, _ in ifc_entities)
    json_guids = set(json_entities)
    all_guids = ifc_guids | json_guids

    if filter_guids:
        all_guids &= filter_guids
        logger.info(f"Filtered to {len(all_guids)} entities")

    # Create comparison summary
    summary = ComparisonSummary()

    # Compare entities
    for guid in all_guids:
        logger.info(f"Comparing entity {guid}")

        ifc_properties = ifc_reader.get_complex_properties_by_guid(guid)
        json_properties = json_reader.get_complex_properties_by_guid(guid)

        entity_result = comparator.compare_entities(guid, ifc_properties, json_properties)
        summary.add_entity_result(entity_result)

    # Print summary
    print(summary)

    # Write output if requested
    if args.output:
        # Create a serializable summary
        output_data = {
            "entity_count": summary.entity_count,
            "matched_entities": summary.matched_entity_count,
            "mismatched_entities": summary.mismatched_entity_count,
            "entities": {}
        }

        for guid, entity_result in summary.entity_results.items():
            entity_data = {
                "match_count": entity_result.match_count,
                "mismatch_count": entity_result.mismatch_count,
                "missing_ifc_count": entity_result.missing_ifc_count,
                "missing_json_count": entity_result.missing_json_count,
                "property_results": []
            }

            for prop_result in entity_result.property_results:
                if args.show_matches or prop_result.status.name != "MATCH":
                    entity_data["property_results"].append({
                        "property_path": prop_result.property_path,
                        "status": prop_result.status.value,
                        "ifc_value": str(prop_result.ifc_value) if prop_result.ifc_value is not None else None,
                        "json_value": str(prop_result.json_value) if prop_result.json_value is not None else None,
                        "tolerance": prop_result.tolerance
                    })

            output_data["entities"][guid] = entity_data

        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2)

        logger.info(f"Output written to {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())