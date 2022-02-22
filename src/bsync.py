import os, time, requests, zipfile, re, json
from datetime import datetime
# TODO allow menu to loop

# Config
dirZipDownloads = 'downloaded_zips'
dirCustomlevels = ''
CONFIG_FILE = 'config.txt'
logFile = 'log.txt'
debug = False
userChoice = '0'
logFileContents = '\n--------------------------------------------'

# Methods #
#
# Read Config
def readConfigFile():
    global dirZipDownloads, dirCustomlevels, logFile, debug
    try:
        with open(CONFIG_FILE, "r") as read_file:
            data = json.load(read_file)
        dirCustomlevels = data["config"]["CustomLevels"]
        dirZipDownloads = data["config"]["dirZipDownloads"]
        logFile = data["config"]["logFile"]
        debug = bool(data["config"]["debug"])
    except:
        log('Error: Unable to open ' + CONFIG_FILE + ' (readConfigFile)')
#
# Write Config
def writeConfigFile():
    print('Writing config file to', logFile)
    log('Writing config file to ' + logFile)
    config = {
        "config": {
            "CustomLevels" : dirCustomlevels,
            "dirZipDownloads" : dirZipDownloads,
            "logFile" : logFile,
            "debug" : debug,
        }
    }
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file, indent=2)

#
# Adds messages to the log
def log(str):
    global logFileContents
    logFileContents += "\n" + str
        
#
# Writes all the logs to a file before program closes
def writeLogFile():
    dt = datetime.now()
    ts = str(datetime.timestamp(dt))
    global logFileContents
    logFileContents += '\n[' + ts + ']]\n--------------------------------------------'

    with open(logFile, 'a') as file:
            file.write(logFileContents)
#
# Get song IDs from zip downloads folder to prevent duplicate downloads
def getIDsFromZipFolder():
    songZips = os.listdir(dirZipDownloads)
    
    songsIds = []
    reSongID = re.compile('(^[a-zA-z0-9]+)')
    for song in songZips:            # Loop through files and folders
        regMatch = reSongID.match(song)
        songId = str(regMatch.group())
        songsIds.append(songId)

    return songsIds
#
# Check for .tmp files left over in the programs folder
def checkForFailedDownloads():
    files = os.listdir()
    print() # Adds a spacer line
    errorFound = False
    for f in files:
        if(os.path.isfile(f) and f[-4:] == '.tmp'):
            print("Error: Failed to download file:", f)
            log("Failed to download " + f)
            errorFound = True
        
    if(errorFound):
        print("Failed download, this usually happens to songs with different languages. The song zip exists as a .tmp file in the bsync program folder. The ID for the song is in the beginning of the filename. Get the song manually from bsaber or change .tmp extension to .zip to open the file.")
#
# Get song IDs from CustomLevels folder
def getIDsFromFolder(cldir):
    if(cldir[:-1] != '\\'):
        cldir += '\\'
    try:
        songFolders = os.listdir(cldir)
        songs = []
        idsOut = ''
        reSongID = re.compile('(^[a-zA-z0-9]+)')
        for song in songFolders:            # Loop through files and folders
            if(os.path.isdir(cldir + song)):# Choose only folders
                if(debug): print(song)   
                regMatch = reSongID.match(song)
                songId = str(regMatch.group())
                songName = song[regMatch.end():].strip()
                songs.append([songId, songName]) # Format songs into 2D array with ID/Name separate
        # Parse and Print Output for Sharing
        idsOut = ''
        for s in songs:
            if(debug): print(s[0])
            idsOut += s[0] + ','
        if(debug): print(idsOut)

        return idsOut
    except:
        print('Please enter a valid filepath to the CustomLevels folder')
        log('Invalid filepath to CustomLevels folder (getIDsFromFolder)')
#
# Save all given IDs to a CSV text file
def exportIDs(ids):
    if ids is None:
        print("No IDs found, did you enter a valid file path?")
        log("No IDs found, check CustomLevels file path (exportIDs)")
    else:
        dt = datetime.now()
        ts = str(datetime.timestamp(dt))

        userName = 'x'    
        if(not debug): userName = input('Enter your name:')
        filename = 'ids_' + userName + '_' + ts + '.txt'
        with open(filename, 'w') as file:
            file.write(ids[:-1])
            log('Ids written to file: ' + filename)
            print('Ids written to file: ' + filename)    
        
#
# Gets All IDs from the ids_*.txt files
def importIDs():
    files = os.listdir()
    idFiles = []
    for f in files:
        if(os.path.isfile(f) and f.find('ids_') != -1):
            if debug: print(f)
            idFiles.append(f)
            print("Imported IDs from:", f)
            log("Imported IDs from:")
    # Parse ID input
    ids = []
    for f in idFiles:        
        fOpen = open(f, 'r')
        tempIds = fOpen.read()
        tempIds = tempIds.rstrip().split(',')
        for id in tempIds:
            if id not in ids and id != '':
                ids.append(id)
    if len(ids) == 0:
        print("Error: No IDs could be imported, are you text files in the same folder as bsync.exe?")
        log("Error: No IDs could be imported (importIDs)")
    return ids 
#
# Download all songs
def downloadSongs(idsToDownload, localIds):
    # Example url https://api.beatsaver.com/download/key/210e3
    # Create folder for zip files if it doesn't exist
    songsDownloaded = 0
    duplicates = 0

    if(not os.path.isdir(dirZipDownloads)):
        os.mkdir(dirZipDownloads)
    
    for i in idsToDownload:
        if i in localIds:
            duplicates += 1
    print("Maximum songs to be downloaded:", len(idsToDownload) - duplicates, "Duplicates:", duplicates)
    log("IDs Found: " + str(len(idsToDownload)) + ", Duplicates: " + str(duplicates))
    
    for i in idsToDownload:        
        if i not in localIds:
            print('Downloading ID: ', i, '(',idsToDownload.index(i)+1, '/', len(idsToDownload), ')')
            #if (debug): print(url)
            zipFile = str(os.path.join(str(os.getcwd()), dirZipDownloads, i+'.zip'))
           
            #Get already downloaded songs to prevent duplicate songs
            zipIDs = getIDsFromZipFolder()            
            if(i not in zipIDs):
                try:
                    url = 'https://api.beatsaver.com/download/key/' + i
                    zipFileName = i + '.zip'
                    downloadRequest = requests.get(url)  
                    open(zipFileName, 'wb').write(downloadRequest.content)  
                    contentDispo = downloadRequest.headers.get('Content-Disposition') 
                    if(contentDispo is not None):
                        songNameStart = contentDispo.index('"')
                        songName = contentDispo[songNameStart+1:-1]
                        print(songName)
                        if(not os.path.isfile(os.path.join(dirZipDownloads, zipFile))):
                            os.rename(zipFileName, str(os.path.join(str(os.getcwd()), dirZipDownloads, songName)))                        
                            songsDownloaded += 1    
                        else:
                            log("Error: Zip file already exists " + songName + '.zip (downloadSongs)')
                            os.remove(zipFileName)
                    else:
                        print("Failed to download song, ID not found", i)
                        log("Error: Failed to download song, ID not found: " + i)
                        os.remove(zipFileName)
                except Exception as e:
                    print("Failed to download song:", i)
                    log("Failed to download song: " + i)
                    print(e)
                    log(e)                    
            else:
                print("Warning: Skipping download, duplicate zip file:", i)
        else:
            log('Warning: Already own song: ' + i + ' (downloadSongs)')
    checkForFailedDownloads()
    return songsDownloaded
#
# Get CustomLevels file path from user
def getCLFolder():
    global dirCustomlevels
    if(not dirCustomlevels):
        dirCustomlevels = input("Enter filepath for Custom Levels Folder:")        
        #cldir = "D:\Steam\steamapps\common\Beat Saber\Beat Saber_Data\CustomLevels\"
        #cldir = '/home/user/bsync/CustomLevels/'
        if(debug): print(dirCustomlevels)
        log('CustomLevels Folder: ' + dirCustomlevels) 
    return dirCustomlevels
#
# Unzip songs
def unzipSongs(cldir):
    log("Unzipping files now (unzipSongs)")
    zipFiles = []
    files = os.listdir(dirZipDownloads)    
    for f in files:
        if(f[-4:] == '.zip'):
            #if debug: print('zip: ' + f)
                       
            with zipfile.ZipFile(os.path.join(dirZipDownloads, f), 'r') as zip_ref:
                f = f.replace('.zip', '')
                songDir = os.path.join(cldir, f)
                if(not os.path.isdir(songDir)):              
                    os.mkdir(songDir)
                    print('Extracting ' + f)
                    zip_ref.extractall(songDir)
                else:
                    log("Error: Folder already exists (" + f + ") (unzipSongs)")
### MAIN ###

# Get the config file if it exists
readConfigFile()

# Start of Menu #
print()
print("\t\t-- BSync Menu --")
print("0. Set CustomLevels folder in config.txt")
print("1. Export your song IDs to a text file for sharing.")
print("2. Download songs from IDs in text files you've saved.")

if(not debug):
    userChoice = input("Enter the number of your menu choice:")


# Handle Menu Options
if(userChoice == '1'): # Export IDs to text file
    # Get CustomLevels file path
    cldir = getCLFolder()
    # Get Song IDs
    songIDs = getIDsFromFolder(cldir)    
    # Write to file
    exportIDs(songIDs)
    
elif(userChoice == '2'): # Download songs
    log('Retrieving IDs...')
    ids = importIDs()
    # If there are songs to get from .txt files
    if len(ids) > 0:
        cldir = getCLFolder()
        localIds = getIDsFromFolder(cldir).split(',')
        # Download zips in batches
        songsDownloaded = downloadSongs(ids, localIds)
        if(songsDownloaded > 0):
            # Unzip
            print("Downloaded Songs:", songsDownloaded)
            log("Downloaded " + str(songsDownloaded) + " songs (userChoice=2)")
            unzipSongs(cldir)
        else:
            print('------------------------')
            print("No new songs found for download, you have them all already.")
            log("No songs found for download (userChoice=2)")
elif(userChoice == '0'):
    dirCustomlevels = ''
    dirCustomlevels = getCLFolder()
    
writeLogFile()
writeConfigFile()
input("--- Press enter to close this window ---")
