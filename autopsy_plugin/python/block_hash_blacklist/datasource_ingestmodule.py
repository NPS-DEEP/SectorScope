# The software provided here is released by the Naval Postgraduate
# School, an agency of the U.S. Department of Navy.  The software
# bears no warranty, either expressed or implied. NPS does not assume
# legal liability nor responsibility for a User's use of the software
# or the results of such use.
#
# Please note that within the United States, copyright protection,
# under Section 105 of the United States Code, Title 17, is not
# available for any work of the United States Government and/or for
# any works created by United States Government employees. User
# acknowledges that this software contains work which was created by
# NPS government employees and is therefore in the public domain and
# not subject to copyright.
#
# Released into the public domain on April 28, 2015 by Bruce Allen.

import jarray
from java.lang import System
from javax.swing import JCheckBox
from javax.swing import BoxLayout
from org.sleuthkit.autopsy.casemodule import Case
from org.sleuthkit.autopsy.casemodule.services import Services
from org.sleuthkit.autopsy.ingest import DataSourceIngestModule
from org.sleuthkit.autopsy.ingest import FileIngestModule
from org.sleuthkit.autopsy.ingest import IngestMessage
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter
from org.sleuthkit.autopsy.ingest import IngestModuleIngestJobSettings
from org.sleuthkit.autopsy.ingest import IngestModuleIngestJobSettingsPanel
from org.sleuthkit.autopsy.ingest import IngestServices
from org.sleuthkit.autopsy.ingest import IngestModuleGlobalSettingsPanel
from org.sleuthkit.datamodel import BlackboardArtifact
from org.sleuthkit.datamodel import BlackboardAttribute
from org.sleuthkit.datamodel import ReadContentInputStream
from org.sleuthkit.autopsy.coreutils import Logger
from java.lang import IllegalArgumentException

# to support Python
import os
from subprocess import Popen, PIPE

# Defines basic functionality and features of the module
# Implements IngestModuleFactoryAdapter which is a no-op implementation of
# IngestModuleFactory.
class BlockHashBlacklistIngestModuleFactory(IngestModuleFactoryAdapter):
    def __init__(self):
        self.settings = None

    def getModuleDisplayName(self):
        return "Block Hash Blacklist ingest module"

    def getModuleDescription(self):
        return "Find blacklist blocks using the hashdb tool"

    def getModuleVersionNumber(self):
        return "1.0"

    def getDefaultIngestJobSettings(self):
        return BlockHashBlacklistIngestModuleSettings()

    def hasIngestJobSettingsPanel(self):
        return True

    def getIngestJobSettingsPanel(self, settings):
        if not isinstance(settings, BlockHashBlacklistIngestModuleSettings):
            raise IllegalArgumentException("Expected settings argument to be instanceof BlockHashBlacklistIngestModuleSettings")
        self.settings = settings
        return BlockHashBlacklistIngestModuleSettingsPanel(self.settings)

    # Return true if module wants to get passed in a data source
    def isDataSourceIngestModuleFactory(self):
        return True

    # can return null if isDataSourceIngestModuleFactory returns false
    def createDataSourceIngestModule(self, ingestOptions):
        return BlockHashBlacklistDataSourceIngestModule(self.settings)

    # Return true if module wants to get called for each file

    def isFileIngestModuleFactory(self):
        return True

    # can return null if isFileIngestModuleFactory returns false
    def createFileIngestModule(self, ingestOptions):
        return BlockHashBlacklistFileIngestModule(self.settings)

    def hasGlobalSettingsPanel(self):
        return True

    def getGlobalSettingsPanel(self):
        globalSettingsPanel = BlockHashBlacklistIngestModuleGlobalSettingsPanel();
        return globalSettingsPanel


class BlockHashBlacklistIngestModuleGlobalSettingsPanel(IngestModuleGlobalSettingsPanel):
    def __init__(self):
        self.setLayout(BoxLayout(self, BoxLayout.Y_AXIS))
        label = JLabel("Path to Blacklist hashdb database")
        self.add(label)
        textfield = JTextField("hashdb.hdb")
        self.add(textfield)


class BlockHashBlacklistDataSourceIngestModule(DataSourceIngestModule):
    '''
        Data Source-level ingest module.  One gets created per data source. 
        Queries for various files. If you don't need a data source-level module,
        delete this class.
    '''

    def __init__(self, settings):
        self.local_settings = settings
        self.context = None

    def startUp(self, context):
        # Used to verify if the GUI checkbox event been recorded or not.
        logger = Logger.getLogger("BlockHashBlacklistFileIngestModule")

        hashdbDir = self.local_settings.getHashdbDir()
        # check that hashdbDir exists
        if not os.path.isfile(hashdbDir):
            logger.severe("hashdbDir " + hashdbDir + " not found")

        self.context = context

    def process(self, dataSource, progressBar):
        if self.context.isJobCancelled():
            return IngestModule.ProcessResult.OK

        # Configure progress bar for 2 tasks
        progressBar.switchToDeterminate(2)

        autopsyCase = Case.getCurrentCase()
        sleuthkitCase = autopsyCase.getSleuthkitCase()
        services = Services(sleuthkitCase)
        fileManager = services.getFileManager()

        # get case directory
        caseDir = Case.getCurrentCase().getCaseDirectory()
        beOutDir = os.path.join(caseDir, "be_out")
        logger.info("bulk_extractor dir " + beOutDir)

        # get block hash database
        db = context.blockHashDir

        # run hashdb scan
        cmd = ["bulk_extractor.exe", "-E", "hashdb",
               "-S", "hashdb_mode=scan",
               "-S", "hashdb_scan_path_or_socket="+db,
               "-o", "beOutDir"]
        p = Popen(cmd, stdout=PIPE)
        lines = p.communicate()[0].decode('utf-8').split("\n")
        if p.returncode != 0:
            logger.severe("error running bulk_extractor scan")

        # note: at this point, a match exists if identified_blocks.txt
        # is not empty.  For now, just report this fact.
        identified_blocksPath = os.path.join(beOutDir, "identified_blocks.txt")
        if os.getsize(identified_blocksPath) > 0:
            message = IngestMessage.createMessage(
                          IngestMessage.MessageType.DATA,
                          "Block Hash Blacklist Data Source Ingest Module",
                          "No blacklist block hashes were found")
        else:
            message = IngestMessage.createMessage(
                          IngestMessage.MessageType.DATA,
                          "Block Hash Blacklist Data Source Ingest Module",
                          "At least one blacklist block hash was found")

        IngestServices.getInstance().postMessage(message)

        return IngestModule.ProcessResult.OK;


class BlockHashBlacklistIngestModuleSettings(IngestModuleIngestJobSettings):
    serialVersionUID = 1L

    def __init__(self):
        self.hashdbDir = "hashdb.hdb"

    def getVersionNumber(self):
        return serialVersionUID

    def getHashdbDir(self):
        return self.hashdbDir

    def setHashdbDir(self, hashdbDir):
        self.hashdbDir = hashdbDir


class BlockHashBlacklistIngestModuleSettingsPanel(IngestModuleIngestJobSettingsPanel):
    # self.settings instance variable not used. Rather, self.local_settings is used.
    # https://wiki.python.org/jython/UserGuide#javabean-properties
    # Jython Introspector generates a property - 'settings' on the basis
    # of getSettings() defined in this class. Since only getter function
    # is present, it creates a read-only 'settings' property. This auto-
    # generated read-only property overshadows the instance-variable -
    # 'settings'

    def __init__(self, settings):
        self.local_settings.hashdbDir = "blacklist.hdb"

    def getSettings(self):
        return self.local_settings
