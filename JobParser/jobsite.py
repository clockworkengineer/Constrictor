#!/usr/bin/env python3
"""
"""

from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta

__author__ = "Rob Tizzard"
__copyright__ = "Copyright 20018"
__credits__ = ["Rob Tizzard"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Rob Tizzard"
__email__ = "robert_tizzard@hotmail.com"
__status__ = "Pre-Alpha"


class JobSite(object):
    """Base Job Site class."""

    _date_format = '%d/%m/%Y'
    _html_parser = 'html5lib'

    def __init__(self):
        self.title = "N/A"
        self.location = "N/A"
        self.recruiter = "N/A"
        self.contact = "N/A"
        self.applied = "N/A"

    def __lt__(self, other):
        """Used in sorting."""
        return datetime.strptime(self.applied, JobSite._date_format) < datetime.strptime(other.applied,
                                                                                         JobSite._date_format)

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


class Reed(JobSite):
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
        html_source = BeautifulSoup(html_file, JobSite._html_parser)
        return html_source.find_all('article', class_='job row')

    @staticmethod
    def convert_date(date):
        """Convert applied date to DD/MM/YYYY format."""
        if 'Today' in date:
            applied_date = datetime.today()
            return applied_date.strftime(JobSite._date_format)
        elif 'Yesterday' in date:
            applied_date = datetime.today()
            applied_date = applied_date - timedelta(days=1)
            return applied_date.strftime(JobSite._date_format)
        elif 'days ago' in date:
            applied_date = datetime.today()
            applied_date = applied_date - timedelta(days=int(date.split(' ')[0]))
            return applied_date.strftime(JobSite._date_format)
        elif '1 week ago' in date:
            applied_date = datetime.today()
            applied_date = applied_date - timedelta(days=7)
            return applied_date.strftime(JobSite._date_format)
        else:
            applied_date = datetime.strptime(date, '%d %B %Y')
            return applied_date.strftime(JobSite._date_format)


class ComputerWeekly(JobSite):
    """Computer Weekly job site."""

    def __init__(self, job):
        super().__init__()
        job_details = job.find_all('div', class_='col-xs-7')
        self.title = job.find('a').text
        self.recruiter = job_details[2].p.text
        self.applied = job_details[1].p.text.split(' ')[0]

    @classmethod
    def fetch_raw_jobs(cls, html_file):
        html_source = BeautifulSoup(html_file, JobSite._html_parser)
        return html_source.find_all('div', class_='col-xs-12 col-sm-9')


class CVLibrary(JobSite):
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
        html_source = BeautifulSoup(html_file, JobSite._html_parser)
        return html_source.find_all('div', class_='app-card')


class FindAJob(JobSite):
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
        html_source = BeautifulSoup(html_file, JobSite._html_parser)
        jobs_body = html_source.find('tbody')
        return jobs_body.find_all('tr')

    @staticmethod
    def convert_date(date):
        """Convert applied date to DD/MM/YYYY format."""
        applied_date = datetime.strptime(date.split(',')[0], '%d %b %Y')
        return applied_date.strftime(JobSite._date_format)
