#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ================================================================================================================================================ #
# IMPORTS
# ================================================================================================================================================ #

import boto3

# ================================================================================================================================================ #
# CONSTANTS
# ================================================================================================================================================ #

# S3 properties
maxLevel = 3
s3bucket = "qa-reports-mediktiv"

# HTML file properties
baseHtml = "baseIndex.html"

# ================================================================================================================================================ #
# MAIN FUNCTION
# ================================================================================================================================================ #

def updateS3(event, context):
    # Get all the folders in the bucket
    folders = { 0: [""] }
    client = boto3.client('s3')
    
    # Get the root response
    response = client.list_objects_v2(Bucket = s3bucket, Prefix = "", Delimiter = "/")

    # While other folders exists, continue exploring subfolders
    folderLevel = 1
    while 'CommonPrefixes' in response and folderLevel < maxLevel:
        subFolders = []
        for prefix in response['CommonPrefixes']: subFolders.append(prefix['Prefix'])
        folders[folderLevel] = subFolders

        response = {}
        for folder in subFolders:
            newPrefixes = client.list_objects_v2(Bucket = s3bucket, Prefix = folder, Delimiter = "/")
            if 'CommonPrefixes' in newPrefixes: newPrefixes = newPrefixes['CommonPrefixes']
            else: continue
            if 'CommonPrefixes' not in response: response['CommonPrefixes'] = newPrefixes
            else: response['CommonPrefixes'] = response['CommonPrefixes'] + newPrefixes

        folderLevel += 1

    # Update the 'index.html' of each folder
    baseHtmlStr = readFile(baseHtml)
    for level in range(0, len(folders) - 1):
        for folder in folders[level]:
            head = "    <h1>Mediktiv QA Reports</h1><br/><h2>Projects</h2>" if level == 0 else "    <h1>{}</h1>".format(folder)
            links = ""
            for subFolder in folders[level + 1]:
                if folder in subFolder: links = links + "\n    <a href={} target=\"_blank\">{}</a><br/>".format(subFolder.replace(folder, ""), subFolder.replace(folder, ""))

            finalHtml = baseHtmlStr.split("[spl]")[0] + head + links + baseHtmlStr.split("[spl]")[1]
            #writeToFile('./index.html', finalHtml)

            # Now just send the file and replace it in S3
            client.put_object(ACL = "public-read", Body = finalHtml, Bucket = s3bucket, Key = folder + "index.html", ContentType = "text/html")
            

# ================================================================================================================================================ #
# FUNCTIONS
# ================================================================================================================================================ #

def readFile(filePath):
    with open(filePath, 'r') as myfile:
        return(myfile.read())

def writeToFile(filePath, text):
    f = open(filePath, "w")
    f.write(text)
    f.close()

# ================================================================================================================================================ #
# RUN TEST FUNCTION
# ================================================================================================================================================ #

if __name__ == '__main__':
    updateS3("", "")

# ================================================================================================================================================ #
# END OF FILE
# ================================================================================================================================================ #