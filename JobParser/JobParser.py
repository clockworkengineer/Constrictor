from bs4 import BeautifulSoup
import requests
import csv


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
        self.applied = job.find('span', {'data-bind': 'text: AppliedOn'}).text

    @staticmethod
    def fetch_raw_jobs(html_file):
        html_source = BeautifulSoup(html_file, 'html5lib')
        return (html_source.find_all('article', class_='job row'))


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


with open('reed.html') as html_file:
    csv_file = open('reed.csv', 'w')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['title', 'location', 'recruiter', 'contact/ref.', 'date applied)'])
    for job in ReedJobDetails.fetch_raw_jobs(html_file):
        reed_job = ReedJobDetails(job)
        csv_writer.writerow([reed_job.title, reed_job.location, reed_job.recruiter, reed_job.contact, reed_job.applied])
        print(reed_job.title)
    csv_file.close()

with open('cwjobs.html') as html_file:
    csv_file = open('cwjobs.csv', 'w')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['title', 'location', 'recruiter', 'contact/ref.', 'date applied)'])
    for job in CWJobDetails.fetch_raw_jobs(html_file):
        cw_job = CWJobDetails(job)
        csv_writer.writerow([cw_job.title, cw_job.location, cw_job.recruiter, cw_job.contact, cw_job.applied])
        print(cw_job.title)
    csv_file.close()

with open('cvlibrary.html') as html_file:
    csv_file = open('cvlibrary.csv', 'w')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['title', 'location', 'recruiter', 'contact/ref.', 'date applied)'])
    for job in CVLibraryJobDetails.fetch_raw_jobs(html_file):
        cw_job = CVLibraryJobDetails(job)
        csv_writer.writerow([cw_job.title, cw_job.location, cw_job.recruiter, cw_job.contact, cw_job.applied])
        print(cw_job.title)
    csv_file.close()
