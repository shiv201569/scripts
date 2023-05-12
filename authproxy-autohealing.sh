#!/bin/bash

for project in $(cat projects.txt); do
        for img in $(gcloud compute instance-groups list --project $project); do
        if [[ ${img} == *"webuserproxy"* ]]; then
        echo "${img}"
        health_check=$(gcloud compute health-checks list --project ${project} | awk '{print $1}' | grep webuserproxy)
        zone=$(gcloud compute instance-groups list --format "get(zone)" --project ${project} --filter="name=${img}" | awk -F/ '{print $NF}')
        echo "${health_check}"
        echo "${zone}"
        echo "Enabling auto healing on ${img}"
        gcloud compute instance-groups managed update ${img} --health-check ${health_check} --zone ${zone} --initial-delay 300
        sleep 60
        fi
        done
done
