import requests
import hashlib
import os.path
import os
import bz2
import time
import sys
import subprocess
import stat

def hashFile(filename):
	BLOCKSIZE = 65536
	hasher = hashlib.sha1()
	with open(filename, 'rb') as afile:
		buf = afile.read(BLOCKSIZE)
		while len(buf) > 0:
			hasher.update(buf)
			buf = afile.read(BLOCKSIZE)
	return hasher.hexdigest()

def updateFile(filename, manifest):
	if os.path.isfile(filename):
		if hashFile(filename) == manifest[filename]["hash"]:
			print(filename + " is up to date, skipping...")
		else:
			print("Downloading updated " + filename + "...")
			file = requests.get('https://cdn.toontownrewritten.com/content/' + manifest[filename]["dl"])
			with open(filename + '.bz2', 'wb') as zipped:
				zipped.write(file.content)
			with open(filename, 'wb') as newfile, open(filename + '.bz2', 'rb') as zipped:
				newfile.write(bz2.decompress(zipped.read()))
			os.remove(filename + ".bz2")
	else:
		print(filename + " doesn't exist, downloading...")
		file = requests.get('https://cdn.toontownrewritten.com/content/' + manifest[filename]["dl"])
		with open(filename + '.bz2', 'wb') as zipped:
			zipped.write(file.content)
		with open(filename, 'wb') as newfile, open(filename + '.bz2', 'rb') as zipped:
			newfile.write(bz2.decompress(zipped.read()))
		os.remove(filename + ".bz2")

def checkForUpdates():
	manifest = requests.get('https://cdn.toontownrewritten.com/content/patchmanifest.txt').json()
	print("Checking for updates...")
	files = ["TTREngine", "phase_10.mf", "phase_5.mf", "phase_6.mf", "phase_8.mf", "phase_5.5.mf",
	"phase_13.mf", "phase_12.mf", "winter.mf", "phase_3.mf", "phase_3.5.mf", "phase_11.mf",
	"phase_7.mf", "phase_9.mf", "TTRGame.vlt", "phase_4.mf"]

	for file in files:
		updateFile(file, manifest)

	os.chmod('TTREngine', os.stat('TTREngine').st_mode | stat.S_IEXEC | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

def launch(cookie, server):
	os.environ['TTR_PLAYCOOKIE'] = cookie
	os.environ['TTR_GAMESERVER'] = server
	subprocess.Popen('./TTREngine')

def delay(token):
	params = {'username': sys.argv[1], 'password': sys.argv[2], 'queueToken': token}
	delayed = 1
	while delayed:
		time.sleep(15)
		print("Still trying...")
		response = requests.post('https://www.toontownrewritten.com/api/login?format=json', params=params).json()
		if response["success"] == "true":
			launch(response["cookie"], response["gameserver"])
			delayed = 0
		else:
			print(response["banner"])
			os.exit()

checkForUpdates()

if not sys.argv[1] or not sys.argv[2]:
	print("You need to supply a username and password!")
	os.exit()

params = {'username': sys.argv[1], 'password': sys.argv[2]}

response = requests.post('https://www.toontownrewritten.com/api/login?format=json', params=params).json()

if response["success"] == "false":
	print(response["banner"])
	os.exit()

elif response["success"] == "partial":
	print("Enter the ToonGuard code emailed to you.")
	guard = input("> ")
	params['appToken'] = guard
	params['authToken'] = response["responseToken"]
	response = requests.post('https://www.toontownrewritten.com/api/login?format=json', params=params).json()

	if response["success"] == "true":
		launch(response["cookie"], response["gameserver"])
	elif response["success"] == "delayed":
		delay(response["queueToken"])
	else:
		print(response["banner"])
		os.exit()

elif response["success"] == "delayed":
	print("Game enterance delayed, trying to enter...")
	delay(response["queueToken"])

elif response["success"] == "true":
	launch(response["cookie"], response["gameserver"])
