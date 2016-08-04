// The software provided here is released by the Naval Postgraduate
// School, an agency of the U.S. Department of Navy.  The software
// bears no warranty, either expressed or implied. NPS does not assume
// legal liability nor responsibility for a User's use of the software
// or the results of such use.
//
// Please note that within the United States, copyright protection,
// under Section 105 of the United States Code, Title 17, is not
// available for any work of the United States Government and/or for
// any works created by United States Government employees. User
// acknowledges that this software contains work which was created by
// NPS government employees and is therefore in the public domain and
// not subject to copyright.
//
// Released into the public domain on April 28, 2015 by Bruce Allen.

package edu.nps.sectorscope;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.BufferedReader;
import java.io.FileReader;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.Collection;
import java.util.Date;
import java.util.Iterator;
import java.util.Set;
import org.sleuthkit.autopsy.casemodule.Case;
import org.sleuthkit.autopsy.coreutils.ExecUtil;
import org.sleuthkit.autopsy.coreutils.Logger;
import org.sleuthkit.autopsy.coreutils.MessageNotifyUtil;
import org.sleuthkit.autopsy.ingest.DataSourceIngestModule;
import org.sleuthkit.autopsy.ingest.DataSourceIngestModuleProcessTerminator;
import org.sleuthkit.autopsy.ingest.DataSourceIngestModuleProgress;
import org.sleuthkit.autopsy.ingest.IngestJobContext;
import org.sleuthkit.autopsy.ingest.IngestMessage;
import org.sleuthkit.autopsy.ingest.IngestServices;
import org.sleuthkit.datamodel.BlackboardArtifact;
import org.sleuthkit.datamodel.BlackboardAttribute;
import org.sleuthkit.datamodel.Content;
import org.sleuthkit.datamodel.Image;
import org.sleuthkit.datamodel.SleuthkitCase;
import org.sleuthkit.datamodel.TskCoreException;

/**
 * Blacklist data source ingest module.
 */
public class BlacklistDataSourceIngestModule implements DataSourceIngestModule {

    private static final String moduleName = BlacklistIngestModuleFactory.getModuleName();

    // instantiation
    private final String hashdbDir;

    // startUp
    private IngestJobContext context;
    private Logger logger;
    private String moduleDir;

    // process
    private DataSourceIngestModuleProgress progressBar;
    private String mediaImagePath;
    private String mediaImageName;
    private String jobDir;
    private String hashdbScanFile;
    
    BlacklistDataSourceIngestModule(BlacklistModuleIngestJobSettings settings) {
        this.hashdbDir = settings.getHashdbDir();
    }

    @Override
    public void startUp(IngestJobContext context) throws IngestModuleException {
        this.context = context;
        this.logger = IngestServices.getInstance().getLogger(moduleName);
        
        // make sure hashdb path is valid
        if (new File(this.hashdbDir).exists() == false) {
            logger.log(Level.SEVERE, "hashdb directory path is invalid");
            throw new IngestModuleException("The path to the hashdb directory is invalid");
        }
    }

    private void setWorkPaths(Content dataSource) {

        // define the module output directory
        moduleDir = Case.getCurrentCase().getModulesOutputDirAbsPath() + File.separator + moduleName; //NON-NLS

        // set media image path and name
        Image image = (Image)dataSource;
        mediaImagePath = image.getPaths()[0];
        mediaImageName = new File(mediaImagePath).getName();

        // define the output directory for this job
        String timestampString = new SimpleDateFormat("yyyy-MM-dd-HH-mm-ss").format(new Date());
        jobDir = moduleDir + File.separator + mediaImageName + "_" + timestampString;

        // set path to the scan file
        hashdbScanFile = jobDir + File.separator + "hashdb_scanfile.json";

        // create the output directory and any parent directories required to reach it
        new File(jobDir).mkdirs();
    }

    @Override
    public ProcessResult process(Content dataSource, DataSourceIngestModuleProgress progressBar) {
        this.progressBar = progressBar;

        // skip if not processing sleuthkit.datamodel.Image
        if (!(dataSource instanceof Image)) {
            // not a disk image
            return ProcessResult.OK;
        }

        // set work paths
        setWorkPaths(dataSource);

//        // perform phases of processing
 //       progressBar.switchToDeterminate(4);
 //       progressBar.progress(0);

        // run hashdb scan_media
        progressBar.switchToIndeterminate();
        ProcessResult result = hashdbScanMedia();
        progressBar.switchToDeterminate(3);

        // report results depending on whether blacklist data was found
        if (result == ProcessResult.OK && hasMatch()) {

            // show source summary from hashdb_scanfile.json
            if (result == ProcessResult.OK) {
                progressBar.progress(1);
                result = showSourceSummaryString();
            }

            // add report visualization launcher
            if (result == ProcessResult.OK) {
                progressBar.progress(2);
                result = addReportVisualizationLauncher();
            }

        } else {
            // no blacklist block hashes were found
            progressBar.progress(3);
        }

        // alert if error
        if (result != ProcessResult.OK) {
            MessageNotifyUtil.Notify.show("Error processing block hash blacklist module",
                       "Block hash blacklist module failed", MessageNotifyUtil.MessageType.ERROR);
        } else {
            progressBar.progress(3);
        }
        return result;
    }

    // run hashdb scanner
    private ProcessResult hashdbScanMedia()
        // set progress type
        // in the future, get fancy and track progress using switchToDeterminate(n)
        // progressBar.switchToIndeterminate();

        // configure the hashdb command to execute
        List<String> commandLine = new ArrayList<>();
        commandLine.add("hashdb.exe");
        commandLine.add("scan_media");
        commandLine.add("-x");
        commandLine.add("r");
        commandLine.add(hashdbDir);
        commandLine.add(mediaImagePath);

        // configure the process to be executed
        ProcessBuilder processBuilder = new ProcessBuilder(commandLine);
        String stdoutPath = hashdbScanFile;
        String stderrPath = jobDir + File.separator + "stderr_hashdb.txt";
        processBuilder.redirectOutput(ProcessBuilder.Redirect.to(new File(stdoutPath)));
        processBuilder.redirectError(ProcessBuilder.Redirect.to(new File(stderrPath)));
        
        // execute the hashdb scan_media process
        try {
            int status;
            status = ExecUtil.execute(processBuilder, new DataSourceIngestModuleProcessTerminator(context));
            if (status == 0) {
                logger.log(Level.INFO, "hashdb scan_media completed");
            } else {
                logger.log(Level.SEVERE, "hashdb scan_media failed");
                return ProcessResult.ERROR;
            }
        } catch (IOException ex) {
            logger.log(Level.SEVERE, "hashdb process failed", ex);  //NON-NLS
            return ProcessResult.ERROR;
        }
        return ProcessResult.OK;
    }

    // return summary else "" and log on error
    private String getScanFileSummary() {
        logger = IngestServices.getInstance().getLogger(BlacklistIngestModuleFactory.getModuleName());
        logger.log(Level.INFO, "ScanFileSummaryReader.a");
        int count = 0;
        try {
            // process each input line hashdb_scan_file.json
            BufferedReader br;
            br = new BufferedReader(new FileReader(hashdbScanFilePath));
            String line = br.readLine();

            while (line != null) {
                // count match lines
                if (!line.isEmpty() && line.charAt(0) != '#') {
                    count++;
                }
                line = br.readLine();
            }

        } catch (IOException ex) {
            logger.log(Level.SEVERE, "hashdb read file failed", ex);  //NON-NLS
            return "";
        }
        if (count == 1) {
            return "1 blacklist block hash offset match found";
        } else {
            return count + " blacklist block hash offset matches found";
        }
    }

    private ProcessResult showSourceSummaryString() {
        String summaryString = getSourceSummaryString();
        if (summaryString == "") {
            return ProcessResult.ERROR;
        } else {
            // send summary to message inbox
            IngestMessage message = IngestMessage.createMessage(IngestMessage.MessageType.INFO,
                                  BlacklistIngestModuleFactory.getModuleName(), summaryString);
            IngestServices.getInstance().postMessage(message);

            return ProcessResult.OK;
        }

    // add visualization launcher if data was found
    private ProcessResult addReportVisualizationLauncher() {

        String blockViewerPath = jobDir + File.separator + "sectorscope_launcher.bat";
        String blockViewerCommand = "sectorscope.py -i \"" + hashdbScanFile + "\"";
        try {
            File file = new File(blockViewerPath);
            if (!file.exists()) {
                file.createNewFile();
            }
            FileOutputStream fileStream = new FileOutputStream(file);
            fileStream.write(blockViewerCommand.getBytes());
            fileStream.flush();
        } catch (IOException ex) {
            logger.log(Level.SEVERE, "Error writing sectorscope launcher at "
                       + blockViewerPath, ex);  //NON-NLS
            return ProcessResult.ERROR;
        }

        try {
            Case.getCurrentCase().addReport(blockViewerPath, moduleName, mediaImageName);
        } catch (TskCoreException ex2) {
            String errorMessage = String.format("Error adding %s to case as report", mediaImageName);
            logger.log(Level.SEVERE, errorMessage, ex2);
            return ProcessResult.ERROR;
        }
        return ProcessResult.OK;
    }
}

