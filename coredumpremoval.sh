#!/bin/bash
# This script is used to remove the coredump files whose size > 1G

target_dir="/nfs/science"
log_file="/var/log/coredump_cleaner.log"
base_file_names="/tmp/base_file_names.txt"
to_be_removed="/tmp/tbr_file_names.txt"
threshold_size=1
oldIFS=$IFS
IFS=$'\n'

echo "Start Time: "`date` >> $log_file

find $target_dir -type f -iname 'core\.[0-9]*' > $base_file_names

for file_name in `cat $base_file_names`; do
  size=$(echo \'$file_name\' | xargs stat -c %s);
  file_type=$(echo \'$file_name\' | xargs file -bi | cut -d ';' -f1 );
  if [ "$size" -gt $threshold_size -a "$file_type" == "application/x-coredump" ]; then
   echo \'$file_name\' >> $to_be_removed
  fi;
done

if [ `cat $to_be_removed | wc -l` -gt 0 ]; then
 echo "Removing below binary coredump file(s) > "$threshold_size" byte(s) in size: " >> $log_file
 for file_name in `cat $to_be_removed`; do
  echo $file_name | xargs stat -c %s" "%n >> $log_file
  echo $file_name | xargs rm -f
 done
else
 echo "Nothing to remove today!" >> $log_file
fi

rm -f $base_file_names $to_be_removed

echo "Stop Time: "`date` >> $log_file
echo "" >> $log_file

IFS=$oldIFS
