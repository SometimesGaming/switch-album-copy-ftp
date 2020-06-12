#!/usr/bin/env python3
import os
import sys
import subprocess
import urllib.error
from urllib.request import urlopen
from urllib.parse import urlparse
from argparse import ArgumentParser, RawTextHelpFormatter

print("Author: SometimesGaming")
print("Project: https://github.com/SometimesGaming/switch-album-copy-ftp")
print("Reddit: https://old.reddit.com/user/SometimesGaming/")

# download string from url
def remoteGet(url):
	try:
		result = urlopen(url).read().decode("utf-8").strip()
		return (200, result)
	except urllib.error.URLError as e:
		return (450, None)
	except:
		return (0, None)

# downloads file from remote to local
def downloadFile(remoteFilePath, localFilePath):
	with urlopen(remoteFilePath) as remoteFile, open(localFilePath, 'wb') as localFile:
		localFile.write(remoteFile.read())

# recursively gets all files in path and subpaths
def getRemoteFileList(remotePath):
	files = []
	for line in remoteGet(remotePath)[1].splitlines():
		name = line.strip().split()[-1]  # last string is file name (will break with space in name but screenshots don't have that)
		if line[0] == 'd':  # if file is a directory
			files = files + getRemoteFileList(f"{remotePath}{name}/")
		else:
			files.append(f"{remotePath}{name}")
	return files

def initArgs():

	argsParser = ArgumentParser(description='Nintendo Switch album downloader', formatter_class=RawTextHelpFormatter)
	argsParser.add_argument('-s', '--source',  
		help="""Plug your switch FTP address here. No need for protocol but don't forget the port!
	To find your IP check your router or use GoldLeaf.
	Ex: 192.168.0.2:5000""")
	argsParser.add_argument('-d', '--destination',  
		help="""Folder where all files will be downloaded to on your PC.
	Ex: downloads
	Ex: C:\\switch\\album""")
	argsParser.add_argument('-e', '--extensions', default=["jpg", "mp4"], nargs='*',
		help="""File extensions to download.
	Default: jpg and mp4. AFAIK Switch only uses those two formats
	Ex: mp4
	Ex: jpg png""")
	argsParser.add_argument('-p', '--paths', default=["/Nintendo/Album/", "/emuMMC/RAW1/Nintendo/Album/", "/emuMMC/RAW2/Nintendo/Album/"], nargs='*',
		help="""Paths to look for in your Switch.
	Default: /Nintendo/Album/, /emuMMC/RAW1/Nintendo/Album/, /emuMMC/RAW2/Nintendo/Album/""")
	argsParser.add_argument('--overwrite', type=bool, default=False, 
		help="""If true will overwrite existing files with same name""")
	argsParser.add_argument('--delete-source', type=bool, default=False, 
		help="""If true will delete files on Switch after download""")
	return argsParser.parse_args()

args = initArgs()

SOURCE = args.source
DESTINATION = args.destination
EXTENSIONS = args.extensions
OVERWRITE = args.overwrite
DELETE_SOURCE = args.delete_source
PATHS = args.paths

files = []
for albumPath in PATHS:
	remote = f"ftp://{SOURCE}{albumPath}"
	print(f"Scanning album {remote}", end = "... ")
	try:
		remoteFiles = getRemoteFileList(remote)
		files = files + remoteFiles
		print(f"Found {len(remoteFiles)} remote files")
	except Exception:
			print(f"No files or server inaccessible")

if not OVERWRITE:
	files = [f for f in files if not os.path.isfile(f"{DESTINATION}{os.path.basename(f)}")]

if len(files) < 1:
	print("No files to download")
else:
	print(f"Preparing to download {len(files)} files")

for file in files:
	destPath = f"{DESTINATION}{os.path.basename(file)}"
	downloadFile(file, destPath)
	print("■", end='')

print("\nDone")


