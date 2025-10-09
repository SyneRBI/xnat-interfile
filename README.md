# Interfile

Xnat schema for PET raw data format supported by STIR.

## Build the plugin locally

**Note:** The plugin must be built using `Java 8`. If you have multiple Java
versions installed, ensure your IDE is set to use the correct version, or the
`JAVA_HOME` environment variable is set to the `Java 8` path.

In order to create the plugin clone the repository:

```shell
git clone https://github.com/SyneRBI/xnat-interfile.git
cd xnat-interfile
```

and then use gradlew to build the plugin

```shell
./gradlew init
./gradlew clean xnatPluginJar
```

If you want to rebuild the plugin after making some changes to the code it is a
good idea to ensure there are no more running gradlew clients:

```shell
./gradlew --stop
```

before building again with

```shell
./gradlew clean xnatPluginJar
```

## Run tests locally

Follow the steps below to run the tests locally on your computer:

- Install [Docker](https://www.docker.com/) on your computer.
- Install the python dependencies:

  ```bash
  pip install -r python/tests/requirements.txt
  ```

- Build the plugin locally, [as described above](#build-the-plugin-locally).
  This will create a plugin jar at `build/libs/interfile-VERSION-xpl.jar`, which will
  be used by the tests.

- Run pytest

  ```python
  pytest
  ```

### Running tests locally with a different xnat version

By default, the following versions will be used:

- gradle will build the plugin using the xnat version `vXnat` from
  `build.gradle`.
- pytest will spin up xnat in a docker container using the default versions in
  `python/tests/conftest.py` under `xnat_version` and
  `xnat_container_service_version`.

If you want to use a different version locally, you can override this by setting
the following environment variables:

```bash
# Set xnat version
export XNAT_VERSION=1.8.3

# Set xnat container service plugin version
export XNAT_CS_VERSION=3.1.0
```

Then repeat the last two steps above (building the plugin + running pytest).

Note that Github actions are configured to automatically test multiple versions
of xnat - so it may be simpler to add your required versions to
`.github/workflows/test.yaml` in the `matrix` section. You will need to ensure
your provided xnat container service plugin versions are compatible with the
corresponding xnat version - the xnat docs provide a
[compatibility matrix](https://wiki.xnat.org/container-service/container-service-compatibility-matrix)
for this.

## Creating a new release

Create a new tag in the form `vX.Y.Z` and push it to the repository e.g.

```bash
git tag v1.0.0
git push origin v1.0.0
```

This will trigger a github actions workflow creating:

- a new Github release with `.jar` attached
- a new package on
  [Github packages](https://github.com/orgs/SyneRBI/packages?repo_name=xnat-interfile)

For information about how to use this package as a dependency, see the github
docs for
[maven](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-apache-maven-registry#installing-a-package)
or
[gradle](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-gradle-registry#using-a-published-package).

## Running pre-commit

To set up and run pre-commit:

```shell
# Install pre-commit (if not already installed)
pip install pre-commit

# Install the pre-commit hooks
pre-commit install

# Run pre-commit on all files (optional)
pre-commit run --all-files
```

If you want to disable the pre-commit hooks:

```shell

pre-commit uninstall
```

## Requirements

If using uv then you can take advantage of the inline requirements at the top of
populate_datatype_fields.py by running:

```shell

uv run populate_datatype_fields.py
```

However, the `requirements.txt` file is still available if running the code as
normal with python.
