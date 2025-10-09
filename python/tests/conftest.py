from pathlib import Path
import subprocess
import pytest
import xnat4tests
import time
import requests
import xnat
import re
import os


@pytest.fixture(scope="session")
def xnat_version():
    try:
        version = os.environ["XNAT_VERSION"]
    except KeyError:
        version = "1.9.2"

    return version


@pytest.fixture(scope="session")
def xnat_container_service_version():
    try:
        version = os.environ["XNAT_CS_VERSION"]
    except KeyError:
        version = "3.7.2"

    return version


@pytest.fixture(scope="session")
def xnat_config(tmp_path_factory, xnat_version, xnat_container_service_version):
    tmp_dir = tmp_path_factory.mktemp("data")

    return xnat4tests.Config(
        xnat_root_dir=tmp_dir,
        docker_image="xnat_interfile_xnat4tests",
        docker_container="xnat_interfile_xnat4tests",
        build_args={
            "xnat_version": xnat_version,
            "xnat_cs_plugin_version": xnat_container_service_version,
        },
    )


@pytest.fixture(scope="session")
def jar_path():
    jar_dir = Path(__file__).parents[2] / "build" / "libs"
    return list(jar_dir.glob("interfile-*xpl.jar"))[0]


@pytest.fixture(scope="session")
def plugin_version(jar_path):
    match_version = re.search("interfile-(.+?)-xpl.jar", jar_path.name)

    if match_version is None:
        raise NameError(
            "Jar name contains no version - did you pull the latest tags from github before running gradlew?"
        )
    else:
        return match_version.group(1)


@pytest.fixture(scope="session")
def xnat_session(xnat_config, jar_path):
    plugin_path = Path("/data/xnat/home/plugins")
    if not jar_path.exists():
        raise FileNotFoundError(f"Plugin JAR file not found at {jar_path}")

    xnat4tests.start_xnat(xnat_config)

    # Install interfile plugin by copying the jar into the container
    try:
        subprocess.run(
            [
                "docker",
                "cp",
                str(jar_path),
                f"xnat_interfile_xnat4tests:{(plugin_path / jar_path.name).as_posix()}",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Command {e.cmd} returned with error code {e.returncode}: {e.output}"
        ) from e

    xnat4tests.restart_xnat(xnat_config)

    # Wait for XNAT to be available. This is based on code in xnat4tests.start_xnat that waits for the initial
    # container startup.
    for attempts in range(xnat_config.connection_attempts):
        try:
            session = xnat4tests.connect(xnat_config)
        except (
            xnat.exceptions.XNATError,
            requests.ConnectionError,
            requests.ReadTimeout,
        ):
            if attempts == xnat_config.connection_attempts:
                raise RuntimeError("XNAT did not start in time")
            else:
                time.sleep(xnat_config.connection_attempt_sleep)
        else:
            break

    yield session

    session.disconnect()
    xnat4tests.stop_xnat(xnat_config)
