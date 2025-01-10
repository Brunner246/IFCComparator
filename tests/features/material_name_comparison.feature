Feature: Compare Material Names in IFC Files
  Scenario: Compare material names for equality
    Given I have an IFC file "tests/new.ifc"
#    run from cmd with "../new.ifc"
    And I have another IFC file "tests/old.ifc"
    When I compare the material names
    Then the material name should be "Duo nsi I"