# Interfile

Xnat schema for interfile data format.

In order to create the plugin clone the repository:
```
git clone https://github.com/ckolbPTB/xnat-interfile.git
cd xnat-interfile
```
and then use gradlew to build the plugin
```
./gradlew clean xnatPluginJar
```

If you want to rebuild the plugin after making some changes to the code
it is a good idea to ensure there are no more running gradlew clients:
```
./gradlew --stop
```
before building again with
```
./gradlew clean xnatPluginJar
```

## Hints
- If you make changes to interfile.xsd and add new parameters then it is best to delete *interfile_itfScanData_details.vm* and let gradle recreate it. Copy it then from the folder *xnat-generated* back.
