import xnat4tests
import xnat
import requests
import time


class XnatConnection:
    """Handle connection to the xnat4tests xnat.

    Allows the same connection to be re-used in most cases (keeping tests fast), but handles creating a
    new connection in the case of xnat restart.
    """

    def __init__(self, config: xnat4tests.Config):
        self.config = config
        self.session = None
        self._connect_to_xnat()

    def restart_xnat(self):
        self.close()
        xnat4tests.restart_xnat(self.config)
        self._connect_to_xnat()

    def close(self):
        self.session.disconnect()

    def _connect_to_xnat(self):
        """Connect to the XNAT instance. Tries multiple times to allow time for initial startup -
        based on code in xnat4tests.start_xnat"""

        for attempts in range(self.config.connection_attempts):
            try:
                session = xnat4tests.connect(self.config)
            except (
                xnat.exceptions.XNATError,
                requests.ConnectionError,
                requests.ReadTimeout,
            ):
                if attempts == self.config.connection_attempts:
                    raise RuntimeError("XNAT did not start in time")
                else:
                    time.sleep(self.config.connection_attempt_sleep)
            else:
                break

        self.session = session


def delete_data(session: xnat.XNATSession) -> None:
    for project in session.projects:
        for subject in project.subjects.values():
            session.delete(
                path=f"/data/projects/{project.id}/subjects/{subject.label}",
                query={"removeFiles": "True"},
            )
        project.subjects.clearcache()
