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

package edu.nps.autopsy.hashdb.blacklist;

import java.util.HashMap;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.logging.Level;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.sleuthkit.autopsy.coreutils.Logger;

import org.sleuthkit.autopsy.ingest.IngestModule.ProcessResult;
import org.sleuthkit.autopsy.ingest.IngestServices;

/**
 * Read identified_blocks_expanded.txt into data structures.
 */
public class IdentifiedBlocksExpandedReader {
    public final String identifiedBlocksExpandedPath;
    public HashMap<Integer, SourceData> sourceMap;
    private Logger logger;
    
    public IdentifiedBlocksExpandedReader(String identifiedBlocksExpandedPath) {
        this.identifiedBlocksExpandedPath = identifiedBlocksExpandedPath;
        sourceMap = new HashMap<Integer, SourceData>();
        logger = IngestServices.getInstance().getLogger(BlacklistIngestModuleFactory.getModuleName());
    }

    public ProcessResult read() {
logger.log(Level.INFO, "IdentifiedBlocksExpandedReader.a");
        try {
            // process each input line from identified_blocks_expanded.txt
            BufferedReader br;
            br = new BufferedReader(new FileReader(identifiedBlocksExpandedPath));
            String line = br.readLine();

            while (line != null) {
                // skip comment or blank
                if (line.isEmpty() || line.charAt(0) == '#') {
                    line = br.readLine();
                    continue;
                }

                // split line into its three parts
                String[] parts = line.split("\t");
                if (parts.length != 3) {
                    // invalid line
                    logger.log(Level.SEVERE, "Error processing file " + identifiedBlocksExpandedPath +
                                             " line '" + line + "'");
                    return ProcessResult.ERROR;
                }

                // parse the JSON part
                try {
                    // drill down to the sources array
                    JSONArray jsonArray = new JSONArray(parts[2]);
                    JSONObject jsonObject = jsonArray.getJSONObject(1);
                    JSONArray jsonSources = jsonObject.getJSONArray("sources");

                    for (int i=0; i < jsonSources.length(); i++) {
                        JSONObject jsonSource = jsonSources.getJSONObject(i);

                        // get source ID
                        Integer sourceID = new Integer(jsonSource.getInt("source_id"));

                        // add source to map if new
                        if (!sourceMap.containsKey(sourceID)) {
                            SourceData sourceData = new SourceData(
                                  jsonSource.getString("repository_name"),
                                  jsonSource.getString("filename"),
                                  jsonSource.getInt("filesize"),
                                  jsonSource.getString("file_hashdigest")
                            );
                            sourceMap.put(sourceID, sourceData);
                        }

                        // increment count values
                        SourceData data = sourceMap.get(sourceID);
                        data.count++;
                        if (!jsonSource.has("label")) {
                            data.probativeCount++;
                        }
                    }
                } catch (JSONException e) {
                    // a syntax error in the generated input file is bad
                    logger.log(Level.SEVERE, "json parse error in identified_blocks_ranked for line '"
                                                               + line + "'", e);
                    return ProcessResult.ERROR;
                }
                line = br.readLine();
            }

        } catch (IOException ex) {
            logger.log(Level.SEVERE, "hashdb read file failed", ex);  //NON-NLS
            return ProcessResult.ERROR;
        }
        return ProcessResult.OK;
    }
}

