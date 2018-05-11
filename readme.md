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

For setting up the crentials and secrets for use with the API it is suggsested that [googles quickstart guide](https://developers.google.com/drive/v3/web/quickstart/python)  be consulted.

	usage: GoogleDriveSync.py [-h] [-p POLLTIME] [-r] [-s SCOPE] [-e SECRETS]
	                          [-c CREDENTIALS] [-f FILEIDCACHE] [-t TIMEZONE]
	                          [-l LOGFILE] [-n NUMWORKERS] [-u UPLOADFOLDER]
	                          [-i IGNORELIST [IGNORELIST ...]]
	                          folder
	
	Synchronize Google Drive with a local folder
	
	positional arguments:
	  folder                Local folder
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -p POLLTIME, --polltime POLLTIME
	                        Poll time for drive sychronize in minutes
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
	  -l LOGFILE, --logfile LOGFILE
	                        All logging to file
	  -n NUMWORKERS, --numworkers NUMWORKERS
	                        Number of worker threads for downloads
	  -u UPLOADFOLDER, --uploadfolder UPLOADFOLDER
	                        Google upload folder
	  -i IGNORELIST [IGNORELIST ...], --ignorelist IGNORELIST [IGNORE