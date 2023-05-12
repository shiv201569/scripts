#!/dhcommon/dhhadoop/python3/bin/python3
# importing libraries
import os
import subprocess
import requests

threshold = 90



# a function to df on path
def df():

    # command is df
    cmd = 'df'
    path = ['/nfs/science/tesco_uk','/nfs/science/ti_thailand']
    res = []
    #global res

    # calculate df in human readable format
    # this is specified by '-h' in the
    # args list
    for dir in path:
        temp = subprocess.Popen([cmd, '-Ph', dir], stdout = subprocess.PIPE).stdout.read()

    # get the output of df
        #output = str(temp.communicate())
        output = str(temp)
        output = output.replace("b'","").replace("'","").split('\n')
        output = output[0].split('\\n')

    # variable to store the result
        used = []

        for row in output:
            used.append(row.split())

    # check if usage is above threshold

        if int((used[1][4][:-1])) >= threshold:
            res.append(dir)
            for line in output:
                res.append(line)

    #returning the final result

    res = '\n'.join(map(str, res))

    return res

def send_mail(df_output):
    proxyDict = { 'http'  : 'http://165.225.80.41:80', 'https' : 'http://165.225.80.41:80' }  # this is the UK proxy server

    #Replacing underscore and other special character in output with \ -
    # https://stackoverflow.com/questions/35827838/how-to-show-underscores-symbol-in-markdown
    formatted_df_output=df_output.replace('\n','<br/>').replace('_','\\_')

    # The URL below is created when you create the WebHook for the Channel in Teams
    MSTwebHookURL = "https://outlook.office.com/webhook/8b119804-697f-4beb-973a-0c1ba173e137@457a65b9-e5e8-45e1-83fb-85aa42633e5b/IncomingWebhook/1b29f82a69f64c3799108b4b4ab42393/908468a6-f18e-4e44-8c6f-b3d7e990429a"     # replace the URL with your own hook

    #MSTwebHookURL = "https://outlook.office.com/webhook/ac231853-8719-4649-84ba-1479160c8949@457a65b9-e5e8-45e1-83fb-85aa42633e5b/IncomingWebhook/9ef03014372a48818f95150e84160fce/908468a6-f18e-4e44-8c6f-b3d7e990429a"
    # You can use markdown syntax in the message
    formatted_df_output=df_output.replace('\n','<br/>').replace('_','\\_')

    textToPost = """# **ACTION REQUIRED : Disk usage close to 100% on science servers on premises**\n
Utilization has exceeded 90% in below market(s) directory on UK science servers. \
Users/teams storing data there are required to do cleanup asap. \
""" + formatted_df_output

    payload={"text": textToPost}

    requests.post(MSTwebHookURL, json=payload, proxies=proxyDict)

if __name__ == '__main__':

    # call function to calculate usage
    df_output=df()
    if len(df_output) != 0:
        send_mail(df_output)
