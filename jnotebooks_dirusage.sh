#!/bin/bash 
#Purpose - To monitor notebook directory usage
#Note : du --thresold option not available in coreutils of centOS6 versions,please test the script before running  

monitor_path=/nfs/science/shared/ipythonNotebooks
threshold_usage=1G
mail_subject=$1
flag_file=/nfs/science/shared/util/jailing_utility/not_to_run_today

if [ -f $flag_file ];then
 echo "Skipping run of Jupyter Notebook defaulter report as the flag file: $flag_file is present. EXITING!"
 read -r -d '' MSG_BODY <<- EOM
        To: ScienceEnvironmentsSupportSquad@domain.com
	Subject: Jupyter Notebook Directory Usage - Skipped today!
	Content-Type: text/html; charset="us-ascii"
 	
	<html>
	<p>
       The process of Jupyter Notebook disk usage status report has been <span style="color:red;"><b>SKIPPED</b></span> today because of the presence of flag file: <b>$flag_file</b><br><br>
       To resume the process, <b>REMOVE</b> the flag file and retrigger the process manually. In the coming days the process will be skipped again, until the file is removed.</p>
	</html>
EOM
 echo "$MSG_BODY" | /usr/sbin/sendmail -r svc_sciops@domain.co.uk ScienceEnvironmentsSupportSquad@domain.com
else
 echo "Generating usage report on $(date)"
 result="$(du -shx --threshold=$threshold_usage $monitor_path/* | sort -rh)"
 echo "$result"

 #Generating users list
 users_list="$(printf "$result" | awk -F/ '{print $NF}')"

 #Converting user id's to emailid's
 #users_email_ids="$(printf "$users_list" | /nfs/science/shared/util/userid2email.py)"

 printf "$users_list" | /nfs/science/shared/util/userid2email.py > /tmp/emailids_jnotebooks.txt

 #Adding code for automating the jailing of directories
 printf "$users_list" | /nfs/science/shared/util/jailing_utility/check2jail.py

 #Mapping the email ids for service accounts from lookup.txt file
 users_email_ids=$(awk -F"[: ]" -v OFS=" " -v ORS="," 'NR==FNR { A[$1]=$2 ; next } ; { for(N=1; N<=NF; N++) if($N in A) $N = A[$N] } 1' /nfs/science/shared/util/lookup.txt /tmp/emailids_jnotebooks.txt)

 #Sending mail to users
 read -r -d '' MSG_BODY <<- EOM
        To: $users_email_ids
	Cc: ScienceEnvironmentsSupportSquad@domain.com
	Subject: $mail_subject
	Content-Type: text/html; charset="us-ascii"
	
	<html>
	<p>You are receiving this alert because your Jupyter Notebooks directory is taking 
	more than 1Gb space on Science Servers.<br><br> 

	Notebooks directory is not the place to store data and big files. It will impact
	all users if the disk fills up. Please move data under market directories (/nfs/science/{market}) and cleanup your Notebook directory so that it is less than 1Gb.<br><br>

	To find the size of files and directories, refer page - https://dhgitlab.domain.co.uk/science/environments/-/wikis/Find-disk-usage-of-files-and-directories-using-du-commands<br><br>
	
	Note - All data under your notebook directory will be <span style="color:red;"><b>moved AFTER 2 consecutive notifications</b></span>, if no action is taken.</p>
	<br>
	<pre><b>$result</b></pre>
	</html>
EOM

 if [ $(echo "$users_email_ids" | wc -l) > 0 ];then
 #echo "$MSG_BODY" $'\n\n'"$result" | mail -r svc_sciops@domain.co.uk -c ScienceEnvironmentsSupportSquad@domain.com -s "$mail_subject" $users_email_ids
  echo "$MSG_BODY" | /usr/sbin/sendmail -r svc_sciops@domain.co.uk $users_email_ids ScienceEnvironmentsSupportSquad@domain.com
 fi
fi
