#!/bin/bash

###########################################
# Cleanup for science_scratch NFS mount 
# Created by Punit Goyal
# Modified by Shivam Agrawal
###########################################

# Usage:
# bash cleanup_scratch_disk_v0.5.sh <Market_Name>

FS=/nfs/science_scratch/$1
cd $FS
cat /dev/null > /tmp/list_of_files_to_be_deleted.txt

# Funtion for just sending the communication and not deleting the files
send_comms()
{
  #Finding the list of files which are not modified in last 13 days
  find $FS -type f -mtime +13  -exec ls -lh {} >> /tmp/list_of_files_to_be_deleted.txt \;

  #Counting number of files
  Number_of_files=$(cat /tmp/list_of_files_to_be_deleted.txt | awk '{ print $3}' | grep -v root | wc -l )
  echo -e "There are total $Number_of_files file in /nfs/science_scratch/$1, which were not used/modified in last 13 days. And these will be deleted tomorrow.\n\nNOTE: There is no backup being taken for these file, so if you need these files permanently, please edit them or move to /nfs/science/$1 \n \n"  > /tmp/mail_body

  #Finding list of users who own the older files
  result=$(cat /tmp/list_of_files_to_be_deleted.txt | awk '{ print $3}' | uniq | grep -v root)
  if [ -z "$result" ]; then
       exit 1
  fi

  #Creating a user list for sending emails
  users_list="$(printf "$result" | awk -F/ '{print $NF"@domain.com"}')"

  #Sending the list of files to the users
  cat /tmp/mail_body /tmp/list_of_files_to_be_deleted.txt | mail -r svc_sciops@domain.co.uk -c ScienceEnvironmentsSupportSquad@domain.com -s "Files to be removed from /nfs/science_scratch for market - $1" $users_list
}

# Function for removing the files only
remove_data()
{
  #Finding the list of files which are not modified in last 13 days
  find $FS -type f -mtime +14 -exec ls -lh {} >> /tmp/list_of_files_to_be_deleted.txt \;

  echo -e "Following files will be deleted today. \n \n"  > /tmp/mail_body

  #Sending the list of files to be deleted
  cat /tmp/mail_body /tmp/list_of_files_to_be_deleted.txt | mail -r svc_sciops@domain.co.uk -s "Files to be removed from /nfs/science_scratch for market - $1" ScienceEnvironmentsSupportSquad@dunnhumby.com

  #Removing the list of files
  find $FS -type f -mtime +14 -exec rm -f {} \; 
}

# Funtion for listing and removing the data
listing_remove_data()
{
  #Removing the files
  find $FS -type f -mtime +14 -exec rm -f {} \;

  #Finding the list of files which are not modified in last 13 days
  find $FS -type f -mtime +13  -exec ls -lh {} >> /tmp/list_of_files_to_be_deleted.txt \;

  #Counting number of files
  Number_of_files=$(cat /tmp/list_of_files_to_be_deleted.txt | awk '{ print $3}' | grep -v root | wc -l )
  echo -e "There are total $Number_of_files file in /nfs/science_scratch/$1, which were not used/modified in last 13 days. And these will be deleted tomorrow.\n\nNOTE: There is no backup being taken for these file, so if you need these files permanently, please edit them or move to /nfs/science/$1 \n \n"  > /tmp/mail_body

  #Finding list of users who own the older files
  result=$(cat /tmp/list_of_files_to_be_deleted.txt | awk '{ print $3}' | uniq | grep -v root)
  if [ -z "$result" ]; then
       exit 1
  fi

  #Creating a user list for sending emails
  users_list="$(printf "$result" | awk -F/ '{print $NF"@domain.com"}')"

  #Sending the list of files to the users
  cat /tmp/mail_body /tmp/list_of_files_to_be_deleted.txt | mail -r svc_sciops@domain.co.uk -c ScienceEnvironmentsSupportSquad@domain.com -s "Files to be removed from /nfs/science_scratch for market - $1" $users_list
}  

#Deleting the files when the week day is Monday
we=$(LC_TIME=C date +%A)
if [ "$we" = "Monday" ]
then
send_comms "$1"
elif [ "$we" = "Saturday" ]
then
remove_data "$1"
else
listing_remove_data "$1"
fi
