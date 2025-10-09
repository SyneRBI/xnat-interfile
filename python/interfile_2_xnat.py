import xmlschema
from typing import Any, Tuple
from pathlib import Path
import stir


def get_dict_values(dict: dict, key_list: list[Any]) -> Any:
    """Given a dictionary and a list of keys, a new filtered
    dictionary is returned"""
    if key_list:
        result = dict
        for key in key_list:
            result = result[key]
        return result
    else:
        return None


def get_main_parameter_groups(interfile_dict: dict[str, Any]) -> list[list[Any]]:
    """Given a dictionary, pull out the main parameter groups i.e. keys and
    return in a list"""
    xnat_interfile_list = []
    for ckeys in interfile_dict.keys():
        if "@" not in ckeys and "userParameter" not in ckeys:
            xnat_interfile_list.append([ckeys])
    return xnat_interfile_list


def create_list_param_names(
    xnat_interfile_list: list[list[Any]], interfile_dict: dict[str, Any]
) -> list[list[Any]]:
    """Given a dictionary with info from Mrd headers and a list of main parameter groups
    return a list of parameter names nested within main parameter groups"""
    for _ in range(5):
        flag_finished = True
        xnat_interfile_list_new = []
        for ckey_list in xnat_interfile_list:
            cvals = get_dict_values(interfile_dict, ckey_list)
            if isinstance(cvals, dict):
                flag_finished = False
                xnat_interfile_list_new.extend([ckey_list + [ckey] for ckey in cvals.keys()])
            elif isinstance(cvals, list):
                list_had_dicts = False
                for idx, item in enumerate(cvals):
                    if isinstance(item, dict):
                        list_had_dicts = True
                        xnat_interfile_list_new.extend(
                            [ckey_list + [idx, ckey] for ckey in item.keys()]
                        )
                    else:
                        xnat_interfile_list_new.append(ckey_list + [idx])
                if list_had_dicts:
                    flag_finished = False
            else:
                xnat_interfile_list_new.append(ckey_list)

        if flag_finished:
            break
        xnat_interfile_list = xnat_interfile_list_new
    return xnat_interfile_list

def create_final_xnat_interfile_dict(
    xnat_interfile_list: list[list[Any]],
    interfile_dict: dict[str, Any],
    xnat_interfile_dict: dict[str, str],
) -> dict[str, Any]:
    """
    Create final xnat_interfile_dict by building parameter paths and extracting values.

    Converts parameter paths to XNAT-compatible key strings and retrieves corresponding
    values from the interfile_dict. Handles XNAT field length limitations.
    """
    for param_path in xnat_interfile_list:
        # Build XNAT key path
        key_parts = ["interfile:petLmScanData"]
        key_parts.extend(str(part) for part in param_path if isinstance(part, str))
        ckey = "/".join(key_parts)

        # This field seems to be too long for xnat
        if "parallelImaging/accelerationFactor/kspace_encoding_step" in ckey:
            ckey = ckey.replace("kspace_encoding_step", "kspace_enc_step")
        xnat_interfile_dict[ckey] = get_dict_values(interfile_dict, param_path)

    return xnat_interfile_dict


def check_header_valid_convert_to_dict(
    xml_schema_filename: Path, interfile_listmode_header: bytes
) -> dict[str, Any]:
    """Use xmlschema package to read in xml_schema_filename as xmlschema object and check
    interfile_header is valid before converting the header to a dictionary and returning"""
    xml_schema = xmlschema.XMLSchema(xml_schema_filename)

    if not xml_schema.is_valid(interfile_listmode_header):
        raise Exception("Raw data file is not a valid interfile file")

    return xml_schema.to_dict(interfile_listmode_header)


def interfile_listmode_2_xnat(interfile_listmode_header: bytes, xml_schema_filepath: Path) -> dict[str, Any]:
    """
    This takes the interfile_listmode_header and converts it to a dictionary compatible with XNAT data types.
    """
    interfile_dict = check_header_valid_convert_to_dict(
        xml_schema_filepath, interfile_listmode_header
    )

    xnat_interfile_list = get_main_parameter_groups(interfile_dict)

    xnat_interfile_list = create_list_param_names(xnat_interfile_list, interfile_dict)

    # Create dictionary with parameter names and their values
    xnat_interfile_dict = {}
    xnat_interfile_dict["scans"] = "interfile:petLmScanData"

    return create_final_xnat_interfile_dict(xnat_interfile_list, interfile_dict, xnat_interfile_dict)

def temp():
    xnat_dict = {}

    xnat_dict['scans'] = 'stir:petLmScanData'
    
    xnat_dict['stir:petLmScanData/scannerInformation/name'] = str(lm.get_scanner().get_name())
    
    xnat_dict['stir:petLmScanData/radionuclideInformation/radionuclide'] = str(lm.get_exam_info().get_radionuclide().get_name())
    xnat_dict['stir:petLmScanData/radionuclideInformation/energy'] = float(lm.get_exam_info().get_radionuclide().get_energy())
    xnat_dict['stir:petLmScanData/radionuclideInformation/halfLife'] = float(lm.get_exam_info().get_radionuclide().get_branching_ratio())
    xnat_dict['stir:petLmScanData/radionuclideInformation/branchingRatio'] = float(lm.get_exam_info().get_radionuclide().get_branching_ratio())
    
    xnat_dict['stir:petLmScanData/examInformation/lowEnergyThres'] = float(lm.get_exam_info().get_low_energy_thres())
    xnat_dict['stir:petLmScanData/examInformation/highEnergyThres'] = float(lm.get_exam_info().get_high_energy_thres())
    pat_pos = str(lm.get_exam_info().patient_position)
    pat_pos = pat_pos.replace('<stir::PatientPosition::', '').replace('>', '')
    xnat_dict['stir:petLmScanData/examInformation/patientPosition'] = pat_pos
    
    xnat_dict['stir:petLmScanData/frameInformation/frameStart'] = float(lm.get_exam_info().get_time_frame_definitions().get_start_time())
    xnat_dict['stir:petLmScanData/frameInformation/frameEnd'] = float(lm.get_exam_info().get_time_frame_definitions().get_end_time())
    frame_dur = float(lm.get_exam_info().get_time_frame_definitions().get_end_time() - lm.get_exam_info().get_time_frame_definitions().get_start_time())
    xnat_dict['stir:petLmScanData/frameInformation/frameDuration'] = frame_dur

    return(xnat_dict)
