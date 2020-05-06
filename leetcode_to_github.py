import browsercookie
import requests
import os
from github import Github

cj = browsercookie.chrome()
sessionCSRF = ''
sessionId = ''

for cookie in cj:
    if cookie.domain == 'leetcode.com' and cookie.name=='csrftoken':
        sessionCSRF = cookie.value
    if cookie.domain == '.leetcode.com' and cookie.name=='LEETCODE_SESSION':
        sessionId = cookie.value

headers = {
        "Cookie":  'LEETCODE_SESSION=' + sessionId + ';csrftoken=' + sessionCSRF + ';',
        'X-CSRFToken': sessionCSRF,
        'X-Requested-With': 'XMLHttpRequest'
}

res = requests.get("https://leetcode.com/api/submissions/", headers=headers)
submissions = res.json()['submissions_dump']


GITHUB_KEY = open(os.path.abspath('/Users/jlionwg/Documents/Projects/leetcron/github_key')).readline()
g = Github(GITHUB_KEY)

REPO_NAME = open(os.path.abspath('/Users/jlionwg/Documents/Projects/leetcron/repo_name')).readline()
repo = g.get_repo(REPO_NAME)
lang_to_extension = {'python3':'.py'}

for sub in submissions:
    if sub['status_display'] == 'Accepted':
        filename = sub['title']+lang_to_extension[sub['lang']]
        try:
            contents = repo.get_contents(filename)
            repo.update_file(contents.path, sub['title']+' '+str(sub['timestamp']), sub['code'], contents.sha)
        except Exception:
            repo.create_file(filename, sub['title']+' '+str(sub['timestamp']), sub['code'])







