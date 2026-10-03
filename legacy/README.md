# Original demonstration

stego.py is the original script, byte unchanged, kept for characterization only.
It replaces full channel bytes along a diagonal, writes a lossy JPEG, and reads the
same in-memory array. Its passcode compares strings within the same process; it
does not encrypt anything. It has no on-disk length, capacity or Unicode handling.
It launches a Windows shell command. Do not use it to store sensitive information.
Historical sample photographs and the presentation were removed from the current
tree because redistribution rights were undocumented. Existing history is unchanged.
