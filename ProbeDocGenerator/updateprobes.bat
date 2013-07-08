echo off
ScanForProbeFiles.py
sort  probetext-unsorted.txt > probetext-sorted.txt
BuildProbeDocs.py ProbeReference probetext-sorted.txt Probe_Index.htm
CheckXML.py ProbeReference
Pause