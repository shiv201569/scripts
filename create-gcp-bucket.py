#!/usr/bin/python

import os
from google.cloud import storage

with open('client_list.txt') as dataproject:

    for clientdataName in dataproject:
        clientdataName = clientdataName.strip()
        csn1 = clientdataName.find('-') + 1
        # find() method will search the given
        # marker and sotres its index
        csn2 = clientdataName.find('-data', csn1)
        # using slicing substring will be
        # fetched in between markers.
        clientshortName = clientdataName[ csn1 : csn2 ]
        print ("Client short name is: " + clientshortName)

        # Extracting the client name
        clientName = clientdataName.replace('-data','')
        print ("Client name is: " + clientName)

        # Extract the zone details
        p2 = sp.Popen("gcloud compute instances list --project " + clientName + " | awk 'NR==2{print $2}'", stdout=sp.PIPE, stderr=sp.PIPE, shell=True).communicate()[0]
        zone = p2.decode('utf-8')[:-1]
        zone = zone[:-2]
        print ("Zone is: " + zone)

        # Extract location of analystplatform analyst-tmp buket
        client = storage.Client()
        bucket = client.get_bucket(clientshortName + "-analystplatform-analyst-tmp")
        location = bucket.location
        print ("Bucket location is: " + location)

        # Finally run various shell commands. This command is to create a GCP bucket.
        # This command can be used if multi_regional bucket needs to be created.
        cmd1 = "gsutil mb -b on -l " + location + " -p " + clientdataName + " -c multi_regional gs://" + clientshortName + "-analystplatform-soft-erasure"
        createBucket = os.system(cmd1)
        print("cmd1 ran with exit code %d" % createBucket)

        # This command can be used if regional bucket needs to be created.
        cmd1 = "gsutil mb -b on -l " + zone + " -p " + clientdataName + " -c regional gs://" + clientshortName + "-analystplatform-shelving-short"
        createBucket1 = os.system(cmd1)
        print("cmd1 ran with exit code %d" % createBucket1)

        # Shell command to set a lifecycle policy on the bucket of 7 days
        cmd2 = "gsutil lifecycle set lifecycle.json gs://" + clientshortName + "-analystplatform-soft-erasure"
        lifecycleRule = os.system(cmd2)
        print("cmd2 ran with exit code %d" % lifecycleRule)

        # Shell command for giving permissions to various service accounts on the GCP bucket created above
        cmd3 = "gsutil iam ch serviceAccount:" + clientshortName + "-an@" + clientName + ".iam.gserviceaccount.com:projects/" + clientdataName + "/roles/dsp_dataproject_bucket_read_write gs://" + clientshortName + "-analystplatform-soft-erasure"
        bucketPermission = os.system(cmd3)
        print("cmd3 ran with exit code %d" % bucketPermission)

        cmd4 = "gsutil iam ch serviceAccount:" + clientshortName + "-an-dp@" + clientName + ".iam.gserviceaccount.com:projects/" + clientdataName + "/roles/dsp_dataproject_bucket_read_write gs://" + clientshortName + "-analystplatform-soft-erasure"
        bucketPermission1 = os.system(cmd4)
        print("cmd4 ran with exit code %d" % bucketPermission1)

        cmd5 = "gsutil iam ch serviceAccount:" + clientshortName + "-an-admn@" + clientName + ".iam.gserviceaccount.com:projects/" + clientdataName + "/roles/dsp_dataproject_bucket_read_write gs://" + clientshortName + "-analystplatform-soft-erasure"
        bucketPermission2 = os.system(cmd5)
        print("cmd5 ran with exit code %d" % bucketPermission2)

        cmd6 = "gsutil iam ch serviceAccount:" + clientshortName + "-an-admn-dp@" + clientName + ".iam.gserviceaccount.com:projects/" + clientdataName + "/roles/dsp_dataproject_bucket_read_write gs://" + clientshortName + "-analystplatform-soft-erasure"
        bucketPermission3 = os.system(cmd6)
        print("cmd6 ran with exit code %d" % bucketPermission3)

        cmd7 = "gsutil iam ch serviceAccount:" + clientshortName + "-an-sen@" + clientName + ".iam.gserviceaccount.com:projects/" + clientdataName + "/roles/dsp_dataproject_bucket_read_write gs://" + clientshortName + "-analystplatform-soft-erasure"
        bucketPermission4 = os.system(cmd7)
        print("cmd7 ran with exit code %d" % bucketPermission4)

        cmd8 = "gsutil iam ch serviceAccount:" + clientshortName + "-an-sen-dp@" + clientName + ".iam.gserviceaccount.com:projects/" + clientdataName + "/roles/dsp_dataproject_bucket_read_write gs://" + clientshortName + "-analystplatform-soft-erasure"
        bucketPermission5 = os.system(cmd8)
        print("cmd8 ran with exit code %d" % bucketPermission5)

        cmd9 = "gsutil iam ch serviceAccount:" + clientshortName + "-an-af-sch@" + clientName + ".iam.gserviceaccount.com:projects/" + clientdataName + "/roles/dsp_dataproject_bucket_read_write gs://" + clientshortName + "-analystplatform-soft-erasure"
        bucketPermission6 = os.system(cmd9)
        print("cmd9 ran with exit code %d" % bucketPermission6)
