# Constrictor Python Repository

This repository contains projects written in python in the course of learning the language (just 3.6 for the moment). Please forgive any bad practices, style faux pas or just incorrect code.

### [File Processing Engine (FPE)](https://github.com/clockworkengineer/Constrictor/tree/master/FPE) 

This is a Python  variant of the JavaScript/Node file processing engine. It uses the watchdog package to monitor a configured folder for files created in it and processes each file with a custom file handler script.

Current built in file handlers:

- Copy files.
- FTP copy files to an FTP server.
- Import CSV file to MySQL database table (missing for moment).
- Import CSV file to SQLite database table (missing for moment).

		usage: fpe.py [-h] [--nogui] file

		Process files copied into watch folder with a custom handler(s).

		positional arguments:
		file        JSON Configuration file

		options:
		-h, --help  show this help message and exit
		--nogui     run FPE with no user interface




	
