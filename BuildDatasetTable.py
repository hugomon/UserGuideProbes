# BuildProbeDocs.py
# Uses the sorted output of ScanForProbeFiles.py
# to isolate the probe's display_name and <description>
#
# The script creates a set of HTML files compatible with MadCap's Flare help authoring tool.
# The files are stored in a directory, one file per category.
#
# It also creates a file called "Probe_Index.htm" which contains a list of
# probes, divided by category, with a link to each probe's detail.
#
# Each doc file contains a "mini-TOC" with a list of the probes in that file,
# with a link to each probe's detail.

import os
import sys
import re
import pdb

filename = ""
category = ""
crlf    = "\r\n"
cr = "\r"
lf = "\n"
backslash = "\\"
ulOpen = "<ul>"
ulClose = "</ul>"
tab = "\t"
tr = "<tr>"
trClose = "</tr>"
th = tab+"<th>"
thClose = "</th>"
col = tab+'<col />'
#catPat = re.compile(r'^(.*)"\|"')
catPat = re.compile(r'^((.*)"\|com.")')
linePat = re.compile(r'^((.*)"\|([0-9]*)\|"(.+))')

def getFlareDoc(part,title):
        hdr = ""
        ftr = ""
        hdr += '<?xml version="1.0" encoding="utf-8"?>'+lf
        hdr += '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'+lf
        hdr += '<html xmlns:MadCap="http://www.madcapsoftware.com/Schemas/MadCap.xsd" MadCap:conditions="Primary.online,Primary.print">'+lf
        hdr += '<head>'+lf
        hdr += '      <link rel="StyleSheet" href="../../../default.css" />'+lf
        hdr += '      <title>'+title+'</title>'+lf
        hdr += '</head>'+lf
        hdr += '<body>'+lf
        hdr += '<h1 class="L2">Automatically-Recorded Data Values</h1>'+lf
        hdr += '<p>The following values were selected to be recorded automatically from built-in probes.</p>'+lf
        hdr += '<table style="margin-left: 0;margin-right: auto;caption-side: top;">'+lf
        hdr += '<col style="width: 5.00em;" />'+lf+col+lf+col+lf+col+lf+col+lf+'<col style="width: 4.00em;" />'+lf
        hdr += tr+lf
        hdr += '<th style="text-align: left;vertical-align: top;background-color: #eee;">Probe Name/<br />File Name</th>'+lf
        hdr += '<th style="text-align: left;vertical-align: top;background-color: #eee;">Variable Name<br /></th>'+lf
        hdr += '<th style="text-align: left;vertical-align: top;background-color: #eee;">Tag(30)<br /></th>'+lf
        hdr += '<th style="text-align: left;vertical-align: top;background-color: #eee;">Units<br /></th>'+lf
        hdr += '<th style="text-align: left;vertical-align: top;background-color: #eee;">Legend(255)<br /></th>'+lf
        hdr += trClose+lf
        
        ftr += '</body>'+lf
        ftr += '</html>'+lf
        retstr = ""
        if part == "hdr":
                return hdr
        if part == "ftr":
                return ftr

def getTopCat(category):
        noslash = category.replace('\/','|')        
        parts = noslash.split("/")
        for i in range(len(parts)):
                parts[i] = parts[i].replace('|','/')
        filename  = parts[0].replace(" ","_")
        filename = filename.replace("-","_")
        return (filename, parts[0], filename)

def prepLinkText(text):
        nospace = text.replace(' ', '_')
        noamp = nospace.replace('&', '_')
        noslash = noamp.replace('\/','|')        
        parts = noslash.split("/")
        partcount = len(parts)
        ipart = 0
        while ipart < partcount:
                parts[ipart] = parts[ipart].replace('|','/')
                ipart += 1
        return parts

def getCloseTags(tabcount, lasttabcount):
        closetags = ""
        closetagcount = lasttabcount - tabcount
        c=0
        while c < closetagcount:
                closetags += "</ul>\n"
                c += 1
        return closetags
        
def buildLinkBlocks(infile):
        # Build a dictionary, with each entry containing a set of <li> entries,
        # one dictionary entry for each category,
        # one <li> entry for each probe file in the category.
        # This dictionary is used to build the Probe_Index.htm file and the "mini-TOC"
        # in each Probe doc file.
        linkBlocks = {}
        fi = open(infile,'r')
        thisfilename = ""
        newFilename = ""
        thisblockKey = ""
        blockKey = ""
        loopcount = 0
        tabcount = 0
        lasttabcount = 0
        tabs = "\t\t\t\t\t\t\t\t\t\t"
        lasttabcount = 0
        tabcount = 0
        while True:
                loopcount += 1
                aLine = fi.readline()
                if aLine == "":
                        break
                aLine = aLine.replace(crlf, "")       # remove crlf
                aLine = aLine.replace(cr, "")         # remove cr
                aLine = aLine.replace(lf, "")         # remove lf
                catSplit = aLine.split("|")
                
                if len(catSplit) > 0:
                        #get the parts
                        linkparts = prepLinkText(catSplit[0])
                        partcount = len(linkparts)
                        blockIdx = catSplit[2]
                        filecontent = catSplit[3]
                        #print "partcount:", partcount
                                
                        #Create one dictionary entry for each output file
                        (newFilename, topCat, blockKey) = getTopCat(catSplit[0])
                        if blockIdx == "00": #line contains link to probe doc
                                if linkBlocks.has_key(blockKey):
                                        linkBlocks[blockKey] = linkBlocks[blockKey]+filecontent+lf
                                else:
                                        linkBlocks[blockKey] = filecontent+lf
                                        continue
                                #if we're already in the block, write the LI and move on
                                if thisblockKey == blockKey:
                                        if linkBlocks.has_key(thisblockKey):
                                                linkBlocks[thisblockKey] = linkBlocks[thisblockKey]+filecontent+lf

                                if thisblockKey != blockKey: #Starting new category
                                        #print "keys don't match: this=", thisblockKey, "that=", blockKey, lf, linkBlocks.keys()
                                        bkeytest = linkBlocks.has_key(blockKey)
                                        tbkeytest = linkBlocks.has_key(thisblockKey)
                                        if bkeytest is not True:
                                                linkBlocks[blockKey] = ulOpen+lf+filecontent+lf
                                                thisblockKey = blockKey
                                                thisfilename = newFilename
                                                
                                                
                                        if tbkeytest is True  and bkeytest is not True:
                                                linkBlocks[thisblockKey] = linkBlocks[thisblockKey]+lf+ulClose+lf

        if linkBlocks.has_key(thisblockKey):
                linkBlocks[thisblockKey] = linkBlocks[thisblockKey]+ulClose+lf
        return linkBlocks

                
                
#main routine
# Assume sorted file
# default infile = 'probetext-sorted.txt'

args = sys.argv[1:]                      # retrieve the arguments
if len(args) == 0:                       # handle missing argument
        arg1 = ""
        arg2 = ""
        arg3 = ""

else:
        arg1 = args[0]
        arg2 = args[1]
        arg3 = args[2]

probedocpath = arg1                      # use the argument that was passed in
probeinfile = arg2                       # use the argument that was passed in
thisdocpath = arg3                    # use the argument that was passed in

wd = os.getcwd()                         # get the working directory

if thisdocpath == "":                                          # no argument: build path to local copy of probes
        thisdocpath = wd+backslash+"datasetpage"
else:
        thisdocpath = wd+backslash+thisdocpath

thisdocfile = thisdocpath+backslash+"dartwareprobedata.htm"

#print wd
if probedocpath == "":                                          # no argument: build path to local copy of probes
        probedocpath = wd+backslash+thisdocpath
else:
        probedocpath = wd+backslash+thisdocpath
        

if probeinfile == "":                                           # no argument: build path to local copy of probes
        probeinfile = 'datasets-sorted.txt'
else:
        probeinfile = wd+backslash+probeinfile


#print probedocpath, lf, probeinfile, lf, probeindexfile
ulBlocks = buildLinkBlocks(probeinfile)
ulblockkeys = ulBlocks.keys()
ulblockkeys.sort()


# pidx = open(probeindexfile, 'w')                                #initialize the index file
# pidx.write(getFlareDoc("hdr","Probe Reference Index")+lf)       #write the header content
# pidx.write("<h1 class=\"L2\">Probe Reference Index</h1>"+lf)    #start writing the file content
# for i in ulblockkeys:
#       i_ = i.replace("_"," ")
#       
#       idxfilelink = '&#160;&#160;<a href="'+i+'.htm"> view<MadCap:xref href="'+i+'.htm" target="" title="" alt="" MadCap:conditions="Primary.print" /></a>'
#       pidx.write("<h3>"+i_+idxfilelink+"</h3>"+lf+ulOpen+lf+ulBlocks[i]+ulClose+lf)
# pidx.write(getFlareDoc("ftr","")+lf)                            #write the footer content
# pidx.close()

#open the sorted output of ScanForProbeFiles.doc
f = open(probeinfile, 'r')
o = open(thisdocfile,"w")
o.write(getFlareDoc("hdr","Automatically-Recorded Data Values"))
i = 1
links = {}
thisfilename = ""
#thisdocfile = ""
idxreturnlink = '<blockquote><p><a href="Probe_Index.htm">To Probe Index<MadCap:xref href="Probe_Index.htm" ></MadCap:xref></a></p></blockquote>'
inContent = False
inULblock = False
ULblockOpen = False
lastLI = 0
currentline = 0
while True:
        # Start reading the source file
        aLine = f.readline()
        currentline += 1
        if aLine == "":
                break
        aLine = aLine.replace(crlf, "")       # remove crlf
        aLine = aLine.replace(cr, "")         # remove cr
        aLine = aLine.replace(lf, "")         # remove lf
        #Split each line at pipes, which gives you:
        #       The probe's place in heirarchy|probe's file name|line sequence number|probe doc entry
        #       The first line of each probe doc contains a sequence # of |00|. This line contains
        #       the link to that probe. This is used in the buildLinkBlocks() function.
        #       The remaining lines contain the probe doc.
        catSplit = aLine.split("|")
        if len(catSplit) > 0:
                #get the parts
                linkparts = prepLinkText(catSplit[0])
                blockIdx = catSplit[2]
                filecontent = catSplit[3]
                (newFilename, topCat, blockKey) = getTopCat(catSplit[0])
                if thisfilename != newFilename: #Starting new category
                        #print "New file name!",thisdocfile
                        if thisfilename != "":
                                #put footer on old file
                                # o = open(thisdocfile,"a")
                                if inULblock:
                                        print "Warning: Unclosed UL block at line", lastLI
                        thisfilename = newFilename
                        #newFilename += ".htm"
                        #thisdocfile = probedocpath+backslash+newFilename
                        #initialize new file
                        #o.write('<a name="'+topCat+'_top" MadCap:conditions="Primary.online"></a>'+lf)
                        #o = open(thisdocfile,"a")
                        #o.write('<h1 class="L2">'+topCat+"</h1>"+lf)
                        #o.write(ulOpen+lf+ulBlocks[blockKey]+lf+ulClose+lf)
                        #o.write(idxreturnlink+lf)
                        #o.close()
                if blockIdx == "00": #line contains link to probe doc
                        inContent = False
                        if ULblockOpen: #close UL block
                                inULblock = False
                                #filecontent = "</ul>"+lf+filecontent
                                #print "Closing UL", newFilename
                                ULblockOpen = True
                if blockIdx > "02":
                        inContent = True
                        #print "opening thisdocfile: ",thisdocfile
                        o = open(thisdocfile,"a")
                        if filecontent[:3] == "<td":
                                if filecontent == "<td></td>":
                                        # do nothing
                                        filecontent = ""
                                else:
                                        filecontent = tr+filecontent+trClose+lf        
                                print blockIdx,filecontent
                                #lastLI = currentline
                                #if ULblockOpen: 
                                #        ULblockOpen = True
                                #else:   #open UL block
                                #        inULblock = True
                                #        #filecontent =  "<!-- Opening UL "+newFilename+" -->"+lf+filecontent
                                
                                #        ULblockOpen = True
                                
                        else:
                                if ULblockOpen: #close UL block
                                        inULblock = False
                                        #filecontent =  "<!-- Closing UL "+newFilename+" -->"+lf+filecontent
                                        filecontent = filecontent+lf
                                        ULblockOpen = False
                                        
                        o.write(filecontent+lf)
                        o.close()

        else:
                category + aLine
                i += 1
f.close()
o = open(thisdocfile,"a")
o.write("</table>"+lf)
o.write(getFlareDoc("ftr","")+lf)
o.close()
print "Build complete: ", currentline, " lines"

