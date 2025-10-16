import xnat
from pathlib import Path
import xmlschema
import pytest
import stir

from xnat_interfile.interfile_2_xnat import interfile_listmode_2_xnat
from xnat_interfile.populate_datatype_fields import upload_interfile_data, add_project


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


def verify_headers_match(interfile_file_path, scan):
    """Check headers from a given interfile file match those in an xnat scan object"""

    header = stir.ListModeData.read_from_file(str(interfile_file_path))
    interfile_headers = interfile_listmode_2_xnat(header)

    for file_key, file_value in interfile_headers.items():
        if (file_key[0:24] == "interfile:petLmScanData/") and (file_value != ""):
            xnat_header = file_key[24:]

            # xnat seems to round floats to four decimal places
            if isinstance(file_value, float):
                file_value = round(file_value, 4)

            assert file_value == scan.data[xnat_header]


def test_interfilePlugin_installed(xnat_connection, plugin_version):
    assert "interfilePlugin" in xnat_connection.session.plugins
    interfile_plugin = xnat_connection.session.plugins["interfilePlugin"]
    assert interfile_plugin.version == f"{plugin_version}-xpl"
    assert interfile_plugin.name == "XNAT 1.8 Interfile plugin"


@pytest.mark.filterwarnings("ignore:Import of namespace")
def test_interfile_data_fields(xnat_connection, interfile_schema_fields):
    """Confirm that all data fields defined in the interfile schema file - interfile.xsd - are registered in xnat"""

    # get interfile data types from xnat session
    inspector = xnat.inspect.Inspect(xnat_connection.session)
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


@pytest.mark.usefixtures("remove_test_data")
def test_upload_of_data(xnat_connection, interfile_file_path):
    """Upload real-world data."""

    xnat_session = xnat_connection.session
    project_name = "interfile_project"
    subject_name = "interfile_subject"
    experiment_name = "interfile_experiment"
    scan_name = "interfile_scan"

    add_project(xnat_session, project_name)

    upload_interfile_data(
        xnat_session,
        interfile_file_path,
        project_name,
        subject_name,
        experiment_name,
        scan_name,
    )

    # verify data was successfully added
    xnat_experiment = (
        xnat_session.projects[project_name]
        .subjects[subject_name]
        .experiments[experiment_name]
    )

    assert sorted(f.fieldname for f in xnat_experiment.scans[0].files) == [
        "InterfilePetLmScanData",
        "InterfilePetLmScanData",
    ]
    assert sorted(f.id for f in xnat_experiment.scans[0].files) == [
        "20170809_NEMA_60min_UCL.l",
        "20170809_NEMA_60min_UCL.l.hdr",
    ]

    verify_headers_match(interfile_file_path, xnat_experiment.scans[0])


@pytest.mark.usefixtures("remove_test_data")
def test_interfile_data_modification(xnat_connection, interfile_file_path):
    xnat_session = xnat_connection.session
    project_id = "interfile_project"
    add_project(xnat_session, project_id)

    upload_interfile_data(
        xnat_session,
        interfile_file_path,
        project_id,
        "interfile_subject",
        "interfile_experiment",
        "interfile_scan",
    )
    subject = xnat_session.projects[project_id].subjects[0]

    xnat_header = "radionuclideInformation/energy"
    all_headers = subject.experiments[0].scans[0].data
    assert all_headers[xnat_header] == 511
    all_headers[xnat_header] = 513
    assert all_headers[xnat_header] == 513
    assert xnat_header in all_headers.keys()
    new_header = "energy"
    all_headers[new_header] = all_headers.pop(xnat_header)
    assert new_header in all_headers.keys()
    assert xnat_header not in all_headers.keys()
