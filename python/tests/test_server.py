import xnat
from pathlib import Path
import xmlschema
import pytest


@pytest.fixture
def interfile_schema_fields():
    """Read data fields from the plugin's interfile schema file - interfile.xsd - and convert to xnat style."""

    interfile_schema_file = (
        Path(__file__).parents[2]
        / "src"
        / "main"
        / "resources"
        / "schemas"
        / "interfile"
        / "interfile.xsd"
    )
    interfile_schema = xmlschema.XMLSchema(interfile_schema_file, validation="skip")

    # we only want the 'leaves' of the xml tree - not intermediate elements
    components = [
        component
        for component in interfile_schema.iter_components(
            xsd_classes=(xmlschema.validators.elements.XsdElement,)
        )
    ]
    filtered_components = []
    for component in components:
        if isinstance(component.type, xmlschema.validators.simple_types.XsdSimpleType):
            filtered_components.append(component)
        elif (component.type.name is not None) and (
            component.type.name.endswith("anyType")
        ):
            filtered_components.append(component)

    # get full path to each component in xnat style (i.e. _ separated + uppercase)
    component_paths = []
    for component in filtered_components:
        path = component.get_path().replace("{http://ptb.de/interfile}", "")
        path = f"petLmScanData/{path.replace('/', '_').upper()}"

        # paths over 75 characters in xnat seem to be truncated
        if len(path) > 75:
            path = path[:75]

        component_paths.append(path)

    return component_paths


def test_interfilePlugin_installed(xnat_session, plugin_version):
    assert "interfilePlugin" in xnat_session.plugins
    interfile_plugin = xnat_session.plugins["interfilePlugin"]
    assert interfile_plugin.version == f"{plugin_version}-xpl"
    assert interfile_plugin.name == "XNAT 1.8 Interfile plugin"


def test_interfile_data_fields(xnat_session, interfile_schema_fields):
    """Confirm that all data fields defined in the interfile schema file - interfile.xsd - are registered in xnat"""

    # get interfile data types from xnat session
    inspector = xnat.inspect.Inspect(xnat_session)
    assert "interfile:petLmScanData" in inspector.datatypes()
    xnat_data_fields = inspector.datafields("petLmScanData")

    # get expected data types from plugin's interfile schema (+ added types relating to xnat project / session info)
    additional_xnat_fields = [
        "petLmScanData/SESSION_LABEL",
        "petLmScanData/SUBJECT_ID",
        "petLmScanData/PROJECT",
        "petLmScanData/ID",
    ]
    expected_data_fields = interfile_schema_fields + additional_xnat_fields

    assert sorted(xnat_data_fields) == sorted(expected_data_fields)
