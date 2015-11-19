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
#include <cstdlib>
#include <cstdio>
#include <string>
#include <sstream>
#include <iostream>
#include <fstream>
#include <errno.h>
#include <cassert>
#include "feature_line.hpp"

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

typedef std::set<uint64_t> source_ids_t;

class hash_attributes_t {
  public:
  uint64_t count;
  source_ids_t source_ids;
  bool has_label;
  hash_attributes_t(uint64_t p_count, const source_ids_t p_source_ids,
                    bool p_has_label) :
           count(p_count), source_ids(p_source_ids), has_label(p_has_label) {
  }

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
  std::string binary_hash;
  source_detail_t(uint64_t p_source_id,
                  const std::string& p_repository_name,
                  const std::string& p_filename,
                  uint64_t p_filesize,
                  const std::string& p_binary_hash):
           source_id(p_source_id),
           repository_name(p_repository_name), filename(p_filename),
           filesize(p_filesize), binary_hash(p_binary_hash) {
  }

typedef std::map<uint64_t, source_detail_t> source_details_t;

// ************************************************************
// json_scan_reader_t JSON reader
// ************************************************************

class json_scan_reader_t {
  public:

  bool is_valid;
  std::string error_string;
  std::string filename;
  std::ifstream in;
  forensic_paths_t* forensic_paths;
  hashes_t* hashes;
  source_details_t* source_details;

  ~json_scan_reader_t() {
    delete forensic_paths;
    delete hashes;
    delete source_details;
  }

  json_scan_reader_t(std::string p_filename) :
              is_valid(true)
              error_string("")
              filename(p_filename),
              in(filename.c_str()),
              forensic_paths(0),
              hashes(0),
              source_details(0) {

    // scan data
    forensic_paths = new forensic_paths_t()
    hashes = new hashes_t()
    source_details = new source_details_t()

    // see that the file opened
    if (!in.is_open()) {
      is_valid = false;
      std::stringstream ss;
      ss << "Cannot open " << filename << ": " << strerror(errno);
      return
    }

    // read the JSON scan input and populate the scan data
    std::string line;
    while(getline(in, line)) {

      // skip comment lines
      if (line[0] == '#') {
        // not valid
        continue;
      }

      // parse line of "offset tab hexdigest tab count"

      // find tabs
      size_t tab_index1 = line.find('\t');
      if (tab_index1 == std::string::npos) {
        continue;
      }
      size_t tab_index2 = line.find('\t', tab_index1 + 1);
      if (tab_index2 == std::string::npos) {
        continue;
      }

      // forensic path
      std::string forensic_path = line.substr(0, tab_index1);

      // feature
      std::string feature = line.substr(tab_index1+1, tab_index2 - tab_index1 - 1);

      // context
      std::string context = line.substr(tab_index2+1);

      feature_line = feature_line_t(forensic_path, feature, context);

      return;
    }

    // at eof
    at_end = true;
  }

  public:
  feature_scan_reader_t(std::string p_filename) :
              filename(p_filename),
              in(filename.c_str()) {

    // see that the file opened
    if (!in.is_open()) {
      std::cout << "Cannot open " << filename << ": " << strerror(errno) << "\n";
      exit(1);
    }

    // read the first feature
    read_feature();
  }

  feature_line_t read() {
    if (at_end) {
      // program error
      assert(0);
    }
    feature_line_t temp = feature_line;
    read_feature();
    return temp;
  }

  // at EOF
  bool at_eof() {
    return at_end;
  }
};

#endif

