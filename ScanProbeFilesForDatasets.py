# Scan a directory of files for InterMapper probe files
# 
# Detect the probe file by the presence of <description> ... </description>
# 
# Extract the definition lines and the probe meta info which includes:
# - Probe Category (Servers Standard/HTTP & HTTPS/HTTP)
# - Probe version
# - Full probe path info
# - Flags - (Used to exclude probes flagged as "INVISIBLE")
# 

import os
from os.path import join, getsize
import sys
import re
import datetime
import time
from IMML2HTML import IMMLtoHTML

crlf        = "\r\n"
cr          = "\r"
lf          = "\n"
pTag        = '<p>'
pTagNoPrint = '<p MadCap:conditions="Primary.online">'
closepTag   = '</p>'
liTag       = '<li>'
closeliTag  = '</li>'
td = "<td>"
tdClose = "</td>"


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
#    	print "***File: '%s', Len: %d, Match: %d" % (fname, len(fname), fname.find(".zip"))
    	return False
    return True

def CleanLineEndings(aLine):

    """
    Return the line, minus any trailing CR and LF
    """
    str = aLine.replace(cr, "")       # remove cr
    str = str.replace(lf, "")         # remove lf
    return str
    
def GetProbeMetaInfo(probepath, infile):

    """
    Get the meta-info about the probe:
    Input:	
    - probepath is the directory that encloses all the probes
    - infile is the specific file to check
    
    Return: it as (display_name, filename, version)
    - display_name
    - filename including enclosing folder(s) if not at top level of probes folder
    - version

    """
    f = open(infile, 'r')
    dispPat = re.compile(r'display_name.["]?.*"(.+)"', re.I)        
    namePat = re.compile(r'human_name.["]?.*"(.+)"', re.I)  # look for "human_name"      
    versPat = re.compile(r"version[\"\']?.*?=.*[\"\']?([0-9]+\.[0-9]+)", re.I)
    flagPat = re.compile(r'.+flags.+=.+"(.+)"', re.I)

    displayName = ""
    version = ""
    humanname = ""
    flags = ""
    while displayName == "" or version == "" or flags == "":
        aLine = f.readline()
        if aLine == "":
            break
        aLine = CleanLineEndings(aLine)
        # bLine = aLine
        matches = dispPat.search(aLine)
        if matches:
            displayName = matches.group(1)
        matches = versPat.search(aLine)
        if matches:
            version = matches.group(1)
        matches = namePat.search(aLine)
        if matches:
            humanname = matches.group(1)
            #print "***Found HumanName: '%s'; human_name: '%s'" % (aLine, humanname)
        matches = flagPat.search(aLine)
        if matches:
            flags = matches.group(1)
            #print "***Found flags: '%s'; flags: '%s'" % (aLine, flags)
# 
#    else:
#        print "Fell off end of file****"
        
    f.close()
    
    if displayName == "" and humanname != "":	      # some probes don't have "display_name"
        # print "***Line: '%s'; human_name: '%s'" % (bLine, humanname)
        displayName = "Uncategorized/" + humanname    # just use the human name
    if displayName.find("/") == -1:
        displayName = "Uncategorized/" + displayName  # No category? Add "Uncategorized/"

    # clean up the path
    enclosingpath = infile[len(probepath):]
    # print "Enclosing path: '%s'" % enclosingpath
    return (displayName, enclosingpath, version, flags)


def GetDataset(infile):

    """
    Scan through the file line by line
    Find all the lines between <description> and </description>
    Change each line from IMML to HTML
    Return a list of the HTML-ized lines without line endings
    """
    f = open(infile, 'r')
    # print "Opening: '" + infile + "'<br />"

    printing = False
    notDone = True                                # set to false when we hit closing </description>
    result = []
    while notDone:
        aLine = f.readline()
        #print infile + ":" + aLine + "<br />"
        if aLine == "":
            break
        aLine = CleanLineEndings(aLine)
        bLine = aLine.lower()
        if bLine.find("<datasets>") != -1:
            aLine = ""                            # issue opening <p> tag
            printing = True                       # start handling subsequent lines
        if bLine.find("</datasets>") != -1:    # Done! issue closing </p> tag
            aLine = ""
            f.close()
            notDone = False
        if printing:
            bLine = aLine
            # resultstr += bLine
            if bLine is not None:
                result.append(bLine+lf)
    return result

def prepTableLine(dataset):
    parts = dataset.split(",")
    returnstr = ""
    includeset = False
    #print dataset
    if (len(parts) >= 3):
        parts3 = parts[3]
        parts3 = parts3.strip()
        if (parts[3] == '"false"'):
            print "dataset is false: "+dataset[1]+" "+dataset[3]
            return ""
    else:
        return ""
    for i in range(0,len(parts)):
        thispart = parts[i]
        thispart = thispart.strip()
        if i == 3: #only include the dataset if it is true, don't include this part at all
              returnstr += ""
              #returnstr += td+thispart+tdClose
        else:
            thispart = thispart.replace('"',"")
            thispart = thispart.replace("'","")
            returnstr += td+thispart+tdClose
    if returnstr == "<td></td>":
        return ""
    return returnstr

    
def prepLink(category):
    linkparts = prepLinkText(category)
    title = prepTitle(category)
    filename = linkparts[0]+".htm"
    filename = filename.replace("-","_")
    #print ("Linkparts: ", linkparts)
    targetstr = linkparts[0]+"-"
    for i in range(1,len(linkparts)):
            targetstr += linkparts[i]+"-"
    targetstr = targetstr[:-1]
    targetstr = prepTarget(targetstr)
    linkstr = filename
    linktext = linkstr.replace("_"," ")      #remove underscores in link text
    linktext = linktext.replace("&","&amp;") #replace ampersands in link text
    linkstr = linkstr.replace("(","_")       #replace Parens with underscores in link URLs
    linkstr = linkstr.replace(")","_") 
    linkstr = linkstr.replace("&","_")       #replace ampersands with underscores in link URLs
    linkstr = linkstr.replace("-","_")       #replace hyphens with underscores in link URLs
    linkstr = filename+"#"+prepTarget(targetstr)

    link = '<a href="'+linkstr+'">'+title+'<MadCap:xref href="'+linkstr+'" target="" title="" alt="" MadCap:conditions="Primary.print" /></a>'
    return link

    
def prepLinkText(text):
    #replace spaces and hyphens with underscores in link text
    text = text.replace(' ', '_')
    text = text.replace('-', '_')
    #temporarily replace forward slashes with pipes
    text = text.replace('\/','|')        
    parts = text.split("/")
    partcount = len(parts)
    ipart = 0
    while ipart < partcount:
        #restore slashes
        parts[ipart] = parts[ipart].replace('|','/')
        ipart += 1
    return parts

def prepTarget(category):
    linkparts = prepLinkText(category)
    targetstr = linkparts[0]+"-"
    for i in range(1,len(linkparts)):
            targetstr += linkparts[i]+"-"
    #replace hyphens, parens, slashes, ampersands, and dots with underscores in link URLs
    targetstr = targetstr.replace("-","_")
    targetstr = targetstr.replace("(","_")
    targetstr = targetstr.replace(")","_")
    targetstr = targetstr.replace("/","_")
    targetstr = targetstr.replace("&","_")
    targetstr = targetstr.replace(".","_")
    targetstr = targetstr[:-1]
    return targetstr

def prepTitle(category):
    parts = prepLinkText(category)
    title = parts[0]
    # replace underscores with spaces, ampersands with HTML entities,
    # separate with > to indicate heirarchy
    for i in range(1,len(parts)):
        parts[i] = parts[i].replace("_"," ")
        parts[i] = parts[i].replace("&","&amp;")
        title += " &gt; "+parts[i]
    return title.replace("_"," ")

def getTopCat(category):
    #replace slashes temporarily with pipes
    noslash = category.replace('\/','|')        
    parts = noslash.split("/")
    for i in range(len(parts)):
            parts[i] = parts[i].replace('|','/')
    #put slashes back, replace spaces and hyphens with underscores
    filename  = parts[0].replace(" ","_")
    filename = filename.replace("-","_")
    return parts[0]

def getBaseFileName(category):
    #Categories are used as filenames - condition them
    topcat = getTopCat(category)
    topcat = topcat.replace(" ","_")
    topcat = topcat.replace("-","_")
    topcat = topcat.replace("/","_")
    return topcat+".htm"
    
def ProcessProbeFile(probepath, infile, outfile):

    """
    Process each probe file:
       scan to find the file's display_name (to get its category)
       pull out the <description> section
       Append the filename and version numbers
    """
    (category, filename, version, flags) = GetProbeMetaInfo(probepath, infile)
    #stableflag = pflags
    if category == "" or version == "":              # couldn't find category or version
        # print "*** Bad News - File: %s; Category '%s'; Version '%s'" % (filename, category, version)
        return None
    datasets = GetDataset(infile)        
    if len(datasets) == 0:              # couldn't find <datasets>
        return None
    if flags == "INVISIBLE":                         #don't include INVISIBLE probes in doc
        return None
    category = category.replace("&","&amp;")
    
    #print "ProcessProbeFile: flags = ", stableflag
    
    # Output lines have the form:
    #   category|filename|0|<li href="[link to file/probe block]">category text</li>
    #       where filename = [Category level 1].htm - target comes from preplink
    #   category|filename|1|<a name=[targettext]></a><h2>category</h2>
    #   category|filename|2|<blockquote>
    #   category|filename|3| HTML-ized line1
    #   category|filename|4| HTML-ized line2
    #   ...
    #   category|filename|n-1| HTML-ized line n-2
    #   category|filename|n| </blockquote>
    myfile = open(outfile, 'a')
    myfile.write("%s|%s|%02d|%s" % (category, filename, 0, "<li>"+prepLink(category)+"</li>"+lf))
    myfile.write("%s|%s|%02d|%s" % (category, filename, 1, '<a name="'+prepTarget(category)+'"></a>'+'<h2>'+prepTitle(category)+'</h2>'+lf))
    #myfile.write("%s|%s|%02d|%s" % (category, filename, 2, "<blockquote>"+lf))
    for i in range(len(datasets)):
        tableline = prepTableLine(datasets[i])
        if tableline == "":
            tableline = ""
        else:
            if i > 1:
                myfile.write("%s|%s|%02d|%s" % (category, filename, i+2, "<td>&#160;</td>"+tableline+lf))
            else:
                myfile.write("%s|%s|%02d|%s" % (category, filename, i+2, "<td><strong>"+category+"</strong><br />"+filename+"</td>"+tableline+lf))
                

    myfile.close()
    #myfile.write("%s|%s|%02d|%s" % (category, filename, i+3, pTag+"<i>Filename: "+filename+"</i><br />"+lf))
    #myfile.write("%s|%s|%02d|%s" % (category, filename, i+4, "<i>Version: "+version+"</i>"+closepTag+lf))    
    #myfile.write("%s|%s|%02d|%s" % (category, filename, i+5, pTag+'<a href="'+getBaseFileName(category)+'">Back to Top</a>'+closepTag+lf))    
    #myfile.write("%s|%s|%02d|%s" % (category, filename, i+7, "</blockquote>"+lf))    
    

# Main Routine
# For each file from designated directory
#     Scan them for interesting meta info
#     (Category, file name, version, date last modified)
#     Retrieve the <definitions> section
#     Output the information in the proper format
def main(argv=None):

    # path = './'
    # infile = 'com.dartware.email.imap.txt'
    # ProcessProbeFile(path, infile)

    args = sys.argv[1:]                     # retrieve the arguments
    if len(args) == 0:                      # handle missing argument
        arg = ""
    else:
        arg = args[0]
    
    probepath = arg                         # use the argument that was passed in
    wd = os.getcwd()                        # get the working directory
    if probepath == "":			    # no argument: build path to local copy of probes
        probepath = join(wd, 'BuiltinProbes')
    
    listing = []                            # listing holds files to process
    if os.path.isfile(probepath) or os.path.isfile(join(wd, probepath)):  # if it's just a filename
        listing.append(probepath)           # add it as the sole item in the list
    elif os.path.isdir(probepath):
        if probepath[-1] != os.sep:	    # make sure the path ends in separator
            probepath += os.sep
        # walk the root directory, build a list of all the non-directory files
        for root, dirs, files in os.walk(probepath):
            for name in files:
                fname = join(root, name)
                if (usableFile(fname)):
                    listing.append(fname)
    else: 
        print "No such file or directory: '%s'" % probepath 
        return 1                            # return something bad

    # Print heading info with date          # add this to the head of the output file
    today = str(datetime.date.today())
    probetextNoSort = "datasets-unsorted.txt"
    # Create an empty file - originally some meta info was written.
    # This is now written in the BuildProbeDocs.py script.
    myfile = open(probetextNoSort, 'w') 
    myfile.close()
    
    # listing contains a list of filenames to process
    for infile in listing:
        ProcessProbeFile(probepath, infile, probetextNoSort)
    return 0
    myfile.close()
    
if __name__ == "__main__":
    sys.exit(main())
