"""Job Site classes.

Base JobSite class and indiviual job site child classes for supported sites.

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


class InvalidJobRecord(Exception):
    """Invalid Job Record."""
    def __init__(self, message):
        super().__init__(message)

class JobSite(object):
    """Base Job Site class."""

    _html_parser = 'html5lib'

    def __init__(self):
        self.title = "N/A"
        self.location = "N/A"
        self.recruiter = "N/A"
        self.contact = "N/A"
        self.applied = "N/A"
        self.site = "N/A"

    def get_applied_datetime(self):
        """Return datetime for applied date string."""
        return (self.convert_to_datetime(self.applied))

    def __lt__(self, other):
        return (datetime.strptime(self.applied, "%d/%m/%Y") < datetime.strptime(other.applied, "%d/%m/%Y"))

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
    def fetch_jobs(cls, html_file):
        """Create a list of job HTML details from beautiful soup to be processed."""
        raise NotImplementedError

    @classmethod
    def convert_to_datetime(cls, date):
        """Convert job date string format (DD/MM/YYYY) to datetime object."""
        return (datetime.strptime(date, '%d/%m/%Y'))

    @classmethod
    def convert_from_datetime(cls, date):
        """Convert to job date format string (DD/MM/YYYY) from datetime object."""
        return (date.strftime('%d/%m/%Y'))

    # Properties

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, location):
        self._location = location

    @property
    def recruiter(self):
        return self._recruiter

    @recruiter.setter
    def recruiter(self, recruiter):
        self._recruiter = recruiter

    @property
    def contact(self):
        return self._contact

    @contact.setter
    def contact(self, contact):
        self._contact = contact

    @property
    def applied(self):
        return self._applied

    @applied.setter
    def applied(self, applied):
        self._applied = applied

class Reed(JobSite):
    """Reed job site."""

    def __init__(self, job):
        super().__init__()
        self.site = "Reed"
        self.title = job.a['title']
        self.location = job.find('div', class_='job-location').text
        self.recruiter = job.find('span', {'data-bind': 'html: Recruiter'}).text
        self.contact = job.find('span', {'data-bind': 'html: ApplicationEmail'}).text
        self.applied = Reed._convert_date(job.find('span', {'data-bind': 'text: AppliedOn'}).text)

    @classmethod
    def fetch_jobs(cls, html_file):
        html_source = BeautifulSoup(html_file, JobSite._html_parser)
        return html_source.find_all('article', class_='job row')

    @staticmethod
    def _convert_date(date):
        """Convert applied date to DD/MM/YYYY format."""
        if 'Today' in date:
            applied_date = datetime.today()
            return JobSite.convert_from_datetime(applied_date)
        elif 'Yesterday' in date:
            applied_date = datetime.today()
            applied_date = applied_date - timedelta(days=1)
            return JobSite.convert_from_datetime(applied_date)
        elif 'days ago' in date:
            applied_date = datetime.today()
            applied_date = applied_date - timedelta(days=int(date.split(' ')[0]))
            return JobSite.convert_from_datetime(applied_date)
        elif '1 week ago' in date:
            applied_date = datetime.today()
            applied_date = applied_date - timedelta(days=7)
            return JobSite.convert_from_datetime(applied_date)
        else:
            applied_date = datetime.strptime(date, '%d %B %Y')
            return JobSite.convert_from_datetime(applied_date)


class ComputerWeekly(JobSite):
    """Computer Weekly job site."""

    def __init__(self, job):
        super().__init__()
        self.site = "Computer Weekly"
        job_details = job.find_all('div', class_='col-xs-7')
        self.title = job.find('a').text
        self.recruiter = job_details[2].p.text
        self.applied = job_details[1].p.text.split(' ')[0]

    @classmethod
    def fetch_jobs(cls, html_file):
        html_source = BeautifulSoup(html_file, JobSite._html_parser)
        return html_source.find_all('div', class_='col-xs-12 col-sm-9')


class CVLibrary(JobSite):
    """CV Library Job site."""

    def __init__(self, job):
        super().__init__()
        self.site = "CV Library"
        job_details = job.find_all('span')
        self.title = job.find('a', class_='apps-job-title').text
        if len(job_details) == 5:
            self.recruiter = job_details[0].text
            self.location = job_details[2].text if job_details[2].text else 'N/A'
            self.contact = job_details[3].text
            self.applied = job_details[4].text.split(' ')[0]
        elif len(job_details) == 4:  # Missing salary
            self.recruiter = job_details[0].text
            self.location = job_details[1].text if job_details[2].text else 'N/A'
            self.contact = job_details[2].text
            self.applied = job_details[3].text.split(' ')[0]
        else:
            raise InvalidJobRecord("Invalid number of fields in record job record.")

    @classmethod
    def fetch_jobs(cls, html_file):
        html_source = BeautifulSoup(html_file, JobSite._html_parser)
        return html_source.find_all('div', class_='app-card')


class FindAJob(JobSite):
    """DWP find a job site."""

    def __init__(self, job):
        super().__init__()
        self.site = "Find A Job"
        job_details = job.find_all('td')
        self.title = job_details[1].text.split('(')[0].strip()
        self.location = job_details[1].text.split('(')[1].split(',')[0].strip()
        self.recruiter = job_details[1].text.split('(')[1].split(',')[-1][:-1].strip()
        self.applied = FindAJob._convert_date(job_details[0].text)

    @classmethod
    def fetch_jobs(cls, html_file):
        html_source = BeautifulSoup(html_file, JobSite._html_parser)
        jobs_body = html_source.find('tbody')
        return jobs_body.find_all('tr')

    @staticmethod
    def _convert_date(date):
        """Convert applied date to DD/MM/YYYY format."""
        applied_date = datetime.strptime(date.split(',')[0], '%d %b %Y')
        return JobSite.convert_from_datetime(applied_date)
