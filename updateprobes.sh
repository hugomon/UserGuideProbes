#!/bin/sh

# This is a set of commands to grep through all the InterMapper Probe files and:
# isolate all display_name and <description> ... </description> lines
# regularize them with a Python script
# Sort them into category order
# Output a set of files containing probe reference documentation

# USAGE
#   
#    sh ./updateprobe.sh [ defaults to reading built-in probes from local directory ]
#
# OUTPUTS
# 
# probetext-unsorted.txt - a file containing all the display_name and <definition> ... </definition> lines
# probetext-sorted.txt - a file containing doc lines sorted by category
# ProbeReference directory - a directory containing probe doc files, one for each category, and Probe_Index.htm

python ScanForProbeFiles.py "$1" > probetext-unsorted.txt 
sort -t"|" -k1f,1 -k2,2 -k3n,3 < probetext-sorted.txt \
python BuildProbeDocs.py ProbeReference probetext-sorted.txt Probe_Index.htm 
