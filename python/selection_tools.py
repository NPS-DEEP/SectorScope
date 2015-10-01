def sources_in_range(identified_data, start_byte, stop_byte):
    """Return set of source IDs in range start_byte <= byte < stop_byte."""

    hashes = identified_data.hashes
    forensic_paths = identified_data.forensic_paths
    source_ids = set()
        
    # optimization
    seen_hashes = set()

    # check sources of hashes of all forensic paths in range
    for forensic_path, block_hash in forensic_paths.items():
        offset = int(forensic_path)
        if offset >= start_byte and offset < stop_byte:
            # hash is in range so note its sources
            if block_hash in seen_hashes:
                # do not reprocess this hash
                continue

            # remember this hash
            seen_hashes.add(block_hash)

            # get sources associated with this hash
            sources = hashes[block_hash]

            # ignore each source associated with this hash
            for source in sources:
                source_ids.add(source["source_id"])

    return source_ids

def hashes_in_range(identified_data, start_byte, stop_byte):
    """Return set of block hashes in range start_byte <= byte < stop_byte."""

    identified_data_hashes = identified_data.hashes
    forensic_paths = identified_data.forensic_paths
    hashes = set()
    
    # check sources of hashes of all forensic paths in range
    for forensic_path, block_hash in forensic_paths.items():
        offset = int(forensic_path)
        if offset >= start_byte and offset < stop_byte:
            hashes.add(block_hash)

    return hashes

