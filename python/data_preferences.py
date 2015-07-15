class DataPreferences():
    """Contains data preferences affecting the user view.

    Attributes:
      max_hashes (int): Maximum duplicates allowed before disregarding the hash.
      skip_flagged_blocks (bool): Whether to disregard flagged hashes.
      skipped_sectors (array<int>): Sectors to skip.
      skipped_hashes (array<str>): Hashes to skip.
    """

    def __init__(self):
        self.max_hashes = 0
        self.skip_flagged_blocks = False
        self.skipped_sectors = []
        self.skipped_hashes = []

