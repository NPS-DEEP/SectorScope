# Run this Makefile to build the NPS-block_match Windows Installer and
# the .zip distribution.  Both are copied into the download directory.

VERSION = 0.2.0

SOURCES = ../python/*.py
UM_DIR = ../doc/SectorScope_um
UM = SectorScope_um.pdf

WIN_INSTALLER = NPS-SectorScope-$(VERSION)-windowsinstaller.exe
ZIP = NPS-SectorScope-$(VERSION).zip
ZIP_DIR = NPS-SectorScope-$(VERSION)
AUTOPSY_PLUGIN = NPS-SectorScope-$(VERSION).nbm
#AUTOPSY_PLUGIN = ../autopsy_plugin/nbm/SectorScope-$(VERSION).nbm

all: win_installer zip plugin

win_installer: $(INSTALLER)

$(INSTALLER): build_installer.nsi EnvVarUpdate.nsi $(UM) $(SOURCES)
	@echo Making $(INSTALLER)
	makensis -DVERSION=$(VERSION) build_installer.nsi
	cp $(INSTALLER) download/$(INSTALLER)
	@echo '**************** INSTALLER IS MADE ****************'

$(UM_DIR)/$(UM):
	@echo Please run make in $(UM_DIR)
	exit 1

$(UM): $(UM_DIR)/$(UM)
	cp $(UM_DIR)/$(UM) .

zip: $(ZIP)

$(ZIP): $(SOURCES) $(UM)
	rm -rf $(ZIP_DIR)
	mkdir $(ZIP_DIR)
	cp $(SOURCES) $(ZIP_DIR)
	zip -r9 $(ZIP) $(ZIP_DIR)
	rm -rf $(ZIP_DIR)
	cp $(ZIP) download/$(ZIP)

$(AUTOPSY_PLUGIN): ../autopsy_plugin/build/SectorScope.nbm
	cp ../autopsy_plugin/build/SectorScope.nbm $(AUTOPSY_PLUGIN)

clean:
	/bin/rm -rf $(INSTALLER) $(ZIP_DIR) $(ZIP) $(AUTOPSY_PLUGIN) $(UM)

.PHONY: win_installer zip clean

