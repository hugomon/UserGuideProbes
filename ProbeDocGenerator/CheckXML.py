# CheckXML.py
# Very simple script checks the files in the specified folder
# for well-formed XML.
# It uses an XML parser, and outputs the parser's error if the
# the file can't be parsed.
# If there are multiple errors in the file only the first error is flagged.
import xml.parsers.expat,sys 
from glob import glob 
import os
from os.path import join, getsize
import datetime

crlf        = "\r\n"
cr          = "\r"
lf          = "\n"

 
def parsefile(file): 
    parser = xml.parsers.expat.ParserCreate() 
    parser.ParseFile(open(file, "r")) 
 

def usableFile(fname):
    '''
    check that the file name doesn't contain any useless path elements
    - anything path element staring with "." including: 
    	.hg
    	.hgignore
    	.git
    	.gitignore
    	.DS_Store
    	.index
    - CVS as the sole path element
    - xxxx.zip as a suffix
    - "MIB_Viewers" and "MIB Viewers" - they never contain anything interesting
    Returns true if none of these patterns match
    '''
    if fname.find(os.sep + ".") != -1:
        return False
    if fname.find(os.sep + "CVS" + os.sep) != -1:
    	return False
    if fname.find(os.sep + "MIB Viewers" + os.sep) != -1:
    	return False
    if fname.find(os.sep + "MIB_Viewers" + os.sep) != -1:
    	return False
    if fname.find(".zip") == (len(fname) - 4):
#        print "File: '%s'" % fname
#    	print "***File: '%s', Len: %d, Match: %d" % (fname, len(fname), fname.find(".zip"))
    	return False
    return True


def main(argv=None):

    # path = './'
    # infile = 'com.dartware.email.imap.txt'
    # ProcessProbeFile(path, infile)

    args = sys.argv[1:]                     # retrieve the arguments
    if len(args) == 0:                      # handle missing argument
        arg = ""
    else:
        arg = args[0]
    
    docpath = arg                           # use the argument that was passed in
    wd = os.getcwd()                        # get the working directory
    if docpath == "":			    # no argument: build path to local copy of probes
        docpath = join(wd, 'ProbeReference')
    listing = []                            # listing holds files to process
    if os.path.isfile(docpath) or os.path.isfile(join(wd, docpath)):  # if it's just a filename
        listing.append(docpath)             # add it as the sole item in the list
    elif os.path.isdir(docpath):
        if docpath[-1] != os.sep:	    # make sure the path ends in separator
            docpath += os.sep
        # walk the root directory, build a list of all the non-directory files
        for root, dirs, files in os.walk(docpath):
            for name in files:
                fname = join(root, name)
                if (usableFile(fname)):
                    listing.append(name)
    else: 
        print "No such file or directory: '%s'" % docpath 
        return 1                            # return something bad


    #print listing
    
    # Print heading info with date          # add this to the head of the output file
    today = str(datetime.date.today())
    print "CheckXML.py - "+today+lf, "Checking for well-formed XML in",len(listing), "files in:"+lf+">> ", docpath, lf
    
    # listing contains a list of filenames to process
    for infile in listing:
        # print infile
        thisfile = join(docpath,infile)
        try:
            parsefile(thisfile)
            print "  - File \"%s\" is well-formed" % infile
        except Exception, e:
            print "  - File \"%s\"  is NOT well-formed!\n     - %s" % (infile, e)

    return 0
    
if __name__ == "__main__":
    sys.exit(main())
