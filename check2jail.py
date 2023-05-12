#!/dhcommon/dhhadoop/python3-science/bin/python3.6
# This script is written to determine if any user needs to be jailed based on defaulting for more than a threshold number of days continuosly
import logging,fileinput,json,os,subprocess as sp

def getLoggerFile(log_file):
 logging.basicConfig(filename=log_file, format='%(asctime)s %(levelname)s : %(lineno)d : %(message)s', filemode='w', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
 return logging.getLogger()

def execute_cmd(cmd):
 p = sp.Popen(cmd,stdout=sp.PIPE,shell=True)
 stdout,stderr = p.communicate()
 retcode = p.returncode
 return stdout,stderr,retcode

def read_json(file_path):
 data = dict()

 with open(file_path) as file_input:
  data = json.load(file_input)

 return data 

def write_json(file_path,input_dict):
 with open(file_path, "w") as outfile:
  json.dump(input_dict, outfile)

if __name__ == "__main__":
 json_file = "/nfs/science/shared/util/jailing_utility/jailing_counter.json"
 log_file_name = "/nfs/science/shared/util/jailing_utility/jailing_logs.log"
 output_dict = dict()
 threshold_days = 3
 to_jail_users = ""
 msg_body = "Jailing the iPython Notebook directories of below users as they have defaulted for: "+str(threshold_days)+" days:\n\n"
 email_address = "ScienceEnvironmentsSupportSquad@domain.com"
 mail_subject = "Jailed directories for today!"
 log_file = getLoggerFile(log_file_name)
 log_file.setLevel(logging.DEBUG)
 jailing_script = "sh /nfs/science/shared/util/jailNotebooks.sh"

 log_file.info("Starting the execution of check2jail.py")

 if not os.path.isfile(json_file):
  log_file.info("Creating the JSON file: "+json_file)
  write_json(json_file,output_dict)

 input_dict = read_json(json_file)

 for line in fileinput.input():
  userID = line.rstrip()
  user_count = 0
  try:
   user_count = input_dict[userID]
  except:
   log_file.info("Entry missing for user: "+userID)

  user_count = user_count + 1

  if user_count >= threshold_days:
   log_file.info("Jailing threshold of "+str(threshold_days)+" days met for user: "+userID+". Proceeding to jail!")
   to_jail_users = to_jail_users + userID + "\n"
   jailing_command = jailing_script+" "+userID
   stdout,stderr,retcode = execute_cmd(jailing_command)
   if retcode != 0:
    log_file.error("Jailing command FAILED for user: "+userID)
    log_file.error(stderr)
   else:
    log_file.info(stdout)
 # else:
  output_dict[userID] = user_count

 write_json(json_file,output_dict)

 for username in input_dict:
  try:
   log_file.warn("Defaulter count for: "+username+" is "+str(output_dict[username]))
  except:
   log_file.info("Removing the non-defaulted user: "+username+" from the counter JSON.")
 
 if to_jail_users != "":
  log_file.info("Sending email for Jailing the users: "+to_jail_users)
  mail_cmd = "echo '"+msg_body+to_jail_users+"' | mail -r svc_sciops@domain.co.uk -s '"+mail_subject+"' "+email_address
  execute_cmd(mail_cmd)

 log_file.info("Ending the execution of check2jail.py")
