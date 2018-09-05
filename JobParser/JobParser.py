#!/usr/bin/env python3
""" Scrape applied for jobs from recruiter web pages.

Scrape downloaded web pages for applied to jobs over a period, add to a list, sort and write to a
CSV file suitable for loading into a spreedsheet. To avoid having to login into the individal recruiter
web sites the relevant pages are manually downloaded and placed into a local directory for processing.

Currently 4  web sites are supported Reed, CV Library, CW Jobs and the DWP Find a job. This code is not intended
for public use but a private tool to use for myself but it is being placed unrder GitHub anyways.

"""

from bs4 import BeautifulSoup
import random
import csv
from datetime import datetime
from datetime import timedelta
import os

__author__ = "Rob Tizzard"
__copyright__ = "Copyright 20018"
__credits__ = ["Rob Tizzard"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Rob Tizzard"
__email__ = "robert_tizzard@hotmail.com"
__status__ = "Pre-Alpha"


class JobDetails(object):
    """Base Job Details class."""

    def __init__(self):
        self.title = "N/A"
        self.location = "N/A"
        self.recruiter = "N/A"
        self.contact = "N/A"
        self.applied = "N/A"

    def __lt__(self, other):
        """Used in sorting."""
        return datetime.strptime(self.applied, "%d/%m/%Y") < datetime.strptime(other.applied, "%d/%m/%Y")

    @classmethod
    def get_job_site(cls, file_name):
        """Get job site derived class from html file name."""
        if 'reed' in file_name:
            job_site = Reed
        elif 'cwjobs' in file_name:
            job_site = ComputerWeekly
        elif 'cvlibrary' in file_name:
            job_site = CVLibrary
        elif 'findajob' in file_name:
            job_site = FindAJob
        else:
            job_site = None

        return job_site

    @classmethod
    def fetch_raw_jobs(cls, html_file):
        """Create a list of job HTML job details from beautiful soup to be processed."""
        raise NotImplementedError


class Reed(JobDetails):
    """Reed job site."""

    def __init__(self, job):
        super().__init__()
        self.title = job.a['title']
        self.location = job.find('div', class_='job-location').text
        self.recruiter = job.find('span', {'data-bind': 'html: Recruiter'}).text
        self.contact = job.find('span', {'data-bind': 'html: ApplicationEmail'}).text
        self.applied = Reed.convert_date(job.find('span', {'data-bind': 'text: AppliedOn'}).text)

    @classmethod
    def fetch_raw_jobs(cls, html_file):
        html_source = BeautifulSoup(html_file, 'html5lib')
        return html_source.find_all('article', class_='job row')

    @staticmethod
    def convert_date(date):
        """Convert applied date to DD/MM/YYYY format."""
        if 'Today' in date:
            applied_date = datetime.today()
            return applied_date.strftime("%d/%m/%Y")
        elif 'Yesterday' in date:
            applied_date = datetime.today()
            applied_date = applied_date - timedelta(days=1)
            return applied_date.strftime("%d/%m/%Y")
        elif 'days ago' in date:
            applied_date = datetime.today()
            applied_date = applied_date - timedelta(days=int(date.split(' ')[0]))
            return applied_date.strftime("%d/%m/%Y")
        elif '1 week ago' in date:
            applied_date = datetime.today()
            applied_date = applied_date - timedelta(days=7)
            return applied_date.strftime("%d/%m/%Y")
        else:
            applied_date = datetime.strptime(date, '%d %B %Y')
            return applied_date.strftime("%d/%m/%Y")


class ComputerWeekly(JobDetails):
    """Computer Weekly job site."""

    def __init__(self, job):
        super().__init__()
        job_details = job.find_all('div', class_='col-xs-7')
        self.title = job.find('a').text
        self.recruiter = job_details[2].p.text
        self.applied = job_details[1].p.text.split(' ')[0]

    @classmethod
    def fetch_raw_jobs(cls, html_file):
        html_source = BeautifulSoup(html_file, 'html5lib')
        return html_source.find_all('div', class_='col-xs-12 col-sm-9')


class CVLibrary(JobDetails):
    """CV Library Job site."""

    def __init__(self, job):
        super().__init__()
        job_details = job.find_all('span')
        self.title = job.find('a', class_='apps-job-title').text
        self.recruiter = job_details[1].text
        self.location = job_details[2].text if job_details[2].text else 'N/A'
        self.contact = job_details[3].text
        self.applied = job_details[4].text.split(' ')[0]

    @classmethod
    def fetch_raw_jobs(cls, html_file):
        html_source = BeautifulSoup(html_file, 'html5lib')
        return html_source.find_all('div', class_='app-card')


class FindAJob(JobDetails):
    """DWP find a job site."""

    def __init__(self, job):
        super().__init__()
        job_details = job.find_all('td')
        self.title = job_details[1].text.split('(')[0].strip()
        self.location = job_details[1].text.split('(')[1].split(',')[0].strip()
        self.recruiter = job_details[1].text.split('(')[1].split(',')[-1][:-1].strip()
        self.applied = FindAJob.convert_date(job_details[0].text)

    @classmethod
    def fetch_raw_jobs(cls, html_file):
        html_source = BeautifulSoup(html_file, 'html5lib')
        jobs_body = html_source.find('tbody')
        return jobs_body.find_all('tr')

    @staticmethod
    def convert_date(date):
        """Convert applied date to DD/MM/YYYY format."""
        applied_date = datetime.strptime(date.split(',')[0], '%d %b %Y')
        return applied_date.strftime("%d/%m/%Y")


def get_applied_for_jobs(source_directory):
    """Process HTML job files in turn."""

    print("Getting applied for jobs.")

    applied_for_jobs = []

    file_names = [file_name for file_name in os.listdir(source_directory)
                  if any(file_name.endswith(extention) for extention in 'html')]

    for file_name in file_names:

        job_site = JobDetails.get_job_site(file_name)

        if job_site:
            with open(file_name) as html_file:
                print("Processing {}...".format(file_name))
                for job in job_site.fetch_raw_jobs(html_file):
                    applied_for_jobs.append(job_site(job))

    return applied_for_jobs


def write_applied_for_jobs_to_file(applied_for_jobs, cutoff_date):
    """Write away CSV file."""

    print("Writing Jobs To CSV File...")

    with open('robs_applied_for.csv', 'w') as csv_file:

        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Title', 'Location', 'Recruiter', 'Contact/Ref.', 'Date Applied'])

        for job in applied_for_jobs:
            if datetime.strptime(job.applied, "%d/%m/%Y") > cutoff_date:
                csv_writer.writerow([job.title, job.location, job.recruiter, job.contact, job.applied])


####################
# Main Entry Point #
####################

def main():
    try:

        applied_for_jobs = get_applied_for_jobs(os.getcwd())
        random.shuffle(applied_for_jobs)
        write_applied_for_jobs_to_file(applied_for_jobs, datetime.today() - timedelta(weeks=2))

    except Exception as e:
        print("Error processing an input file.")
        print(e)

    print("Ended.")


if __name__ == '__main__':
    main()
