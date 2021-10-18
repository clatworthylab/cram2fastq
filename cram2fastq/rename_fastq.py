#!/usr/bin/env python

import os
import re


def main():
    files = [f for f in os.listdir() if f.endswith('fastq.gz')]
    for index, file in enumerate(files):
        os.rename(file, re.sub(file.split('.cram')[0] + '.cram', SAMPLE, file))
    os.system('rm *.cram')


if __name__ == "__main__":
    main()
