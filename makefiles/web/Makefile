# This is a template makefile 
#
# by default you will be receiving the following vars.
#
# @name
# @description      
# @release 
# @version
# @source
# @download_dir
# @building_dir
# @package_installation_path
#
# You need to setup the following vars
# @email
# @author

#============= GLOBAL ============================
package_full_name=$(name)-$(version).$(release)
package_building_directory_container=$(building_dir)/$(package_full_name).package
package_building_directory=$(package_building_directory_container)/$(package_full_name)

ifndef package_installation_path
package_installation_path=/tmp/jvibuilder/installation/$(package_full_name)
endif

ifndef email
email=juanviola@gmail.com
endif

ifndef author
author="Juan Viola"
endif

all: test finish

test:
	@echo "name: $(name)\n"\
	"description: $(description)\n"\
	"release: $(release)\n"\
	"version: $(version)\n"\
	"source: $(source)\n"\
	"download_dir: $(download_dir)\n"\
	"building_dir: $(building_dir)\n"\
	"packages_dir: $(packages_dir)\n"\
	"package_full_name: $(package_full_name)\n"\
	"package_building_directory: $(package_building_directory)\n"\
	"package_installation_path: $(package_installation_path)\n"\
	"\n" > /tmp/jvibuilder_$(package_full_name).txt

create_tmp:
	@mkdir -p $(package_building_directory) $(package_building_directory)$(package_installation_path)
	# @cd $(package_building_directory)$(package_installation_path)

decompress: create_tmp
	@tar -zxf $(source) -C $(package_building_directory)$(package_installation_path)

create_tar: decompress
	@cd $(package_building_directory_container); tar -zcf $(package_full_name).tar.gz $(package_full_name)

dh_make: create_tar
	@export DEBFULLNAME=$(email); \
	export DEBEMAIL=$(author); \
	cd $(package_building_directory); yes | dh_make --single -f ../$(package_full_name).tar.gz
	@rm -f $(package_building_directory)/debian/*.ex

create_description:
	@sed -i 's/Description:/#Description:/g' $(package_building_directory)/debian/control
	@sed -i 's/ <insert long description/# <insert long description/g' $(package_building_directory)/debian/control
	@echo "Description: $(description)" >> $(package_building_directory)/debian/control

# Create symlinks ---------------------
# this is not in use, but i leave it here as an example just if you need it
create_symlinks: 
	@echo "$(package_installation_path) /tmp/package-current" > $(package_building_directory)/debian/$(name).links

# Create symlinks ---------------------
# this is not in use, but i leave it here as an example just if you need it
create_preinst: 
	@echo "#!/bin/sh\n"\
	"set -e\n"\
	"mkdir -p $(package_installation_path)\n"\
	"#DEBHELPER#\n\n"\
	"exit 0\n" > $(package_building_directory)/debian/$(name).preinst

# Create symlinks ---------------------
# this is not in use, but i leave it here as an example just if you need it
create_postinst:
	@echo "#!/bin/sh\n"\
	"set -e\n"\
	"chown -R root.root $(package_installation_path) \n"\
	"#DEBHELPER#\n\n"\
	"exit 0\n" > $(package_building_directory)/debian/$(name).postinst


install_files:
	@echo "$(package_installation_path)" > $(package_building_directory)/debian/$(name).install

# build: dh_make add_install_files create_symlinks create_preinst create_postinst
build: dh_make create_description install_files
	@cd $(package_building_directory); fakeroot dpkg-buildpackage -F -uc -us

finish: build
	@mv $(package_building_directory_container)/*.deb $(packages_dir)
	@rm -rf $(package_building_directory_container)
