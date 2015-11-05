# Jvibuilder

JviBuilder will help you to create debian packages from tar.gz source files.

### How it works
This app was created to use in conjuntion with Jenkins (https://jenkins-ci.org/) so, for that reason it takes a tar.gz source file from a specified URL and at the moment do not support creating packages from local files.

## Installation
##### Debian/Ubuntu
You need the following packages:

```sh
$ apt-get install python-pip dh-make fakeroot mongodb git
```
```sh
$ pip install daemon-runner pymongo PyYAML
```
```sh
$ git clone https://github.com/juanviola/jvi-builder.git
```

## How to use it?
After installing, You'll need to start the jvibuilder daemon. So, enter to the jvi-builder directory and run the following.

```sh
$ ./jvibuilder.py start
```
You can see the logs into the jvi-builder/log directory to see if everythig goes allright.

#### Do a manyally push into the mongo database
```sh
$ mongo 
```
```mongo
use jvi
db.packages.insert({
	'description': 'this is a testing package',
	'type': 'web',
	'version': 1,
	'release': 0,
	'name': 'my-appname',
	'opts': 'environment=prodcution package_installation_path=/tmp/my-appname',
	'url': 'http://localhost/my-appname-source.tar.gz
	'building': 0
}); 
```
#### Mongo PUSH required fields
 - **name** -- Package name, ie: my-app-name will create the package *my-app-name_1.0_i386.deb* 
 - **type** -- The type will be the directory where it will look for the makefile to be run. ie: We will use the type=web so, the makefile to be used will be the one under **jvibuilder/makefiles/web/Makefile**
 - **version** -- Version
 - **release** -- Release
 - **opts** [package_installation_path] -- Path to where this package has to be installed after the Debian dpkg was run
 - **url** -- url to download the source package, ie: http://my.jenkins-server.com/my-appname-source.tar.gz 
 - **building** -- this field is required and the value allways is 0 (zero)
 
#### Mongo OPTIONAL fields
 - **description** -- This is my application description

### Technical information
**Version:** 1.0

### Todos
 - Create Debian/Ubuntu files from local "tar.gz" files
 - Create an API
 - Create a web interface to see packages status

License
----
[GPL V3](http://www.gnu.org/licenses/gpl-3.0.txt)




