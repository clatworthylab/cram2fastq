from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

with open("requirements.txt", "rt", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh.readlines()]

setup(name="cram2fastq",
      version='0.0.1',
      author="zktuong",
      author_email="kt16@sanger.ac.uk",
      description="Download and convert cram-to-fastq from irods.",
      long_description=readme,
      long_description_content_type="text/markdown",
      url="https://github.com/clatworthylab/cram2fastq/",
      packages=find_packages(),
      setup_requires=["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.0"],
      install_requires=requirements,
      package_data={
          'cram2fastq': [
              'cram2fastq/bin/cramfastq.sh',
              'cram2fastq/bin/cramfastq_bulk.sh',
              'cram2fastq/bin/cramfastq_par.sh',
              'cram2fastq/bin/cramfastq_bulk_par.sh',
              'cram2fastq/bin/cram2fastq.py'
          ]
      },
      data_files=[('bin', [
          'cram2fastq/bin/cramfastq.sh',
          'cram2fastq/bin/cramfastq_bulk.sh',
          'cram2fastq/bin/cram2fastq.py',
          'cram2fastq/bin/cramfastq_par.sh',
          'cram2fastq/bin/cramfastq_bulk_par.sh',
      ])],
      include_package_data=True,
      classifiers=[
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9",
          "Programming Language :: Unix Shell",
      ],
      zip_safe=False)
