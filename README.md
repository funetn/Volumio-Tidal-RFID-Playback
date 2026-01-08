# RFID-Controlled Tidal Album Player for Volumio

**Synopsis:** A Python app that plays Tidal albums using RFID tags on a Raspberry Pi running Volumio, leveraging Volumio's Tidal Connect feature.

**Background:** In 2025, I discovered the Phoniebox project, which uses Mopidy and the Mopidy-Tidal plugin to play Tidal content via RFID tags (https://github.com/MiczFlor/RPi-Jukebox-RFID). After many trials and errors involving software versions, Raspberry Pi models, and RFID readers, I eventually got it working on a Raspberry Pi 4 with a PN532 HAT and a PHAT DAC. Unfortunately, OS and software updates eventually broke the system.

I rebuilt it more carefully on a Raspberry Pi 3B with the same PN532 HAT, switching to Snapcast for audio distribution to a remote client with a PHAT DAC connected to my Monoprice whole-house amplifier.

My collection now includes ~990 Tidal albums on custom RFID-tagged “physical” albums (CD mailers with printed artwork for that vintage vinyl feel). To ensure long-term reliability and avoid the fragile Mopidy/Tidal API/Snapcast stack, I looked for a Volumio-based solution.

I have a Volumio Premium subscription and a Tidal account. Volumio supports Tidal Connect natively and can cast to supported devices, eliminating the need for Snapcast.

I found Francis Yeong’s RFID-Volumio project (https://github.com/fywk/rfid-volumio), but the Tidal URI examples didn’t work for me. Other projects (e.g., Phillip Hangg’s Bunibox) were promising but too complex for my Linux skill level.

After many iterations with various AI models (including Grok), I finally arrived at a working Python script that lets me scan an RFID tag and play the corresponding Tidal album in Volumio.

This document shares that solution so others can use or build upon it. It currently plays full albums only. There are no pause/stop controls via RFID (I control playback via the Volumio app). Scanning a new tag clears the queue and starts the new album.  This setup serves as a reliable backup to my original Phoniebox/Mopidy-Tidal system.

**Software:**
    Volumio 3.874 (as of January 2026)

**Hardware:**
    Raspberry Pi 4 Model B Rev 1.5, AJFWM 125KHz/13.56MHz Dual Frequency USB RFID Scanner (Amazon: https://www.amazon.com/dp/B0CDXXCHDL), Yarongtech 13.56MHz Round 25mm Adhesive RFID Stickers (Amazon: https://www.amazon.com/dp/B01LZYOR7P)

**Subscriptions Required**

Volumio Premium (~$6/month or $80/year as of January 2026)  
Tidal (paid account required for Tidal Connect)

**Disclaimer:** This is a hobby project provided with no warranty whatsoever. It works for me — your mileage may vary.Volumio Installation & Configuration

1) Install Volumio on your Raspberry Pi: https://volumio.com/get-started/
2) Create Volumio credentials and subscribe to Volumio Premium (your profile should show “PREMIUM” status).
3) In Settings → Sources, enable Tidal Connect and log in to your Tidal account. It should confirm “This device is connected to Tidal.”
4) (Optional) If using an external DAC: Settings → Playback → Audio Output → select your DAC.
5) Enable SSH: https://help.volumio.com/help/how-do-i-enable-ssh-connection
6) SSH into Volumio:  
   ssh volumio@<ip-address-or-hostname>.local

    Default password: volumio


**RFID Reader & Python Script Setup**

*Note*: Files placed in non-standard locations may be overwritten during Volumio updates. Keep backups!

1) Plug in the USB RFID reader.
2) Identify the input device using the following command:
   
    ls /dev/input/event*

    It will typically appear as /dev/input/event0 (or similar).

3) Create a project directory (you can rename this directory):
    cd /home
   
    sudo mkdir tidal-rfid
   
    cd tidal-rfid

4) Create the Python script (you can rename this to whatever you wish):  
    sudo nano tidal_rfid.py

5) Paste the code below (see Python Script section).

6) Edit the CONFIG SECTION near the top:  

    Verify EVENT_DEVICE matches the device from step 2.

    VOLUMIO_HOST should remain 'http://localhost:3000' if running on the same Pi.

7) Save (Ctrl+O → Enter → Ctrl+X).
8) Create the CSV lookup file:  

    sudo nano rfid_lookup.csv

    Format (one album per line):  

    RFID_TAG,tidal_uri,Artist - Album Name

    Example:  

    0966349713,tidal:album:13346481,Loverboy - Loverboy

    Supported URI formats:  

    tidal://album/13346481  
    tidal:album:13346481

    The third field (name) can be any text (no commas). All three fields are required.Tip: If you don’t know a tag’s ID, run the script — it will print unknown tags to the console.


9) Run the script:

     python3 tidal_rfid.py

    Expected output on startup:  

    Connected to Volumio!
   
    Loaded X entries from rfid_lookup.csv
   
    Listening for RFID scans on ...

When you scan a known tag the following will be displayed in the terminal:

		Scanned tag: 0966349713

		Playing: Loverboy - Loverboy

		Queue updated: 0 items

		Queue updated: 9 items

		Playback state: play The Kid Is Hot Tonite



Stop the script with Ctrl+C.  Music will continue playing in Volumio.



**Migrating your Phoniebox-Mopidy-Tidal RFID tags/enteries**

If you want to migrate your Phoniebox/Mopidy-Tidal RFID tags/album references to your new Volumio-RFID system do the following steps.  They use different methods of finding/queuing the  Tidal music.
1) From your Phoniebox/Mopidy-Tidal RPI system copy your /home/RPi-Jukebox-RFID/shared folders (shortcuts & audiofolders) to a USB drive. The "shortcut" directory should have files with the RFID as the name and inside the file the Artist-Album verbiage (or however you did things when registering the RFID card in Phoniebox).  The "audiofolders" directory MUST HAVE a "spotify.txt" file.  There might be another file and that's ok.  The "spotify.txt" file contains the Tidal album URI.
2) Copy this contents to your "Volumio-Tidal-RFID-Playback" RPI.  Note the location you copied it to.  If you are savvy you can probably skip doing this and account for the USB file location below in step 4.
3) Copy the rfidmerge.py code to the Volumio-Tidal-RFID-Playback RPI.
4) You will need to update the following based on where/if you copied the USB files to:

		'# Replace these with your actual directory paths
		DIR1 = '<directory you copied USB to>/shared/shortcuts'  # Directory with rfidtag files
		DIR2 = '<directory you copied USB to>/shared/audiofolders'  # Base directory containing artist-album subdirectories
		OUTPUT_CSV = '<location of rfid_lookup.csv>'          # Name of the output CSV file.  The Volumio-Tidal-RFID-Playback.py (or whatever you called it) variable "CSV_FILE" must point to this location/file.

5) Run rfidmerge.py to merge the 2 directories data into a valid record format for the Volumio-Tidal-RFID-Playback.
6) View the file created by the rfidmerge.py program - cat <name given in OUTPUT_CSV> and check if it looks like <rfidtagnumber>,tidal://album/<artist name - title>.
7) The 1st line of the file must have tag,uri,artist
8) The artist name - title will be the verbiage that was contained in the "spotify.txt" file.

Your file should look like this format:

		tag,uri,artist
		0966145713,tidal://album/36315974,Days of the New - II (Red Cover)
		0965994017,tidal://album/107690629,The Police - Zenyatta Mondatta


Note: Because I created by Phoniebox/Mopidy-Tidal system using a PN532 RFID reader the RFID number is different that what the USB reader was reading.  The rfidmerge.py program also converts the PN532 number to it to the USB correct number (and pads with a leaving 0 to make it 10-digits).  You can search the internet for details on why RFID tags are different between readers for more details.

The albums I've tested have successfully played using the rfidmerge.py process.  This process eliminated the need to re-register the rfid tags on the new Volumio-Tidal-RFID-Playback system saving hours/days of work.


**Caveats & Notes**

Plays full albums only (no single tracks or playlists tested).

No RFID-based pause/stop/skip — use the Volumio app or web interface.

If you encounter socketIO-related errors, install/update the required package (e.g., pip3 install python-socketio).

Keep backups of tidal_rfid.py and rfid_lookup.csv seperately from your SD Card/Volumio IMG card.

**Sources & Inspiration**

		Volumio Rest API page - https://developers.volumio.com/api/rest-api
		EbbLabs / python-tidal - https://github.com/EbbLabs/python-tidal
		python-tidal - https://gitlab.com/morguldir/python-tidal
		Tidal API-SDK Overview - https://developer.tidal.com/documentation/api-sdk/api-sdk-overview
		fywk / rfid-volumio - https://github.com/fywk/rfid-volumio
		Phillip Hangg Bunibox - https://hangg.com/2023/10/bunibox-rfid-jukebox/
		Michael Baumgärtner - https://gitmemories.com/edmw/volumio-diy
		Michael Baumgärtner - https://github.com/edmw/volumio-hid/blob/master/HID.py
		There are prob many others that I ran across doing searches (apologies if I missed you).


Thanks to everyone whose approches and ideas helped make this possible!
