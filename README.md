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

## Running a local containerised XNAT

To interactively test the plugin, you can spin up your own local XNAT with
[xnat-docker-compose](https://github.com/NrgXnat/xnat-docker-compose). See their
README for the relevant setup instructions and docker compose commands. The XNAT
instance can then be accessed at <http://localhost> if you want to use the XNAT
user interface.

When you start `xnat-docker-compose` for the first time, a number of directories
will be created inside your clone copy of the repository. To add the plugin,
copy the `build/libs/interfile-VERSION-xpl.jar` into the newly created
`xnat/plugins` directory. Then restart the docker container again following the
instructions in the README.

## Run tests locally

Follow the steps below to run the tests locally on your computer:

- Install [Docker](https://www.docker.com/) on your computer.
- Install the python dependencies:

  ```bash
  # Create xnat-interfile-env environment, with - stir - that can only be
  # installed via conda
  conda env create -f python/environment.yml
  conda activate xnat-interfile-env

  # Install other dependencies with pip
  pip install -e ./python[dev]
  ```

- Build the plugin locally, [as described above](#build-the-plugin-locally).
  This will create a plugin jar at `build/libs/interfile-VERSION-xpl.jar`, which
  will be used by the tests.

- Run pytest

  ```python
  cd python
  pytest
  ```

To skip slow running tests (e.g. those that require restarts of the xnat
instance) use:

```bash
pytest -m "not slow"
```

For faster development you can set an environment variable to keep the xnat4test
instance after an initial run:

```bash
# Keep xnat4test instance
export XNAT4TEST_KEEP_INSTANCE=True
```

If you build a new version of the plugin jar with `gradlew`, you will need to
stop your container before running tests on it.

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

## Version updates

Currently, versions of plugins / gradle are updated manually when required:

### XNAT

To increase the default version of XNAT to build with, you will need to update:

- `vXNAT` in the `buildscript` section at the top of `build.gradle`
- `xnat_version` and `xnat_container_service_version` under
  `python/tests/conftest.py` (as mentioned above, make sure the xnat version +
  container service version are compatible with each other, by referring to the
  xnat
  [compatibility matrix](https://wiki.xnat.org/container-service/container-service-compatibility-matrix)).
- The list of xnat versions you want to test with github actions under `matrix`
  inside `.github/workflows/test.yaml`

### Plugins used in build.gradle

Various gradle plugins are used during the build process, and are listed in the
`plugins` section of `build.gradle` e.g. "com.palantir.git-version". Usually,
these versions are updated to match those used in the latest
[xnat-template-plugin](https://bitbucket.org/xnatx/xnat-template-plugin/src/master/build.gradle).

### Gradle / gradlew

Usually, we keep the `gradle` version matched to that used in the latest
[xnat-template-plugin](https://bitbucket.org/xnatx/xnat-template-plugin/src/master/gradle/wrapper/gradle-wrapper.properties).
The version is listed under `/gradle/wrapper/gradle-wrapper.properties` on the
`distributionUrl` line.

You can check your local version of `gradlew` with:

```bash
./gradlew --version
```

To update, run the following command with the required version:

```bash
# e.g. to update to 8.10.2
./gradlew wrapper --gradle-version 8.10.2
```

This will update most gradle / gradlew files, but to fully update you will need
to run the same command **a second time**. (this will also update
`/gradle/wrapper/gradle-wrapper.jar`).

You may encounter some errors on update, if certain features of your
`build.gradle` have been deprecated in new `gradle` versions. To fix this, refer
to the `build.gradle` in the `xnat-template-plugin`, and read the relevant
[gradle upgrade guides](https://docs.gradle.org/current/userguide/upgrading_version_7.html).
