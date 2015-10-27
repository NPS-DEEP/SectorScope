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
    private String bulk_extractorOutputDir;
    private String identifiedBlocksPath;
    private String identifiedBlocksExpandedPath;
    
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

        // set bulk_extractor output directory
        bulk_extractorOutputDir = jobDir + File.separator + "bulk_extractor";

        // set identified_blocks.txt path
        identifiedBlocksPath = bulk_extractorOutputDir + File.separator + "identified_blocks.txt";
        
        // set identified_blocks_expanded.txt path
        identifiedBlocksExpandedPath = bulk_extractorOutputDir + File.separator + "identified_blocks_expanded.txt";

        // create the output directories
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

        // run bulk_extractor scan
        progressBar.switchToIndeterminate();
        ProcessResult result = bulk_extractorScan();
        progressBar.switchToDeterminate(4);
        progressBar.progress(1);

        // report results depending on whether blacklist data was found
        if (result == ProcessResult.OK && new File(identifiedBlocksPath).length() > 0) {
            // run hashdb expand_identified_blocks command
            if (result == ProcessResult.OK) {
                result = expandIdentifiedBlocks();
            }

            // show source summary from identified_blocks_expanded
            if (result == ProcessResult.OK) {
                progressBar.progress(2);
//                result = showSourceSummaryString(dataSource);
                result = showSourceSummaryStringEasy(dataSource);
            }

            // add report visualization launcher
            if (result == ProcessResult.OK) {
                progressBar.progress(3);
                result = addReportVisualizationLauncher();
            }

        } else {
            // no blacklist block hashes were found
            progressBar.progress(4);
        }

        // alert if error
        if (result != ProcessResult.OK) {
            MessageNotifyUtil.Notify.show("Error processing block hash blacklist module",
                       "Block hash blacklist module failed", MessageNotifyUtil.MessageType.ERROR);
        } else {
            progressBar.progress(4);
        }
        return result;
    }

    // run bulk_extractor hashdb scanner
    private ProcessResult bulk_extractorScan() {
        // set progress type
        // in the future, get fancy and track bulk_extractor progress using switchToDeterminate(n)
        // progressBar.switchToIndeterminate();

        // configure the bulk_extractor command to execute
        List<String> commandLine = new ArrayList<>();
        commandLine.add("bulk_extractor.exe");
        commandLine.add("-E");
        commandLine.add("hashdb");
        commandLine.add("-S");
        commandLine.add("hashdb_mode=scan");
        commandLine.add("-S");
        commandLine.add("hashdb_block_size=512");
        commandLine.add("-S");
        commandLine.add("hashdb_scan_path_or_socket="+hashdbDir);
        commandLine.add("-S");
        commandLine.add("hashdb_scan_sector_size=512");
        commandLine.add("-o");
        commandLine.add(bulk_extractorOutputDir);
        commandLine.add(mediaImagePath);

        // configure the process to be executed
        ProcessBuilder processBuilder = new ProcessBuilder(commandLine);
        String stdoutPath = jobDir + File.separator + "stdout_bulk_extractor.txt";
        String stderrPath = jobDir + File.separator + "stderr_bulk_extractor.txt";
        processBuilder.redirectOutput(ProcessBuilder.Redirect.to(new File(stdoutPath)));
        processBuilder.redirectError(ProcessBuilder.Redirect.to(new File(stderrPath)));
        
        // execute the bulk_extractor process
        try {
            int status;
            status = ExecUtil.execute(processBuilder, new DataSourceIngestModuleProcessTerminator(context));
            if (status == 0) {
                logger.log(Level.INFO, "bulk_extractor completed");
            } else {
                logger.log(Level.SEVERE, "bulk_extractor failed");
                return ProcessResult.ERROR;
            }
        } catch (IOException ex) {
            logger.log(Level.SEVERE, "bulk_extractor process failed", ex);  //NON-NLS
            return ProcessResult.ERROR;
        }
        return ProcessResult.OK;
    }

    private ProcessResult expandIdentifiedBlocks() {

        // create identified_blocks_expanded.txt
        String expandIdentifiedBlocksPath;
        expandIdentifiedBlocksPath = bulk_extractorOutputDir + File.separator + "identified_blocks_expanded.txt";
        List<String> commandLine = new ArrayList<>();
        commandLine.add("hashdb.exe");
        commandLine.add("expand_identified_blocks");
        commandLine.add("-m");
        commandLine.add("0");
        commandLine.add(hashdbDir);
        commandLine.add(identifiedBlocksPath);

        // configure the process to be executed
        ProcessBuilder processBuilder = new ProcessBuilder(commandLine);
        processBuilder.redirectOutput(ProcessBuilder.Redirect.to(new File(expandIdentifiedBlocksPath)));
        processBuilder.redirectError(ProcessBuilder.Redirect.to(new File(jobDir + File.separator + "stderr_hashdb_expand.txt")));

        // execute the hashdb process
        try {
            int status = ExecUtil.execute(processBuilder, new DataSourceIngestModuleProcessTerminator(context));
            if (status == 0) {
                logger.log(Level.INFO, "hashdb expand_identified_blocks completed");
            } else {
                logger.log(Level.SEVERE, "hashdb expand_identified_blocks failed");
                return ProcessResult.ERROR;
            }
        } catch (IOException ex) {
            logger.log(Level.SEVERE, "hashdb expand_identified_blocks process failed", ex);  //NON-NLS
            return ProcessResult.ERROR;
        }

        return ProcessResult.OK;
    }

    private ProcessResult showSourceSummaryString(Content dataSource) {
        // read identified_blocks_expanded.txt into sourceMap
        IdentifiedBlocksExpandedReader reader = new IdentifiedBlocksExpandedReader(identifiedBlocksExpandedPath);
        ProcessResult result = reader.read();
        if (result != ProcessResult.OK) {
            // something went wrong
            return result;
        }

        // get source iterator
        Set<Integer> keys = reader.sourceMap.keySet();
        Iterator<Integer> it = keys.iterator();

        // iterate over sources
        int totalCount = 0;
        int totalProbativeCount = 0;
        while(it.hasNext()) {
            Integer sourceID = it.next();
            SourceData source = reader.sourceMap.get(sourceID);
            totalCount += source.count;
            totalProbativeCount += source.probativeCount;
        }
        String sourceSummaryString;
        int numSources = reader.sourceMap.keySet().size();
        if (totalCount == 1) {
            sourceSummaryString = "1 Blacklist block hash (" + totalProbativeCount + " unflagged) found in " + numSources + " sources";
        } else {
            sourceSummaryString = totalCount + " Blacklist block hashs (" + totalProbativeCount + " unflagged) found in " + numSources + " sources";
        }
        
        // send summary to message inbox
        IngestMessage message = IngestMessage.createMessage(IngestMessage.MessageType.INFO,
                              BlacklistIngestModuleFactory.getModuleName(),
                              sourceSummaryString);
        IngestServices.getInstance().postMessage(message);
 
        return ProcessResult.OK;
    }

    private ProcessResult showSourceSummaryStringEasy(Content dataSource) {
        // send summary to message inbox
        IngestMessage message = IngestMessage.createMessage(IngestMessage.MessageType.INFO,
                              BlacklistIngestModuleFactory.getModuleName(),
                              "Blacklist block hash content found.");
        IngestServices.getInstance().postMessage(message);

        return ProcessResult.OK;
    }

    // add visualization launcher if data was found
    private ProcessResult addReportVisualizationLauncher() {

        String blockViewerPath = jobDir + File.separator + "sectorscope_launcher.bat";
        String blockViewerCommand = "sectorscope.py -i \"" + bulk_extractorOutputDir + "\"";
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

