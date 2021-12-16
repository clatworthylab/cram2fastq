#!/usr/bin/env python
import argparse
import os
import re

import pandas as pd

JOBNAME = 'cram2fastq'
PRIORITY = 'team205'
GROUP = 'teichlab'


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--meta',
        help=(
            'txt/csv file containing the SANGER SAMPLE IDS as per manifest\n' +
            'as a separate line for each sample.'))
    parser.add_argument(
        '--study',
        type=str,
        help=('Study ID. This will be the name of the output folder.'))
    parser.add_argument(
        '--outpath',
        type=str,
        help=('Path to the directory holding the converted files.'))
    parser.add_argument(
        '--bulk',
        action='store_true',
        help=('If passed, assume file is bulk data rather than 10x data.'))
    parser.add_argument(
        '--DNAP',
        action='store_true',
        help=
        ('If passed, treats samples as created using semiautomated pipeline from DNAP.'
         ))
    parser.add_argument('--bsub',
                        action='store_true',
                        help=('If passed, submits as job to bsub.'))
    parser.add_argument('--queue',
                        type=str,
                        default='normal',
                        help=('bsub queue. Only works if --bsub is passed.'))
    parser.add_argument('--ncpu',
                        type=int,
                        default=1,
                        help=('bsub ncpu. Only works if --bsub is passed.'))
    parser.add_argument('--mem',
                        type=str,
                        default='8000',
                        help=('bsub memory. Only works if --bsub is passed.'))
    parser.add_argument(
        '--dryrun',
        action='store_true',
        help=('If passed, prints command rather than actually run.'))

    args = parser.parse_args()
    return args


def print_imeta(samp):
    """Create an imeta.sh file to download the files from irods."""
    os.system('printf "#!/bin/bash\\nset -e\\n\\\n" > imeta.sh')
    os.system(
        'imeta qu -z seq -d sample = {SAMPLE} and target = 1 and manual_qc = 1 >> imeta.sh'
        .format(SAMPLE=samp))
    fh = open('imeta.sh', 'r')
    string_list = fh.readlines()
    fh.close()
    out_list = []
    for i in string_list:
        if re.search('collection:', i):
            ir = re.sub('collection:', 'iget -K', i)
            ir = ir.rstrip()
            out_list.append(ir)
        elif re.search('dataObj:', i):
            ir = re.sub('dataObj: ', '/', i)
            out_list.append(ir)
        else:
            out_list.append(i)

    fh = open('imeta.sh', 'w')
    new_file_contents = "".join(out_list)
    fh.write(new_file_contents)
    fh.close()
    # remove any fastq
    os.system('sed "/.fastq.gz/d" -i imeta.sh')


def create_jobscript(SAMPLE, GROUP, PRIORITY, JOB, QUEUE, LOGPATH, MEMORY,
                     NCPU, bulk, path):
    """Create a bsub job script."""
    fh = open('bsubjob.sh', 'w')
    headers = [
        '#!/bin/bash\n',
        '#BSUB -G {GROUP}\n'.format(GROUP=GROUP),
        '#BSUB -P {PRORITY}\n'.format(PRORITY=PRIORITY),
        '#BSUB -J {JOB}\n'.format(JOB=JOBNAME),
        '#BSUB -q {QUEUE}\n'.format(QUEUE=QUEUE),
        '#BSUB -o {LOGPATH}/{SAMPLE}_%J.out\n'.format(LOGPATH=LOGPATH,
                                                      SAMPLE=SAMPLE),
        '#BSUB -n {NCPU}\n'.format(NCPU=str(NCPU)),
        '#BSUB -R "select[mem>{MEMORY}] rusage[mem={MEMORY}] span[hosts=1]" -M{MEMORY}\n'
        .format(MEMORY=MEMORY),
        '### ~~~ job script below ~~~ ###\n',
    ]
    if bulk:
        job_script = [
            'cd {OUTPATH}\n'.format(OUTPATH=path),
            'bash imeta.sh\n',
            'parallel cramfastq_bulk.sh ::: *.cram\n',
            'rename_fastq.py\n',
            'rm imeta.sh\n',
            'rm bsubjob.sh\n',
        ]
    else:
        job_script = [
            'cd {OUTPATH}\n'.format(OUTPATH=path),
            'bash imeta.sh\n',
            'parallel cramfastq.sh ::: *.cram\n',
            'rename_fastq.py\n',
            'rm imeta.sh\n',
            'rm bsubjob.sh\n',
        ]
    new_file_contents = ''.join(headers + job_script)
    fh.write(new_file_contents)
    fh.close()


def listdir_nohidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f


def print_imeta2(samp):
    """Create an imeta.sh file to download the files from irods."""
    os.system('printf "#!/bin/bash\\nset -e\\n\\\n" > imeta.sh')
    os.system(
        'imeta qu -z seq -d sample = {SAMPLE} and target = 1 and manual_qc = 1 >> imeta.sh'
        .format(SAMPLE=samp))
    fh = open('imeta.sh', 'r')
    string_list = fh.readlines()
    fh.close()
    out_list = []
    for i in string_list:
        if re.search('collection:|dataObj:', i):
            if re.search('collection: ', i):
                ir = re.sub('collection: ', '', i)
                ir = ir.rstrip()
                out_list.append(ir + '/')
            elif re.search('dataObj: ', i):
                ir = re.sub('dataObj: ', '', i)
                out_list.append(ir)
    dataObj_list = "".join(out_list).strip().split('\n')
    fh.close()
    libtype = []
    for dataObj in dataObj_list:
        meta = os.popen(
            'imeta ls -d {dataObj}'.format(dataObj=dataObj.strip())).read()
        meta_list = meta.strip().split('\n')
        attr = [
            re.sub('attribute: ', '', x).strip() for x in meta_list
            if re.search('attribute: ', x)
        ]
        val = [
            re.sub('value: ', '', x).strip() for x in meta_list
            if re.search('value:', x)
        ]
        ser = pd.Series(dict(zip(attr, val)))
        libtype.append(ser.loc['library_type'])
    if len(list(set(libtype))) == 1:
        print_imeta(samp)
    else:
        for dataObj, libt in zip(dataObj_list,
                                 [re.sub(' ', '_', x) for x in libtype]):
            if not os.path.exists(libt):
                os.makedirs(libt)
            os.system(
                'printf "#!/bin/bash\\nset -e\\n\\\niget -K {dataObj}" > '.
                format(dataObj=dataObj) + libt + '/imeta.sh')
            os.system('sed "/.fastq.gz/d" -i ' + libt + '/imeta.sh')


def create_jobscript2(SAMPLE, GROUP, PRIORITY, JOB, QUEUE, LOGPATH, MEMORY,
                      NCPU, bulk, path):
    """Create a bsub job script."""
    folders = list(listdir_nohidden(path))
    for f in folders:
        fh = open(f + '/bsubjob.sh', 'w')
        headers = [
            '#!/bin/bash\n',
            '#BSUB -G {GROUP}\n'.format(GROUP=GROUP),
            '#BSUB -P {PRORITY}\n'.format(PRORITY=PRIORITY),
            '#BSUB -J {JOB}\n'.format(JOB=JOBNAME),
            '#BSUB -q {QUEUE}\n'.format(QUEUE=QUEUE),
            '#BSUB -o {LOGPATH}/{SAMPLE}_%J.out\n'.format(LOGPATH=LOGPATH,
                                                          SAMPLE=SAMPLE),
            '#BSUB -n {NCPU}\n'.format(NCPU=str(NCPU)),
            '#BSUB -R "select[mem>{MEMORY}] rusage[mem={MEMORY}] span[hosts=1]" -M{MEMORY}\n'
            .format(MEMORY=MEMORY),
            '### ~~~ job script below ~~~ ###\n',
        ]
        job_script = [
            'cd {OUTPATH}/{FOLDER}\n'.format(OUTPATH=path, FOLDER=f),
            'bash imeta.sh\n',
            'parallel cramfastq.sh ::: *.cram\n',
            'rename_fastq.py\n',
            'rm imeta.sh\n',
            'rm bsubjob.sh\n',
        ]
        new_file_contents = ''.join(headers + job_script)
        fh.write(new_file_contents)
        fh.close()


def main():
    args = parse_args()
    wd = os.getcwd()
    logpath = wd + '/log'
    if not os.path.exists(logpath):
        os.makedirs(logpath)

    # read in the meta file
    if args.meta.endswith('.csv'):
        meta = pd.read_csv(args.meta, header=None)
    else:
        meta = pd.read_csv(args.meta, sep='\t', header=None)

    for SAMPLE in meta[0]:
        if SAMPLE != "" or pd.notnull(SAMPLE):
            cram_path = args.outpath + '/' + args.study + '/' + SAMPLE
            if not os.path.exists(cram_path):
                os.makedirs(cram_path)
            os.chdir(cram_path)
            cwd = os.getcwd()
            if args.bulk:
                cram2fastq = 'bash imeta.sh; parallel cramfastq_bulk.sh ::: *.cram; rename_fastq.py; rm imeta.sh;'
            else:
                cram2fastq = 'bash imeta.sh; parallel cramfastq.sh ::: *.cram; rename_fastq.py; rm imeta.sh;'
            if not args.DNAP:
                if args.bsub:
                    create_jobscript(SAMPLE=SAMPLE,
                                     GROUP=GROUP,
                                     PRIORITY=PRIORITY,
                                     JOB=JOBNAME,
                                     QUEUE=args.queue,
                                     LOGPATH=logpath,
                                     MEMORY=args.mem,
                                     NCPU=str(args.ncpu),
                                     bulk=args.bulk,
                                     path=cwd)
                    if (args.dryrun):
                        print('Dry run - bsub job script:\r')
                        with open('bsubjob.sh', 'r') as f:
                            print(f.read())
                    else:
                        print_imeta(SAMPLE)
                        os.system('bsub < bsubjob.sh')
                else:
                    if (args.dryrun):
                        print('Dry run - command:\r')
                        print(cram2fastq + '\r')
                    else:
                        print_imeta(SAMPLE)
                        os.system(cram2fastq)
                        os.system('rm imeta.sh')
            else:
                if args.bsub:
                    create_jobscript2(SAMPLE=SAMPLE,
                                      GROUP=GROUP,
                                      PRIORITY=PRIORITY,
                                      JOB=JOBNAME,
                                      QUEUE=args.queue,
                                      LOGPATH=logpath,
                                      MEMORY=args.mem,
                                      NCPU=str(args.ncpu),
                                      bulk=args.bulk,
                                      path=cwd)
                    folders = list(listdir_nohidden(cwd))
                    if (args.dryrun):
                        print('Dry run - bsub job script:\r')
                        for folder in folders:
                            with open(folder + '/bsubjob.sh', 'r') as f:
                                print(f.read())
                    else:
                        print_imeta2(SAMPLE)
                        for folder in folders:
                            os.system('bsub < ' + folder + '/bsubjob.sh')
                else:
                    if (args.dryrun):
                        print('Dry run - command:\r')
                        print(cram2fastq + '\r')
                    else:
                        print_imeta2(SAMPLE)
                        for folder in folders:
                            os.chdir(folder)
                            os.system(cram2fastq)
                            os.system('rm imeta.sh')
                            os.chdir(cwd)
        os.chdir(wd)

    print('\r')
    print('--------------------------------------------------------------\r')
    print('cram2fastq running parameters:\r')
    print('--------------------------------------------------------------\r')
    print('    --meta = {META}\r'.format(META=args.meta))
    print('    --study = {STUDY}\r'.format(STUDY=args.study))
    print('    --outpath = {OUTPATH}\r'.format(OUTPATH=args.outpath))
    print('    --bulk = {BULK}\r'.format(BULK=args.bulk))
    print('    --bsub = {BSUB}\r'.format(BSUB=args.bsub))
    print('    --DNAP = {DNAP}\r'.format(BSUB=args.DNAP))
    if args.bsub:
        print('    --queue = {QUEUE}\r'.format(QUEUE=args.queue))
        print('    --ncpu = {NCPU}\r'.format(NCPU=args.ncpu))
        print('    --mem = {MEM}\r'.format(MEM=args.mem))
    print('    --dryrun = {DRYRUN}\r'.format(DRYRUN=args.dryrun))
    print('--------------------------------------------------------------\r')


if __name__ == "__main__":
    main()
