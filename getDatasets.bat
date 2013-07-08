echo off
ScanProbeFilesForDatasets.py
sort datasets-unsorted.txt > datasets-sorted.txt
BuildDatasetTable.py nothing datasets-sorted.txt datasetpage
CheckXML.py datasetpage
Pause