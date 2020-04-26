from crontab import *
import sys

cron = CronTab(user='jlionwg')

found = False
for j in cron.find_command(sys.executable+" leetcode_to_github.py"): #need to get full path of file too
    found = True
    job = j

if not found:
    job = cron.new(command=sys.executable+" leetcode_to_github.py")

job.hour.on(0)
cron.write()





