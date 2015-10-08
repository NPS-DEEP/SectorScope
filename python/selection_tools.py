def sources_in_range(identified_data, start_byte, stop_byte):
    """Return set of source IDs in range start_byte <= byte < stop_byte."""

    hashes = identified_data.hashes
    forensic_paths = identified_data.forensic_paths
    source_ids = set()
        
    # check sources of hashes of all forensic paths in range
    for forensic_path, block_hash in forensic_paths.items():
        offset = int(forensic_path)
        if offset >= start_byte and offset < stop_byte:

            # get source IDs associated with this hash
            (source_id_set, _) = hashes[block_hash]

            # append source IDs from this hash
            if not source_id_set.issubset(source_ids):
                source_ids = source_ids.union(source_id_set)

    return source_ids

def hashes_in_range(identified_data, start_byte, stop_byte):
    """Return set of block hashes in range start_byte <= byte < stop_byte."""

    forensic_paths = identified_data.forensic_paths
    hashes = set()
    
    # check sources of hashes of all forensic paths in range
    for forensic_path, block_hash in forensic_paths.items():
        offset = int(forensic_path)
        if offset >= start_byte and offset < stop_byte:
            hashes.add(block_hash)

    return hashes

