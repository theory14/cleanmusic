#!/usr/bin/python
#
# Copyright (C) 2012 Chris Gordon
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

'''
Clean out certain data inserted into ID3 tags. Specifically this will remove
any Comments tags, either ID3 v1 or ID3 v2 and ID3 v2 PRIV frames.

The eyeD3 library available at http://http://eyed3.nicfit.net is required.
'''

import eyeD3
import os
import fnmatch
import argparse
import sys

class MessagePrinter(object):
    '''Prints messages (or not) based on level.
    Levels:
        SILENT:  Nothing printed.
        VERBOSE:  List files that are being cleaned.
        DEBUG:  Print out values that are about to be wacked.
    '''
    SILENT = 0
    VERBOSE = 1
    DEBUG = 2
    
    levels = [0, 1, 2]
    
    def __init__(self):
        self.level = 0
    
    def setLevel(self, newlevel):
        '''Set output level.  Initialized default is SILENT.
        Raises a ValueError if newlevel is not a valid level.'''
        if newlevel not in self.levels:
            raise ValueError('Invalid output level, ' +  str(newlevel))
        else:
            self.level = newlevel
            
    def getLevel(self):
        '''Returns the current output level.'''
        return self.level
        
    def printmsg(self, msglevel, msg):
        '''If level is >= current level, msg will be printed to stdout.'''
        if (msglevel <= self.level):
            if (msglevel >= self.DEBUG):
                print '  DEBUG:  ',
            print msg


class MP3File(object):
    '''The mp3File class uses eyeD3 classes and methods to actually modify the ID3 tags.'''
    
    def __init__(self, aFile):
        self.aFile = aFile
        self.tag = eyeD3.Tag()
        self._writeout = MessagePrinter()
        self._inTestMode = False
        
    def setMessagePrinter(self, messagePrinter):
        '''Set the MessagePrinter that will be used for printing output.  One is created
        in __init__, but results in nothing being printed (SILENT) since MessagePrinter 
        initializes to SILENT.'''
        if isinstance(messagePrinter, MessagePrinter):
            self._writeout = messagePrinter
        else:
            raise TypeError('Need a MessagePrinter object')
        
    def setTestMode(self, inTestMode):
        '''Toggle test mode on/off.  inTestMode is either True or False.'''
        if inTestMode in [ True, False]:
            self._inTestMode = inTestMode
        else:
            raise ValueError('inTestMode must be either True or False.')
        
    def getTestMode(self):
        return self._inTestMode
         
    def clean(self):
        '''Cleans both ID3_V1 and ID3_V2 data from aFile.'''
        self._writeout.printmsg(self._writeout.VERBOSE, 'Cleaning file: ' + self.aFile)
        self.cleanV1()
        self.cleanV2()
    
    def cleanV1(self):
        '''Clean just the ID3_V1 data from aFile.'''
        try:
            if (self.tag.link(self.aFile, eyeD3.ID3_V1)):
                self._showComments('ID3_V1')
                if (self._inTestMode == False):
                    self.tag.removeComments()
                    self.tag.update()
        except Exception as e:
            print >> sys.stderr, 'Problem with ID3_V1 tags in file:  ', self.aFile
            print >> sys.stderr, e
        
    def cleanV2(self):
        '''Clean just the ID3_V2 data from aFile.'''
        try:
            if (self.tag.link(self.aFile, eyeD3.ID3_V2)):
                self._showComments('ID3_V2')
                self._showPrivFrame() 
                if (self._inTestMode == False):                        
                    self.tag.removeComments()
                    self.tag.frames.removeFramesByID('PRIV')
                    self.tag.frames.removeFramesByID('COMM')
                    self.tag.update()
        except Exception as e:
            print >> sys.stderr, 'Problem with ID3_V1 tags in file:  ', self.aFile
            print >> sys.stderr, e
            
    def _showComments(self, tagType):
        if (self.tag.getComments() == []):
            self._writeout.printmsg(self._writeout.DEBUG, 'No ' + tagType + ' comments found.')
        else:
            for comment in self.tag.getComments():
                self._writeout.printmsg(self._writeout.DEBUG, tagType + ' comments:  ' + comment.comment)
                
    def _showPrivFrame(self):
        found = False  
        for frame in self.tag.frames:
            if frame.header.id == 'PRIV':
                found = True
                self._writeout.printmsg(self._writeout.DEBUG, 'ID3_V2 PRIV frame:  ' + frame.data)
        if found == False:
            self._writeout.printmsg(self._writeout.DEBUG, 'No ID3_V2 PRIV frame found.')
    
class FileList(object):
    '''Create a list of files to clean.  If pass a single file, it will hold
    just a single file.  If a directory is passed, it will recursive traverse
    the directory and create a list of all of the files.  In either case, it will
    only return files that match the given pattern (default to *.mp3)'''

    def __init__(self):
        self.fileList = []
        self.pattern = '*.mp3'

    def setPattern(self, pat):
        self.pattern = pat
        
    def getPattern(self):
        return self.pattern
    
    def getList(self):
        return self.fileList

    def appendToList(self, filePath):
        '''Add a file or directory contents (recursively) to the list.'''
        if os.path.isdir(filePath):
            self._appendToListFromDir(filePath)
        elif os.path.isfile(filePath):
            self._appendToListFromFile(filePath)
        else:
            return
    
    def _appendToListFromDir(self, path):
        for root, dirnames, filenames in os.walk(path):
            for filename in fnmatch.filter(filenames, self.pattern):
                self.fileList.append(os.path.join(root, filename))
    
    def _appendToListFromFile(self, myfile):
        if fnmatch.fnmatch(myfile, self.pattern):
            self.fileList.append(myfile)
    

if __name__ == "__main__":
    
    # process command line arguments
    parser = argparse.ArgumentParser(description="Clean tracking comments from mp3 files.", epilog="Use at your own risk as this will modify your files!")
    parser.add_argument('file', 
                    help="The path to the files that are to be cleaned. This can be directories or specific files. Multiple items may be supplied.",
                    type=str, nargs='+')
    parser.add_argument('-f', '--filter', help="Regex matching files to be cleaned.  Defaults to '*.mp3'", type=str)
    outputGroup = parser.add_mutually_exclusive_group()
    outputGroup.add_argument('-v', '--verbose', help='Enable verbose output.', action='store_true')
    outputGroup.add_argument('-d', '--debug', help='Enable debug output.', action='store_true')
    parser.add_argument('-t', '--test', help='Enable test mode. No changes are made to files in test mode.', action='store_true')
    args = parser.parse_args()
    
    #
    # Globals
    #
    myFiles = FileList()
    writer = MessagePrinter()
#    filesTotal= 0
#    filesCleaned = 0
#    filesError = 0
    
    # use args to setup things
    if args.filter:
        myFiles.setPattern(args.filter)
    if args.verbose:
        writer.setLevel(writer.VERBOSE)
    if args.debug:
        writer.setLevel(writer.DEBUG)

    for item in args.file:
        myFiles.appendToList(item)
        
    for aFile in myFiles.getList():
#        filesTotal += 1
        song = MP3File(aFile)
        song.setMessagePrinter(writer)
        if args.test:
            song.setTestMode(True)
        song.clean()
        
#    writer.printmsg(writer.VERBOSE, 'Total files:    ' + str(filesTotal))
#    writer.printmsg(writer.VERBOSE, 'Cleaned files:  ' + str(filesCleaned))
#    writer.printmsg(writer.VERBOSE, 'Total files:    ' + str(filesError))
    
    sys.exit()
    
# EOF
        