# Constrictor Python Repository

This repository contains projects written in python in the course of learning the language (just 3.6 for the moment). Please forgive any bad practices, style faux pas or just incorrect code.

### [File Processing Engine (FPE)](https://github.com/clockworkengineer/Constrictor/tree/master/FPE) 

This is a Python  variant of the JavaScript/Node file processing engine. It uses the watchdog package to monitor a configured folder for files created in it and processes each file with a custom file handler script. If the resursive option is configured then any folder created in the watch folder are added to to the watch list.

Current built in file handlers:

- Copy files/directory
- Import CSV file to MySQL database table.
- Import CSV file to SQLite database table.
- SFTP copy files/directory to an SSH server.

		usage: fpe.py [-h] [-n NAME] file
		
		Process files copied into watch folder with a custom handler.
		
		positional arguments:
		  file                  Configration file
		
		optional arguments:
		  -h, --help            show this help message and exit
		  -n NAME, --name NAME  File handler name



### [Google Drive Synchronizer (GoogleDriveSync)](https://github.com/clockworkengineer/Constrictor/tree/master/GoogleDriveSync)

Python program that uses Google Drive Python API so access a users drive and make a copy of it to a local folder.

		usage: GoogleDriveSync.py [-h] [-r] [-s SCOPE] [-e SECRETS] [-c CREDENTIALS]
		                          [-f FILEIDCACHE] [-t TIMEZONE]
		                          folder
		
		Synchronize Google Drive with a local folder
		
		positional arguments:
		  folder                Local folder
		
		optional arguments:
		  -h, --help            show this help message and exit
		  -r, --refresh         Refresh all files.
		  -s SCOPE, --scope SCOPE
		                        Google Drive API Scope
		  -e SECRETS, --secrets SECRETS
		                        Google API secrets file
		  -c CREDENTIALS, --credentials CREDENTIALS
		                        Google API credtials file
		  -f FILEIDCACHE, --fileidcache FILEIDCACHE
		                        File id cache json file
		  -t TIMEZONE, --timezone TIMEZONE
		                        Local timezone (pytz)