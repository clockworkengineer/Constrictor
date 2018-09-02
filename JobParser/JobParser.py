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


class FindAJobDetails(JobDetails):
    def __init__(self, job):
        super().__init__()
        job_details = job.find_all('td')
        self.title = job_details[1].text.split('(')[0].strip()
        self.location = job_details[1].text.split('(')[1].split(',')[0].strip()
        self.recruiter = job_details[1].text.split('(')[1].split(',')[-1][:-1].strip()
        self.contact = "N/A"
        self.applied = FindAJobDetails.convert_date(job_details[0].text)

    def fetch_raw_jobs(html_file):
        html_source = BeautifulSoup(html_file, 'html5lib')
        jobs_body = html_source.find('tbody')
        return (jobs_body.find_all('tr'))

    @staticmethod
    def convert_date(date):
        applied_date = datetime.strptime(date.split(',')[0], '%d %b %Y')
        return (applied_date.strftime("%d/%m/%Y"))


class LinkedInJobDetails(JobDetails):
    def __init__(self, job):
        super().__init__()
        self.title = ""
        self.location = ""
        self.recruiter = ""
        self.contact = ""
        self.applied = ""

    def fetch_raw_jobs(self, html_file):
        html_source = BeautifulSoup(html_file, 'html5lib')
        return (None)


def get_applied_for_jobs():
    with open('robs_applied_for.csv', 'w') as csv_file:

        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['title', 'location', 'recruiter', 'contact/ref.', 'date applied)'])

        applied_for_jobs = []

        with open('reed.html') as html_file:
            print("Reed Applied Jobs...")
            for job in ReedJobDetails.fetch_raw_jobs(html_file):
                applied_for_jobs.append(ReedJobDetails(job))

        with open('cwjobs.html') as html_file:
            print("Computer Weekly Applied Jobs...")
            for job in CWJobDetails.fetch_raw_jobs(html_file):
                applied_for_jobs.append(CWJobDetails(job))

        with open('cvlibrary.html') as html_file:
            print("CV Library Applied Jobs...")
            for job in CVLibraryJobDetails.fetch_raw_jobs(html_file):
                applied_for_jobs.append(CVLibraryJobDetails(job))

        # Read linked in

        with open('findajob.html') as html_file:
            print("Find A Job Applied Jobs...")
            for job in FindAJobDetails.fetch_raw_jobs(html_file):
                applied_for_jobs.append(FindAJobDetails(job))

        # Sort list here!

        for job in applied_for_jobs:
            csv_writer.writerow([job.title, job.location, job.recruiter, job.contact, job.applied])


if __name__ == '__main__':
    get_applied_for_jobs()
