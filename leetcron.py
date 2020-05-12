from crontab import CronTab
import sys
import os
import browsercookie
import json
import getpass
import requests
from github import Github

def getCookie():
    """
    Get cookie of Leetcode session from Chrome or Firefox
    """
    cj = browsercookie.load()
    sessionCSRF = ''
    sessionID = ''

    for cookie in cj:
        if cookie.domain == 'leetcode.com' and cookie.name=='csrftoken':
            sessionCSRF = cookie.value
        if cookie.domain == '.leetcode.com' and cookie.name=='LEETCODE_SESSION':
            sessionID = cookie.value
    
    if not sessionCSRF or not sessionID:
        print('ERROR: Cannot find cookies.')
        print('Are you sure you are logged into leetcode in Chrome or Firefox?')
        return
    
    with open(os.path.abspath("config.json"), "r") as jsonFile:
        data = json.load(jsonFile)

    data["LEETCODE_COOKIE"]["sessionCSRF"] = sessionCSRF
    data["LEETCODE_COOKIE"]["sessionID"] = sessionID

    with open(os.path.abspath("config.json"), "w") as jsonFile:
        json.dump(data, jsonFile)

def setupGithub():
    """
    Set up tool with Github Key and Github repo name
    """
    with open(os.path.abspath("config.json"), "r") as jsonFile:
        data = json.load(jsonFile)
    
    username = input("Github Username: ")
    token = input("Github Access Token: ")
    r = requests.get('https://api.github.com', auth=(username, token))

    while r.status_code != 200:
        print('Invalid credentials. Please try again.')
        username = input("Github Username: ")
        token = input("Github Access Token: ")
        r = requests.get('https://api.github.com', auth=(username, token))
    
    repo = input("Repo for Leetcode files: ")
    r = requests.get("https://api.github.com/repos/"+username+"/"+repo, auth=(username, token))
    while r.status_code != 200:
        toCreate = input('This repository does not exist yet. Do you want leetcron to create it for you? (Y/N)')
        
        if toCreate.upper() == 'Y' or toCreate.lower() == 'yes':

            isPrivate = input('Do you want the repository to be private? (Y/N)')
            while isPrivate.lower() not in ['y', 'n', 'yes', 'no']:
                print('Invalid input.')
                isPrivate = input('Do you want the repository to be private? (Y/N)')

            if isPrivate.upper() == 'Y' or isPrivate.lower() == 'yes':
                isPrivate = True
            else:
                isPrivate = False
            
            g = Github(token)
            g.get_user().create_repo(repo, private = isPrivate)
            r = requests.get("https://api.github.com/repos/"+username+"/"+repo, auth=(username, token))
            if r.status_code == 200:
                print('Repo successfully created!')
                break
            else:
                print('Something went wrong. Please try again later or set up the repo manually.')
                break
        else:
            print('Please input the correct repository name.')
            repo = input("Repo for Leetcode files: ")
            r = requests.get("https://api.github.com/repos/"+username+"/"+repo, auth=(username, token))
    
    data["GITHUB"]["username"] = username
    data["GITHUB"]["token"] = token
    data["GITHUB"]["repo"] = repo

    with open(os.path.abspath("config.json"), "w") as jsonFile:
        json.dump(data, jsonFile)
    
    print('Github setup successful.')

def setCronJob():
    """
    Create or update the cron job that runs leetcode_to_github.py
    """
    cron = CronTab(user=getpass.getuser())

    found = False
    for j in cron.find_command(sys.executable+" "+os.path.abspath("leetcode_to_github.py")): #need to get full path of file too
        found = True
        job = j

    if not found:
        job = cron.new(command=sys.executable+" "+os.path.abspath("leetcode_to_github.py"))

    # job.hour.on(0)
    job.minute.every(2)
    cron.write()

if __name__ == "__main__":

    options = {
        "-g": setupGithub,
        "-c": getCookie,
        "-j": setCronJob
    }

    if len(sys.argv) == 1:
        setupGithub()
        getCookie()
        setCronJob()
        print()
        print('You are all set! A cron job for pushing your leetcode solutions to github is set up to run at 12am everyday.')
    elif len(sys.argv) >= 2:
        options[sys.argv[-1]]()






