# cram2fastq
[![](https://img.shields.io/pypi/v/cram2fastq?logo=PyPI)](https://pypi.org/project/cram2fastq/)

A python script to retrieve and convert crams from irods to fastq files. For internal use within the sanger HPC environment.

## Installation
```bash
pip install cram2fastq
# or
pip install git+https://github.com/clatworthylab/cram2fastq.git
```

Before using the tool, check that:

1) samtools is available on your `$PATH`. If not:
```bash
export PATH=/nfs/team297/kt16/Softwares/samtools-1.11/bin:$PATH
```

2) `REF_PATH` is set as well. If not:
```bash
export REF_PATH=/lustre/scratch117/core/sciops_repository/cram_cache/%2s/%2s/%s:/lustre/scratch118/core/sciops_repository/cram_cache/%2s/%2s/%s:URL=http:://refcache.dnapipelines.sanger.ac.uk::8000/%s
```

If setting it up for the first time, just do this once:
```bash
echo 'export PATH=/nfs/team297/kt16/Softwares/samtools-1.11/bin:$PATH' >> ~/.bashrc
echo 'export REF_PATH=/lustre/scratch117/core/sciops_repository/cram_cache/%2s/%2s/%s:/lustre/scratch118/core/sciops_repository/cram_cache/%2s/%2s/%s:URL=http:://refcache.dnapipelines.sanger.ac.uk::8000/%s' >> ~/.bashrc
source ~/.bashrc
````

## Instructions
```bash
usage: cram2fastq.py [-h] [--meta META] [--study STUDY] [--outpath OUTPATH] [--bulk] [--bsub] [--DNAP] [--queue QUEUE] [--ncpu NCPU] [--mem MEM] [--dryrun]

optional arguments:
  -h, --help         show this help message and exit
  --meta META        txt/csv file containing the SANGER SAMPLE IDS as per manifest as a separate line for each sample.
  --study STUDY      Study ID. This will be the name of the output folder.
  --outpath OUTPATH  Path to the directory holding the converted files.
  --bulk             If passed, assume file is bulk data rather than 10x data.
  --bsub             If passed, submits as job to bsub.
  --DNAP             If passed, treats samples as created using semiautomated pipeline from DNAP (i.e. same ID for GEX/TCR/BCR). Output will be separated as folders.
  --queue QUEUE      bsub queue. Only works if --bsub is passed.
  --ncpu NCPU        bsub ncpu. Only works if --bsub is passed.
  --mem MEM          bsub memory. Only works if --bsub is passed.
  --dryrun           If passed, prints command rather than actually run.
```

After installation, it is as easy as doing:
```bash
cram2fastq.py --meta sampleids.txt --study test --outpath /path/to/folder --bulk
```

Adding the `--bsub` option will submit this as a job if you have many samples to process.
```bash
cram2fastq.py --meta sampleids.txt --study test --outpath /path/to/folder --bulk --bsub
```

`sampleids.txt` is simply a single column `.txt` or `.csv` file with the sanger sample ids (no header).
The IDs should correspond to `SANGER SAMPLE ID` column in the manifest.

For example:
```
SangerSampleID00000001
SangerSampleID00000002
SangerSampleID00000003
```

## Output
Once it is all finished, a folder (with the name as whatever you provide for `--study`) will be created under `--outpath` with the appropriate `.cram` files converted to `.fastq.gz` files.
