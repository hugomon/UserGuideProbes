# ReadMe file for InterMapper Probe Reference

[InterMapper](http://intermapper.com) has a set of built in *probes* (software plug-ins) that control how a device can be tested.

This repository contains programs and scripts that create a set of HTML documents that displays the <definition> section of each of the builtin probes to provide a reference to that probe's use. This fileset, contained in a ProbeReference folder, can be diff'd to see what probes have changed from version to version. 

To run this set of scripts:
- Expand a current copy of BuiltinProbes.zip file (from InterMapper Settings/Probes) for a new version of the built-in probes. Copy these files into the "Builtin Probes" directory of this repository.

- Make sure that the directory containing the scripts contains a folder called "BuiltinProbes" containing the source probes, and a folder called "ProbeReference" to contain the output files.

- Run the updateprobes.sh script ("sh updateprobes.sh") or updateprobes.bat (Windows) with no arguments to build a new set of Probe Reference docs, based on the built-in probes included in this repository.

Notes:
- The updateprobes.sh and updateprobes.bat scripts takes no arguments. 
- ScanForProbes.py scans the BuiltinProbes folder, extracts the information from each file, and creates a text file with the default name of "probetext-unsorted.txt".
- The shell script or batch file sorts it into "probetext-sorted.txt".
- BuildProbeDocs.py builds the doc set from the sorted probe file, writing the HTML output files (one for each category) to the ProbeReference folder. It also creates a file called "Probe_Index.htm" containing a list of the probes by category, with a link to each probe's documentation.
- CheckXML.py scans the resulting fileset for well-formed XML.

## Requirements
- Windows or Unix/Linux platform
- Reasonably modern Python (tested with Python 2.7.1)
