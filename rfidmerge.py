import os
import csv

# Replace these with your actual directory paths
DIR1 = '<??????>/shared/shortcuts'  # Directory with rfidtag files
DIR2 = '<??????>/shared/audiofolders'  # Base directory containing artist-album subdirectories
OUTPUT_CSV = 'rfid_lookup.csv'          # Name of the output CSV file

# Function to reverse the byte order of a 4-byte RFID decimal value
def reverse_rfid_bytes(rfid_str):
    """
    Takes a decimal string from one reader (e.g., '4131582762')
    and returns the byte-reversed decimal (e.g., '720585462')
    to match the other reader's output.
    """
    try:
        rfid_int = int(rfid_str)
        # Extract bytes (big-endian assumption)
        byte1 = (rfid_int >> 24) & 0xFF
        byte2 = (rfid_int >> 16) & 0xFF
        byte3 = (rfid_int >> 8)  & 0xFF
        byte4 = rfid_int         & 0xFF
        # Reassemble in reverse order (little-endian)
        reversed_int = (byte4 << 24) | (byte3 << 16) | (byte2 << 8) | byte1
        return str(reversed_int)
    except ValueError:
        # If not a valid integer, return original (e.g., malformed filename)
        return rfid_str


# Open the CSV file for writing
with open(OUTPUT_CSV, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    # Write header
    writer.writerow(['rfidtag', 'artist-album', 'URI_info'])

    # Iterate through files in DIR1
    for filename in os.listdir(DIR1):
        file_path = os.path.join(DIR1, filename)
        if os.path.isfile(file_path):
            # Filename is rfidtag (strip extension if your files have .txt or similar)
            rfidtag_original = os.path.splitext(filename)[0]

            # Apply the byte reversal
            rfidtag_reversed = reverse_rfid_bytes(rfidtag_original)

            # Pad to exactly 10 digits with leading zeros
            rfidtag = rfidtag_reversed.zfill(10)

            # Read artist-album from file contents
            with open(file_path, 'r') as f:
                artist_album = f.read().strip()

            # Construct path to artist-album subdirectory in DIR2
            subdir_path = os.path.join(DIR2, artist_album)

            # Check if subdirectory exists
            if os.path.isdir(subdir_path):
                spotify_path = os.path.join(subdir_path, 'spotify.txt')

                # Check if spotify.txt exists
                if os.path.isfile(spotify_path):
                    # Read URI_info from spotify.txt
                    with open(spotify_path, 'r') as f:
                        uri_info = f"tidal://album/{f.read().strip()[12:]}"   # Remove tidal:album: from beginning of sting and change to correct format

                    # Write row to CSV with padded 10-digit rfidtag
                    writer.writerow([rfidtag, uri_info, artist_album])
                else:
                    print(f"Warning: spotify.txt not found in {subdir_path}")
            else:
                print(f"Warning: Subdirectory {artist_album} not found in {DIR2}")
        else:
            print(f"Warning: Skipping non-file {filename} in {DIR1}")

print(f"CSV file '{OUTPUT_CSV}' created successfully.")
