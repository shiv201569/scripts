#Script to monitor the utilization of the virtual environments. This is made compatible with Python3
#The script send out a mail to science support team giving a list of the virtual environments listed according to users with their space utilization, in a descending order by size.

import subprocess as sp
from datetime import datetime

def runCommand(cmd):
 return sp.run(cmd,shell=True,stdout=sp.PIPE)

def getDirSize(cmd):
 usr_map = dict()
 out = runCommand(cmd)
 total_map = dict()

 for line in out.stdout.decode('utf-8').split("\n"):
   line_content = line.split("\t")
   if len(line_content) < 2:
    break
   path = line_content[1]
   break_arr = path.split("/")

   if not break_arr[2] in usr_map.keys():
    usr_map[break_arr[2]] = {"ind": {},"total": ""}

   size = int(int(line_content[0])/1024)

   if break_arr[4] == "":
    usr_map[break_arr[2]]["total"] = "total: "+ str(size) + "M"
    if not break_arr[2] in total_map:
     total_map[size] = []

    total_map[size].append(break_arr[2])
   else:
    mod_date = sp.run("stat -c %y "+path,shell=True,stdout=sp.PIPE).stdout.decode('utf-8').split(".")[0]
    try:
     usr_map[break_arr[2]]["ind"][size].append(break_arr[4]+": "+str(size) + "M (" + mod_date+")")
    except KeyError:
     usr_map[break_arr[2]]["ind"][size] = []
     usr_map[break_arr[2]]["ind"][size].append(break_arr[4]+": "+str(size) + "M (" + mod_date+")")

 return (usr_map,total_map)

def sendMail(usr_map,total_map):
 body = "The below gives the details of virtual environments, their space utilization and the last access timestamp for every user, for which they exist. Please analyse the usage and alert the user(s) accordingly to take the necessary action:\n\n"
 users_email_ids = ""
 cntr = 1
 sorted_total_arr = sorted(total_map.keys(),reverse=True)

 for total_size in sorted_total_arr:
  for user in total_map[total_size]:
    body+=str(cntr)+". "+user+" - "+usr_map[user]["total"]+"\n"
    cntr2 = 1
    sorted_keys = sorted(usr_map[user]["ind"].keys(),reverse=True)
    for i in sorted_keys:
     for j in usr_map[user]["ind"][i]:
      body+="   "+str(cntr2)+". "+j+"\n"
      cntr2+=1
    body+="\n"
    cntr+=1
 #print(body)
 mail_cmd = 'echo "'+body+'" | mail -r svc_sciops@domain -s "Virtual Environments Usage Report" "ScienceEnvironmentsSupportSquad@domain.com"'
 retcode = runCommand(mail_cmd).returncode
 #print("Return Code: "+str(retcode))

if __name__ == "__main__":
 cmd = "du --max-depth=1 -t 55K /home/*/virtualenvs/"
 usr_map,total_map = getDirSize(cmd)
 if usr_map:
  sendMail(usr_map,total_map)
 else:
  print("No environment > 55K found.")
