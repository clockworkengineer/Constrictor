from bs4 import BeautifulSoup
import requests
import csv
from datetime import datetime
from datetime import timedelta

class JobDetails(object):
    def __int__(self):
        self.title = ""
        self.location = ""
        self.recruiter = ""
        self.contact = ""
        self.applied = ""


class ReedJobDetails(JobDetails):
    def __init__(self, job):
        super().__init__()
        self.title = job.a['title']
        self.location = job.find('div', class_='job-location').text
        self.recruiter = job.find('span', {'data-bind': 'html: Recruiter'}).text
        self.contact = job.find('span', {'data-bind': 'html: ApplicationEmail'}).text
        self.applied = ReedJobDetails.convert_date(job.find('span', {'data-bind': 'text: AppliedOn'}).text)

    @staticmethod
    def fetch_raw_jobs(html_file):
        html_source = BeautifulSoup(html_file, 'html5lib')
        return (html_source.find_all('article', class_='job row'))

    @staticmethod
    def convert_date(date):
        if 'days ago' in date:
            applied_date = datetime.today();
            applied_date = applied_date - timedelta(days=int(date.split(' ')[0]))
            return (applied_date.strftime("%d/%m/%Y"))
        else:
            applied_date = datetime.strptime(date, '%d %B %Y')
            return (applied_date.strftime("%d/%m/%Y"))


class CWJobDetails(JobDetails):
    def __init__(self, job):
        super().__init__()
        job_details = job.find_all('div', class_='col-xs-7')
        self.title = job.find('a').text
        self.location = "N/A"
        self.recruiter = job_details[2].p.text
        self.contact = "N/A"
        self.applied = job_details[1].p.text.split(' ')[0]

    @staticmethod
    def fetch_raw_jobs(html_file):
        html_source = BeautifulSoup(html_file, 'html5lib')
        return (html_source.find_all('div', class_='col-xs-12 col-sm-9'))


class CVLibraryJobDetails(JobDetails):
    def __init__(self, job):
        super().__init__()
        job_details = job.find_all('span')
        self.title = job.find('a', class_='apps-job-title').text
        self.recruiter = job_details[1].text
        self.location = job_details[2].text if job_details[2].text else 'N/A'
        self.contact = job_details[3].text
        self.applied = job_details[4].text.split(' ')[0]

    @staticmethod
    def fetch_raw_jobs(html_file):
        html_source = BeautifulSoup(html_file, 'html5lib')
        return (html_source.find_all('div', class_='app-card'))


with open('robs_applied_for.csv', 'w') as csv_file:

    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['title', 'location', 'recruiter', 'contact/ref.', 'date applied)'])

    with open('reed.html') as html_file:
        for job in ReedJobDetails.fetch_raw_jobs(html_file):
            reed_job = ReedJobDetails(job)
            csv_writer.writerow(
                [reed_job.title, reed_job.location, reed_job.recruiter, reed_job.contact, reed_job.applied])
            print(reed_job.title)

    with open('cwjobs.html') as html_file:
        for job in CWJobDetails.fetch_raw_jobs(html_file):
            cvlibrary_job = CWJobDetails(job)
            csv_writer.writerow(
                [cvlibrary_job.title, cvlibrary_job.location, cvlibrary_job.recruiter, cvlibrary_job.contact,
                 cvlibrary_job.applied])
            print(cvlibrary_job.title)

    with open('cvlibrary.html') as html_file:
        for job in CVLibraryJobDetails.fetch_raw_jobs(html_file):
            cvlibrary_job = CVLibraryJobDetails(job)
            csv_writer.writerow(
                [cvlibrary_job.title, cvlibrary_job.location, cvlibrary_job.recruiter, cvlibrary_job.contact,
                 cvlibrary_job.applied])
            print(cvlibrary_job.title)
