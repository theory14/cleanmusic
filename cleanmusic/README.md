# About #

This script will clean certain tags from mp3 files.  Various different tools
and services insert different tags for identification or other reasons beyond
the tags that describe the song itself (Artist, Album, Title, etc).  I don't want all 
of that cruft in my library, so I wrote this to remove it.

Specifically the script will remove the following:
* ID3 v1 Comments
* ID3 v2 Comments
* ID3 PRIV frames

When I say remove, I mean it will remove all of the above regardless of their contents.
If you want to be more discriminate, it should be fairly easy to modify the script 
to do so -- feel free to extend this.  

# Dependencies #

The eyeD3 library is required and available at [http://eyed3.nicfit.net](http://eyed3.nicfit.net "http://eyed3.nicfit.net").

# License #

Since the eyeD3 library is licensed under the GPLv2, so is this script.  See LICENSE file for the license.

# Usage #


	usage: cleanmusic.py [-h] [-f FILTER] [-v | -d] [-t] file [file ...]
	
	Clean tracking comments from mp3 files.
	
	positional arguments:
	  file                  The path to the files that are to be cleaned. This can
	                        be directories or specific files. Multiple items may
	                        be supplied.
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -f FILTER, --filter FILTER
	                        Regex matching files to be cleaned. Defaults to
	                        '*.mp3'
	  -v, --verbose         Enable verbose output.
	  -d, --debug           Enable debug output.
	  -t, --test            Enable test mode. No changes are made to files in test
	                        mode.
	
	Use at your own risk as this will modify your files!
