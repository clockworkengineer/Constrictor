#!/usr/bin/env python3
"""Scrape applied for jobs from recruiter web pages.

Scrape downloaded web pages for applied to jobs over a period, add to a list, sort and write to a
CSV file suitable for loading into a spreedsheet. To avoid having to login into the individal recruiter
web sites the relevant pages are manually downloaded and placed into a local directory for processing.

Currently 4  web sites are supported Reed, CV Library, CW Jobs and the DWP Find a job. This code is not intended
for public use but a private tool to use for myself but it is being placed unrder GitHub anyways.

"""

import argparse
import csv
from datetime import datetime
from datetime import timedelta
import os
from jobsite import JobSite, InvalidJobRecord

__author__ = "Rob Tizzard"
__copyright__ = "Copyright 20018"
__credits__ = ["Rob Tizzard"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Rob Tizzard"
__email__ = "robert_tizzard@hotmail.com"
__status__ = "Pre-Alpha"


def get_applied_for_jobs(context):
    """Process HTML job files in turn."""

    print("Getting applied for jobs.")

    applied_for_jobs = []

    file_names = [file_name for file_name in os.listdir(context.source)
                  if any(file_name.endswith(extention) for extention in 'html')]

    for file_name in file_names:

        job_site = JobSite.get_job_site(file_name)

        if job_site:
            with open(os.path.join(context.source, file_name)) as html_file:
                print("Processing {}...".format(file_name))
                for job in job_site.fetch_jobs(html_file):
                    try:
                        applied_for_jobs.append(job_site(job))
                    except InvalidJobRecord as e:
                        print(e)
                        print("Reading next record...")

        else:
            print("Invalid job file {}.".format(file_name))

    return applied_for_jobs


def write_applied_for_jobs_to_file(context, applied_for_jobs):
    """Write away CSV file."""

    print("Writing Jobs To CSV File...")

    # random.shuffle(applied_for_jobs)  # Shuffle things

    applied_for_jobs.sort(reverse=True)

    with open(context.output, 'w') as csv_file:

        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Title', 'Location', 'Recruiter', 'Contact/Ref.', 'Job Site', 'Date Applied'])

        number_of_jobs = 0;
        for job in applied_for_jobs:
            if job.get_applied_datetime() >= context.cutoff:
                csv_writer.writerow([job.title, job.location, job.recruiter, job.contact, job.site, job.applied])
                number_of_jobs += 1

        print("{} jobs applied for over the period.".format(number_of_jobs))


def load_context():
    """Load and parse command line arguments and create runtime context.

    Parse command line arguments and create runtime context. Also set any
    logging parameters passed in (just to file for the moment).

    Returns:
        context:    runtime parameters
    """

    context = None

    try:

        parser = argparse.ArgumentParser(description='crape applied for jobs from recruiter web pages')
        parser.add_argument('-s', '--source', default=os.getcwd(), help='Source folder')
        parser.add_argument('-c', '--cutoff',
                            default=JobSite.convert_from_datetime(datetime.today() - timedelta(weeks=2)),
                            help='Cutoff date')
        parser.add_argument('-o', '--output', default='jobs_applied_for.csv', help='CSV output file')

        context = parser.parse_args()

        context.cutoff = JobSite.convert_to_datetime(context.cutoff)

    except Exception as e:
        print(e)
        raise e

    return context


####################
# Main Entry Point #
####################

def main():
    try:

        context = load_context()
        applied_for_jobs = get_applied_for_jobs(context)
        write_applied_for_jobs_to_file(context, applied_for_jobs)

    except Exception as e:
        print("Error processing an input file: {}".format(e))

    print("Ended.")


if __name__ == '__main__':
    main()
