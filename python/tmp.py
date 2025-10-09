#%%
import xnat 
from pathlib import Path
import logging
from populate_datatype_fields import upload_interfile_data
from interfile_2_xnat import interfile_listmode_2_xnat
import stir

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

pname = '/Users/kolbit01/Documents/Code/Repos/xnat-mrd/test-data/'
fname = 'PET_ACQ_166_20130725111508-0.l.hdr'

xnat_server_address = "http://localhost"
user = "admin"
password = "admin"
project_name = "interfile"

interfile_file_path = Path(pname + fname)

header = stir.ListModeData.read_from_file(interfile_file_path)
xnat_hdr = interfile_listmode_2_xnat(header, Path(__file__).parent / "interfile.xsd")

session=None
logger.info("Connected to XNAT server")
upload_interfile_data(session, interfile_file_path, project_name)

# Use context manager for automatic connection cleanup
with xnat.connect(xnat_server_address, user=user, password=password) as session:
    logger.info("Connected to XNAT server")
    upload_interfile_data(session, interfile_file_path, project_name)