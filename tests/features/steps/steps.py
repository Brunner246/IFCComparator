import os

import ifcopenshell
from behave import given, when, then
from ifcopenshell import open as ifc_open

SUPPORTED_SCHEMAS = ['IFC2X3', 'IFC4']


def verify_schema(ifc_file):
    schema = ifc_file.header.file_schema.schema_identifiers[0]
    if schema not in SUPPORTED_SCHEMAS:
        raise RuntimeError(f"Unsupported schema: {schema}")


def get_absolute_path(relative_path):
    base_path = os.getcwd()
    return os.path.join(base_path, relative_path)


def find_material_by_guid(ifc_file: ifcopenshell.file, guid):
    entity = ifc_file.by_guid(guid)
    if not entity:
        raise RuntimeError(f"Entity with GUID {guid} not found")

    relating_objects = [rel for rel in ifc_file.by_type('IfcRelAssociatesMaterial') if entity in rel.RelatedObjects]
    if not relating_objects:
        raise RuntimeError(f"No material associated with entity {guid}")

    return relating_objects[0].RelatingMaterial


@given('I have an IFC file "{file1}"')
def step_given_ifc_file1(context, file1):
    context.file1_path = get_absolute_path(file1)


@given('I have another IFC file "{file2}"')
def step_given_ifc_file2(context, file2):
    context.file2_path = get_absolute_path(file2)


@when('I compare the material names')
def step_when_compare_material_names(context):
    context.file1 = ifc_open(context.file1_path)
    context.file2 = ifc_open(context.file2_path)

    verify_schema(context.file1)
    verify_schema(context.file2)

    context.material1 = find_material_by_guid(context.file1, "2xhZRRWMbBEgJbs7mKSY8E")
    context.material2 = find_material_by_guid(context.file2, "2xhZRRWMbBEgJbs7mKSY8E")


@then('the material name should be "{expected_name}"')
def step_then_check_material_name(context, expected_name):
    assert context.material1 is not None, "Material not found in file1"
    assert context.material2 is not None, "Material not found in file2"
    assert context.material1.Name == expected_name, f"Material name in file1 is {context.material1.Name}, expected {expected_name}"
    assert context.material2.Name == expected_name, f"Material name in file2 is {context.material2.Name}, expected {expected_name}"
