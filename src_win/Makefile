# Run this Makefile to build the Windows Installer to install the
# block match Python scripts and to set PATH to find them.

VERSION = 0.0.1

INSTALLER = block_match-$(VERSION)-windowsinstaller.exe

installer: $(INSTALLER)

$(INSTALLER): build_installer.nsi EnvVarUpdate.nsi
	@echo Making $(INSTALLER)
	makensis -DVERSION=$(VERSION) build_installer.nsi
	cp $(INSTALLER) download/$(INSTALLER)
	echo '**************** INSTALLER IS MADE ****************'

clean:
	/bin/rm -rf $(INSTALLER)

.PHONY: installer clean

