// Author:  Bruce Allen <bdallen@nps.edu>
// Created: 11/18/2015
//
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
// Released into the public domain on November 18, 2015 by Bruce Allen.

/**
 * \file
 *
 * Read JSON input from hashdb scan output into these structures:
 *
 *   forensic_paths (dict<forensic path int, hash hexcode str>):
 *     Dictionary maps forensic paths to their hash value.
 *
 *   hashes (dict<hash hexcode str, tuple<source ID set, list id offset pair,
 *     bool has_label>>).  Dictionary maps hashes to hash information.
 *
 *   source_details (dict<source ID int, dict<source metadata attributes>>):
 *     Dictionary where keys are source IDs and values are a dictionary
 *     of attributes associated with the given source as obtained from
 *     the identified_blocks_expanded.txt file.
 *
 */

#ifndef JSON_SCAN_READER_HPP
#define JSON_SCAN_READER_HPP

// Standard includes

//#include <cstdlib>
//#include <cstdio>
#include <cstdint>
#include <string>
#include <cstring>
#include <sstream>
#include <iostream>
#include <fstream>
#include <errno.h>
#include <cassert>
#include <vector>
#include <map>
#include <set>
#include "document.h"

// ************************************************************
// forensic_paths_t
// ************************************************************
typedef std::map<uint64_t, std::string> forensic_paths_t;

// ************************************************************
// hashes_t
// ************************************************************
class id_offset_pair_t {
  public:
  uint64_t source_id;
  uint64_t file_offset;
  id_offset_pair_t(uint64_t p_source_id, uint64_t p_file_offset) :
                source_id(p_source_id), file_offset(p_file_offset) {
  }
};

typedef std::vector<uint64_t> z_t;
typedef std::vector<id_offset_pair_t> id_offset_pairs_t;

typedef std::set<uint64_t> source_ids_t;

class hash_attributes_t {
  public:
  uint64_t count;
  source_ids_t source_ids;
  id_offset_pairs_t id_offset_pairs;
  bool has_label;
  hash_attributes_t(uint64_t p_count, const source_ids_t p_source_ids,
                    const id_offset_pairs_t& p_id_offset_pairs,
                    bool p_has_label) :
             count(p_count), source_ids(p_source_ids),
             id_offset_pairs(p_id_offset_pairs), has_label(p_has_label) {
  }
};

typedef std::map<std::string, hash_attributes_t> hashes_t;

// ************************************************************
// source_details_t
// ************************************************************
class source_detail_t {
  public:
  uint64_t source_id; //zz keep?
  std::string repository_name;
  std::string filename;
  uint64_t filesize;
  std::string file_hashdigest;
  source_detail_t(uint64_t p_source_id,
                  const std::string& p_repository_name,
                  const std::string& p_filename,
                  uint64_t p_filesize,
                  const std::string& p_file_hashdigest):
           source_id(p_source_id),
           repository_name(p_repository_name), filename(p_filename),
           filesize(p_filesize), file_hashdigest(p_file_hashdigest) {
  }
};

typedef std::map<uint64_t, source_detail_t> source_details_t;

// ************************************************************
// json_scan_reader_t JSON reader
// ************************************************************

class json_scan_reader_t {

  private:
  std::ifstream in;

  // do not allow copy or assignment
  json_scan_reader_t(const json_scan_reader_t&);
  json_scan_reader_t& operator=(const json_scan_reader_t&);

  public:
  bool is_valid;
  std::string error_string;
  std::string json_scan_filename;
  forensic_paths_t* forensic_paths;
  hashes_t* hashes;
  source_details_t* source_details;

  ~json_scan_reader_t() {
    delete forensic_paths;
    delete hashes;
    delete source_details;
  }

  json_scan_reader_t(std::string p_filename) :
              in(p_filename.c_str()),
              is_valid(true),
              error_string(""),
              json_scan_filename(p_filename),
              forensic_paths(0),
              hashes(0),
              source_details(0) {

    // scan data
    forensic_paths = new forensic_paths_t();
    hashes = new hashes_t();
    source_details = new source_details_t();

    // see that the file opened
    if (!in.is_open()) {
      is_valid = false;
      std::stringstream ss;
      ss << "Cannot open " << json_scan_filename << ": " << strerror(errno);
      error_string = ss.str();
      return;
    }

    // read the JSON scan input and populate the scan data
    int i = 0;
    std::string line;
    while(getline(in, line)) {
      i++;

      // skip comment lines
      if (line[0] == '#') {
        // not valid
        continue;
      }

      // parse line of "offset <tab> hexdigest <tab> source data"

      // find tabs
      size_t tab_index1 = line.find('\t');
      if (tab_index1 == std::string::npos) {
        std::cerr << "invalid line: " << line << "\n";
        continue;
      }
      size_t tab_index2 = line.find('\t', tab_index1 + 1);
      if (tab_index2 == std::string::npos) {
        std::cerr << "invalid line: " << line << "\n";
        continue;
      }

      // parse the forensic path containing the offset
      std::string forensic_path = line.substr(0, tab_index1);

      // parse the feature containing the block_hash
      std::string block_hash =
                  line.substr(tab_index1+1, tab_index2 - tab_index1 - 1);

      // append <key=offset, value=hash> to forensic_paths
      uint64_t offset = std::atol(forensic_path.c_str());
      std::pair<forensic_paths_t::iterator, bool> ret;
      ret = forensic_paths->insert(std::pair<uint64_t, std::string>(
                                                      offset, block_hash));
      if (ret.second == false) {
        std::cerr << "invalid line, path already read: " << line << "\n";
        continue;
      }

      // do not reprocess source information associated with a hash
      if (hashes->find(block_hash) != hashes->end()) {
        // hash already processed
        continue;
      }

      // parse context of json data containing source information
      std::string json_data = line.substr(tab_index2+1);

std::cout << "Starting JSON data: '" << json_data << "'\n";

      // create a source ID set for this hash
      source_ids_t source_ids;                // set
      id_offset_pairs_t id_offset_pairs;      // vector

      // parse json data into a JSON DOM document
      rapidjson::Document document;
      if (document.Parse(json_data.c_str()).HasParseError()) {
        is_valid = false;
        error_string = "Invalid JSON syntax.";
        return;
      }
      if (!document.IsObject()) {
        is_valid = false;
        error_string = "Invalid JSON object.";
        return;
      }
      assert(document.IsObject()); //zz ease this.

      const rapidjson::Value& source_part = document[1];
      const rapidjson::Value& source_list = source_part["sources"];

      // read source_ids and id_offset_pairs
      for (rapidjson::Value::ConstValueIterator it =
                              source_list.Begin();
                              it != source_list.End(); ++it) {
        const rapidjson::Value& source_item = *it;

        const uint64_t source_id = source_item["source_id"].GetUint64();

        // add source_id to source_ids set
        source_ids.insert(source_id);

        // add pair to pairs list
        uint64_t file_offset = source_item["file_offset"].GetUint64();
        id_offset_pairs.push_back(id_offset_pair_t(source_id, file_offset));

        // also store source details if first time seen
        if (source_list.HasMember("filename")) {
          std::string filename = source_list["filename"].GetString();
          std::string repository_name =
                                   source_list["repository_name"].GetString();
          uint64_t filesize = source_list["filesize"].GetUint64();
          std::string file_hashdigest =
                                   source_list["file_hashdigest"].GetString();
          source_details->insert(std::pair<uint64_t, source_detail_t>(
                    source_id, source_detail_t(source_id,
                                               repository_name, filename,
                                               filesize, file_hashdigest)));
        }
      }

      // get any hash entropy label.  For now, get this from source[0].
      bool has_label = source_list[0].HasMember("label");

      // store hash and its attributes in hashes_t
      uint64_t count = source_ids.size();
      hashes->insert(std::pair<std::string, hash_attributes_t>(block_hash,
           hash_attributes_t(count, source_ids, id_offset_pairs, has_label)));
    }
  }
};

#endif

