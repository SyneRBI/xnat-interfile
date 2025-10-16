import xnat
from pathlib import Path
from xnat_interfile.interfile_2_xnat import interfile_listmode_2_xnat
import logging
from typing import Any, Tuple
import stir
import zenodo_get
import zipfile
from xnat.exceptions import XNATResponseError
from datetime import datetime

from xnat_interfile.fetch_datasets import get_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler("xnat_interfile_processing.log"),  # File output
    ],
)

logger = logging.getLogger(__name__)


def verify_project_exists(xnat_session: xnat.XNATSession, project_name: str) -> Any:
    """Verify project exist on XNAT server - disconnect if project does not exist"""
    try:
        xnat_project = xnat_session.projects[project_name]
        logger.info(f"Project {xnat_project} exists")
        return xnat_project
    except KeyError:
        logger.error(f"Project {project_name} not available on server")
        raise NameError(f"Project {project_name} not available on server.")


def upload_interfile_data(
    xnat_session: xnat.XNATSession,
    interfile_listmode_file_path: Path,
    project_name: str,
    subject_name: str,
    experiment_name: str,
    scan_name: str,
) -> Any:
    logger.info(f"Interfile file path: {interfile_listmode_file_path}")

    if not interfile_listmode_file_path.exists():
        raise FileNotFoundError(
            f"Interfile file not found: {interfile_listmode_file_path}"
        )

    xnat_project = verify_project_exists(xnat_session, project_name)
    xnat_subject = create_subject(xnat_session, xnat_project, subject_name)
    experiment = add_experiment(xnat_subject, experiment_name)

    # Load interfile header and convert to XNAT format
    header = stir.ListModeData.read_from_file(str(interfile_listmode_file_path))
    xnat_hdr = interfile_listmode_2_xnat(header)

    xnat_scan = add_scan(experiment, xnat_hdr, scan_name, interfile_listmode_file_path)
    return xnat_scan


def create_subject(
    session: xnat.XNATSession, xnat_project: Any, subject_name: str
) -> Tuple[Any, str]:
    """Create a subject."""
    # Check if subject already exists
    existing_subjects = list(xnat_project.subjects.values())
    existing_subject_labels = [subj.label for subj in existing_subjects]

    if subject_name in existing_subject_labels:
        logger.error(f"Subject {subject_name} already exists")
        raise NameError(f"Subject {subject_name} already exists.")

    # Create subject using the proper XNAT object creation method
    # As per documentation: session.classes.SubjectData(parent=project, label='new_subject_label')
    xnat_subject = session.classes.SubjectData(parent=xnat_project, label=subject_name)

    logger.info(f"Created subject: {subject_name}")

    return xnat_subject


def add_project(xnat_session: xnat.XNATSession, project_name: str) -> None:
    """Add XNAT project"""
    project_uri = f"/data/archive/projects/{project_name}"

    try:
        xnat_session.get(project_uri)
    except XNATResponseError:
        xnat_session.put(project_uri)
    else:
        logger.debug(
            "'%s' project already exists in test XNAT, skipping add data project",
            project_name,
        )

    logger.info(f"Created project: {project_name}")


def add_experiment(xnat_subject: Any, experiment_name: str) -> Any:
    """Add experiment to the XNAT subject"""
    # Check if experiment already exists
    existing_experiments = list(xnat_subject.experiments.values())
    existing_experiment_labels = [exp.label for exp in existing_experiments]

    if experiment_name in existing_experiment_labels:
        logger.error(f"Experiment {experiment_name} already exists")
        raise NameError(f"Experiment {experiment_name} already exists.")

    # Create experiment using the proper XNAT object creation method
    # session.classes.PetSessionData(parent=subject, label='new_experiment_label')
    session = xnat_subject.xnat_session
    experiment = session.classes.PetSessionData(
        parent=xnat_subject, label=experiment_name
    )

    logger.info(f"Created experiment: {experiment_name}")
    return experiment


def add_scan(
    experiment: Any, xnat_hdr: dict, scan_name: str, interfile_file_path: Path
) -> Any:
    """Add scan to experiment. Create scan with the xnat_hdr info. Add PET_RAW resource
    to scan with interfile data.

    Args:
        experiment (Any): existing XNAT experiment
        xnat_hdr (dict): dict containing all the header info to populate in the data type interfile
        scan_name (str): custom str e.g. cart_cine_scan
        interfile_path (Path): Path of interfile containing PET listmode data
    """
    # Check if scan already exists, otherwise create it with all header data
    if scan_name in experiment.scans:
        logger.error(f"XNAT scan {scan_name} already exists")
        raise NameError(f"XNAT scan {scan_name} already exists")

    # Create the scan with all interfile header data at once
    logger.info(f"Creating interfile scan {scan_name} with header data")

    # Use the xnat library's proper method for creating scans with data
    session = experiment.xnat_session
    scan_uri = f"{experiment.uri}/scans/{scan_name}"

    # Create the scan using PUT request with all header data as query parameters
    response = session.put(scan_uri, query=xnat_hdr)

    if response.ok:
        logger.info(f"Successfully created interfile scan: {scan_name}")
        # Refresh the experiment to see the new scan
        experiment.clearcache()

        # Get the created scan object
        scan = experiment.scans[scan_name]

    else:
        logger.error(
            f"Failed to create interfile scan: {response.status_code} - {response.text}"
        )
        raise Exception(f"Failed to create interfile scan: {response.status_code}")

    logger.info(f"Configured interfile scan: {scan_name}")

    # Create resource for interfile files - create the resource first, then upload
    scan_resource = scan.create_resource("PET_RAW")
    scan_resource.upload(interfile_file_path, interfile_file_path.name)
    scan_resource.upload(
        interfile_file_path, interfile_file_path.name.replace(".l.hdr", ".l")
    )
    logger.info(f"Successfully created scan {scan_name} and uploaded interfile files")

    return scan


def main():
    xnat_server_address = "http://localhost"
    user = "admin"
    password = "admin"
    project_name = "interfile_project"
    time_id = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")[:-3]
    subject_name = "Subj-" + time_id
    experiment_name = "Exp-" + time_id
    scan_name = "pet_listmode_scan"
    
    interfile_data_path = get_data()
    logger.info(f"Interfile data path: {interfile_data_path}")

    # Use context manager for automatic connection cleanup
    with xnat.connect(xnat_server_address, user=user, password=password) as session:
        logger.info("Connected to XNAT server")
        upload_interfile_data(
            session,
            interfile_data_path,
            project_name,
            subject_name,
            experiment_name,
            scan_name,
        )


if __name__ == "__main__":
    main()
