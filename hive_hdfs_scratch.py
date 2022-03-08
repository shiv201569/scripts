#!/bin/python3
# -*- coding: utf-8 -*-

#Run this job as hive user or super user e.g BDR_SUPERUSER
# Example command to run the job
#gi-hadoop-scripts/kinit_script.sh hive && PYSPARK_PYTHON=/dhcommon/dhhadoop/python3/bin/python3 spark-submit --master yarn --deploy-mode client --queue root.backup --conf spark.yarn.appMasterEnv.PYSPARK_DRIVER_PYTHON=/dhcommon/dhhadoop/python3/bin/python3 drop_scratch_tables_v1.py

import sys, os, datetime, json, logging, time, re, getopt, pipes, smtplib, json, requests, platform, glob
import subprocess as sp
import base64
import mysql.connector
import configparser
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from requests.auth import HTTPBasicAuth
from datetime import date
from datetime import datetime
from itertools import islice

TODAY = date.today()

hiveTables = 'hiveTables-{0}.txt'.format(TODAY)
hdfsFiles = 'hdfsFiles-{0}.txt'.format(TODAY)
hdfsEmptyDirectories = 'hdfsEmptyDirectories-{0}.txt'.format(TODAY)

################################################################################
# Argument Parser
################################################################################

help_epilog = ("Here is an example command:\n"
" gi-hadoop-scripts/kinit_script.sh hive && PYSPARK_PYTHON=/dhcommon/dhhadoop/python3/bin/python3 spark2-submit --master yarn --deploy-mode client --queue root.backup --conf spark.yarn.appMasterEnv.PYSPARK_DRIVER_PYTHON=/dhcommon/dhhadoop/python3/bin/python3 drop_scratch_tables_v1.py "
" --market tesco_uk"
" --path /opt/scratch"
)

parser = argparse.ArgumentParser(description='Remove older files and tables from scratch area',epilog=help_epilog)
parser.add_argument('--market', required=True, help='The name of the market for which the script is run')
parser.add_argument('--path', required=True, help='Path from where the script is run')

################################################################################
# Parse the arguments and build the query
################################################################################

clientName = ''
path = ''
args = parser.parse_args()
clientName = args.market
path = args.path

#Scratch Interval
#no_of_days = 30
#Store password in external file(with strict permission) in base64 encoded format. Command to encode password - "echo 'password123' | base64"
hivepasswordFile = '{0}/hive_metastore_db_password.txt'.format(path)
hive_db_password = ''
SMTP_SERVER = 'mailserver'
hdfs_scratch_dir = '/{0}/data/unrestricted/analysis_scratch'.format(clientName)

################################################################################
# Functions
################################################################################

def dropScratchHiveTables(hive_db_password):
    #Importing required pytho packages
    from pyspark import SparkConf
    from pyspark.context import SparkContext
    from pyspark.sql import SparkSession, SQLContext
    spark = SparkSession.builder.enableHiveSupport().getOrCreate()
    sc = spark.sparkContext
    sqlContext = spark._wrapped
    from socket import gethostname

    #Connecting to Hive Metastore MySql Db
    mydb = mysql.connector.connect(
    host="mysql-server",
    user="hive",
    passwd=hive_db_password,
    database="hive"
    )

    mycursor = mydb.cursor()

    #USE IT CAUTIOUSLY AND TEST BEFORE MAKING ANY CHANGES. INCORRECT DB NAME PATTERN CAN DROP WRONG TABLES
    #ADD database pattern like "'analysis_scratch'" and create dbs with same suffix e.g tesco_uk_analysis_scratch
    database = clientName + "_analysis_scratch"
    db_name_pattern = "'{0}'".format(database)

    #query will output tables not modified for more than 30 days using property 'transient_lastDdlTime'
    myquery="select DBS.DB_ID, DBS.NAME, TBLS.TBL_ID, TBLS.TBL_NAME, TABLE_PARAMS.PARAM_KEY, FROM_UNIXTIME(TABLE_PARAMS.PARAM_VALUE) \
    FROM TBLS \
    INNER JOIN DBS \
    ON DBS.DB_ID = TBLS.DB_ID \
    INNER JOIN TABLE_PARAMS \
    ON TBLS.TBL_ID = TABLE_PARAMS.TBL_ID \
    WHERE DBS.NAME like {pattern} and TABLE_PARAMS.PARAM_KEY = 'transient_lastDdlTime' \
    AND FROM_UNIXTIME(TABLE_PARAMS.PARAM_VALUE) < now() - INTERVAL {x} DAY".format(pattern = db_name_pattern, x = 30)

    mycursor.execute(myquery)

    #Below output will result in list of result
    myresult = mycursor.fetchall()

    sys.stdout = open('{0}/{1}'.format(path, hiveTables), 'w')
    print("""Welcome to
          ____              __
         / __/__  ___ _____/ /__
        _\ \/ _ \/ _ `/ __/  '_/
       /__ / .__/\_,_/_/ /_/\_\   version %s
          /_/
    """ % sc.version)
    print("Using Python version %s (%s, %s)" % (platform.python_version(),platform.python_build()[0],platform.python_build()[1]))
    print("SparkSession available as 'spark', SparkContext available as 'sc', %s available as 'sqlContext'." % sqlContext.__class__.__name__)
    print("Running from server %s" % gethostname())
    print("Spark Jobs submitted on queue: %s" % sc._conf.get('spark.yarn.queue'))
    print("This is for market: {0}".format(clientName))
    print("This function is for dropping the hive tables from Scratch Database %s which have not been modified in last 30 days \n" % db_name_pattern)

    #Dropping tables sequentially using the list returned by Mysql query
    #Replace sql query with drop query to drop tables

    if not myresult:
      print("No old tables to drop from scratch database %s " % db_name_pattern)
    else:
      for x in myresult:
        sql_query = """show tables from {db_name} like '{table_name}'""".format(db_name =x[1], table_name = x[3])
        print(sql_query)
        spark.sql(sql_query).show()
        sql_query = """DROP TABLE IF EXISTS {db_name}.{table_name}""".format(db_name = x[1], table_name = x[3])
        spark.sql(sql_query)

    spark.stop()
    sc.stop()
    print("End of the job. Bye!")

    sys.stdout.close()

def dropScratchHdfsFiles(hdfs_scratch_dir):
    # Generating hdfs super user keytab
    bashCommand = "/root/gi-hadoop-scripts/kinit_script.sh hdfs"
    os.system(bashCommand)

    sys.stdout = open('{0}/{1}'.format(path, hdfsFiles), 'w')
    print("List of files not modified in last 30 days to be removed from HDFS scratch area %s \n" % hdfs_scratch_dir)
    p2 = sp.Popen("hadoop jar /opt/cloudera/parcels/CDH/jars/search-mr-1.0.0-cdh5.15.1-job.jar org.apache.solr.hadoop.HdfsFindTool -find "+hdfs_scratch_dir+" -mtime +30 -type f", stdout=sp.PIPE, stderr=sp.PIPE, shell=True).communicate()[0]
    output = p2.decode('utf-8')[:-1]

    if not output:
      print("No old files to list and drop from scratch area %s in HDFS" % hdfs_scratch_dir)
    else:
      print (output)
    sys.stdout.close()

    sys.stdout = open('{0}/DeleteFiles-{1}.txt'.format(path,clientName), 'w')
    p3 = sp.Popen("hadoop jar /opt/cloudera/parcels/CDH/jars/search-mr-1.0.0-cdh5.15.1-job.jar org.apache.solr.hadoop.HdfsFindTool -find "+hdfs_scratch_dir+" -mtime +30 -type f", stdout=sp.PIPE, stderr=sp.PIPE, shell=True).communicate()[0]
    output1 = p3.decode('utf-8')[:-1]
    print (output1)
    sys.stdout.close()

    batch_size = 500
    start = 0
    line_count = 0

    #Taking the count of number of files to be removed
    for line in open('{0}/DeleteFiles-{1}.txt'.format(path,clientName), 'r'):
      line_count += 1

    while start < line_count:
      with open('{0}/DeleteFiles-{1}.txt'.format(path,clientName), 'r') as flist:
        out_args = ""
        for file_name in islice(flist, start, start+batch_size):
          out_args = out_args + "'" + file_name.rstrip('\n') + "' "
        sp.Popen("hdfs dfs -rm "+out_args, stdout=None, stderr=None, shell=True).communicate()
        start = start+batch_size

    os.remove('{0}/DeleteFiles-{1}.txt'.format(path,clientName))

# Function for removing the empty HDFS scratch directories
def dropScratchHdfsEmptyDirectories(hdfs_scratch_dir):
    # Generating hdfs super user keytab
    bashCommand = "/root/gi-hadoop-scripts/kinit_script.sh hdfs"
    os.system(bashCommand)

    sys.stdout = open('{0}/{1}'.format(path, hdfsEmptyDirectories), 'w')
    print("List of empty directories not modified in last 30 days to be removed from HDFS scratch area %s \n" % hdfs_scratch_dir)
    p2 = sp.Popen("hadoop jar /opt/cloudera/parcels/CDH/jars/search-mr-1.0.0-cdh5.15.1-job.jar org.apache.solr.hadoop.HdfsFindTool -find "+hdfs_scratch_dir+" -mtime +30 -type d -empty", stdout=sp.PIPE, stderr=sp.PIPE, shell=True).communicate()[0]
    output = p2.decode('utf-8')[:-1]

    if not output:
      print("No old empty directories to list and drop from scratch area %s in HDFS" % hdfs_scratch_dir)
    else:
      print (output)
    sys.stdout.close()

    sys.stdout = open('{0}/DeleteDirectories-{1}.txt'.format(path,clientName), 'w')
    p3 = sp.Popen("hadoop jar /opt/cloudera/parcels/CDH/jars/search-mr-1.0.0-cdh5.15.1-job.jar org.apache.solr.hadoop.HdfsFindTool -find "+hdfs_scratch_dir+" -mtime +30 -type d -empty", stdout=sp.PIPE, stderr=sp.PIPE, shell=True).communicate()[0]
    output1 = p3.decode('utf-8')[:-1]
    print (output1)
    sys.stdout.close()

    batch_size = 500
    start = 0
    line_count = 0

    #Taking the count of number of files to be removed
    for line in open('{0}/DeleteDirectories-{1}.txt'.format(path,clientName), 'r'):
      line_count += 1

    while start < line_count:
      with open('{0}/DeleteDirectories-{1}.txt'.format(path,clientName), 'r') as flist:
        out_args = ""
        for file_name in islice(flist, start, start+batch_size):
          out_args = out_args + "'" + file_name.rstrip('\n') + "' "
        sp.Popen("hdfs dfs -rm -r "+out_args, stdout=None, stderr=None, shell=True).communicate()
        start = start+batch_size

    os.remove('{0}/DeleteDirectories-{1}.txt'.format(path,clientName))

# Function for transferring the files to global science server
def scp():
     p = sp.Popen(["scp", "{0}/{1}".format(path, hiveTables), "{0}/{1}".format(path, hdfsFiles), "{0}/{1}".format(path, hdfsEmptyDirectories) , "user@FQDN:/nfs/science/shared/www/html/science-env/scratch_area/{0}".format(clientName)])
     sts = os.waitpid(p.pid, 0)
     sys.stdout = open('{0}/transferFiles-{1}.txt'.format(path,clientName), 'w')
     print ("Transferred the files successfully to the server gb-slo-svv-0879 at the path /nfs/science/shared/www/html/science-env/scratch_area/{0}".format(clientName))

     files = glob.glob('{0}/*-{1}.*'.format(path, TODAY))
     print ("Removing the following files from the path: %s" % path)
     for f in files:
         try:
             print (f)
             os.remove(f)
         except OSError as e:
             print("Error: %s : %s" % (f, e.strerror))

     sys.stdout.close()

################################################################################
# Main program
################################################################################

def main():
        #This method will decode the password stored in external file
        # Retrieve the hive database password from a file
        in_file = open(hivepasswordFile, "r")
        encodedValue = in_file.readline()
        in_file.close()
        hive_db_password = base64.b64decode(encodedValue).decode('utf-8').strip("\n")

        #Calling the functions
        dropScratchHiveTables(hive_db_password)
        dropScratchHdfsFiles(hdfs_scratch_dir)
        dropScratchHdfsEmptyDirectories(hdfs_scratch_dir)
        scp()

################################################################################
# Program Execution
################################################################################

if __name__ == "__main__":
        main()
