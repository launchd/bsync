import os, time, wget, zipfile, re
from datetime import datetime
# TODO 

# Config
zipDirectory = 'downloaded_zips'
debug = False
userChoice = '2'

# Methods #
# Log progress
def log(str, isError):
    if(isError and debug):
        print(str)
#
#Get song IDs from zip downloads folder to prevent duplicate downloads
def getIDsFromZipFolder():
    songZips = os.listdir(zipDirectory)
    
    songsIds = []
    reSongID = re.compile('(^[a-zA-z0-9]+)')
    for song in songZips:            # Loop through files and folders
        regMatch = reSongID.match(song)
        songId = str(regMatch.group())
        songsIds.append(songId)

    return songsIds
#
# Get song IDs from CustomLevels folder
def getIDsFromFolder(cldir):
    if(cldir[:-1] != '\\'):
        cldir += '\\'
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
#
# Save all given IDs to a CSV text file
def exportIDs(ids):
    dt = datetime.now()
    ts = str(datetime.timestamp(dt))

    userName = 'x'    
    if(not debug): userName = input('Enter your name:')
    filename = 'ids_' + userName + '_' + ts + '.txt'
    with open(filename, 'w') as file:
        file.write(ids[:-1])
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
    return ids 
#
# Download all songs
def downloadSongs(idsToDownload, localIds):
    # Example url https://api.beatsaver.com/download/key/210e3
    # Create folder for zip files if it doesn't exist
    songsDownloaded = 0
    if(not os.path.isdir(zipDirectory)):
        os.mkdir(zipDirectory)

    for i in idsToDownload:
        if i not in localIds:
            url = 'https://api.beatsaver.com/download/key/' + i
            #if (debug): print(url)
            zipFile = str(os.path.join(str(os.getcwd()), zipDirectory, i+'.zip'))
           
            #Get already downloaded songs to prevent duplicate songs
            zipIDs = getIDsFromZipFolder()            
            if(i not in zipIDs):
                try:
                    print('Downloading song: ' + i)
                    zipFile = wget.download(url)
                    
                    # Move song into zip folder if it doesn't already exist
                    if(not os.path.isfile(os.path.join(zipDirectory, zipFile))):
                        os.rename(zipFile, os.path.join(zipDirectory, zipFile))       
                        songsDownloaded += 1         
                    else:
                        log("Error: Zip file already exists " + i + '.zip', True)
                        os.remove(zipFile)
                    time.sleep(1)
                except:
                   log("Error: Unable to download song: " + url, True)
            else:
                print("Warning: Skipping download, duplicate:", i)
        else:
            log('Warning: Already own song: ' + i, True)
    return songsDownloaded
#
# Get CustomLevels file path from user
def getCLFolder():
    cldir = input("Enter filepath for Custom Levels Folder:")
    #cldir = "D:\Steam\steamapps\common\Beat Saber\Beat Saber_Data\CustomLevels\\"
    #cldir = '/home/chris/bsync/CustomLevels/'
    if(debug): print(cldir)
    return cldir
#
# Unzip songs
def unzipSongs(cldir):
    log("Unzipping files now...", False)
    zipFiles = []
    files = os.listdir(zipDirectory)    
    for f in files:
        if(f[-4:] == '.zip'):
            #if debug: print('zip: ' + f)
                       
            with zipfile.ZipFile(os.path.join(zipDirectory, f), 'r') as zip_ref:
                f = f.replace('.zip', '')
                songDir = os.path.join(cldir, f)
                if(not os.path.isdir(songDir)):              
                    os.mkdir(songDir)
                    zip_ref.extractall(songDir)
                else:
                    log("Error: Folder already exists (" + f + ")", True)

# Start of Menu
print()
print("\t\t-- BSync Menu --")
print("1. Export your song IDs to a text file for sharing.")
print("2. Download songs from IDs in text files you've saved.")
print('\tPress Ctrl+C to quit at any time')

if(not debug):
    userChoice = input("Choose 1 or 2 and press enter:")

# Handle Menu Options
if(userChoice == '1'):
    # Get CustomLevels file path
    cldir = getCLFolder()
    # Get Song IDs
    songIDs = getIDsFromFolder(cldir)    
    # Write to file
    exportIDs(songIDs)
    
elif(userChoice == '2'):
    log('Retrieving IDs...', False)
    ids = importIDs()
    if len(ids) > 0:
        cldir = getCLFolder()
        localIds = getIDsFromFolder(cldir).split(',')
        # Download zips in batches
        songsDownloaded = downloadSongs(ids, localIds)
        if(songsDownloaded > 0):
            # Unzip
            unzipSongs(cldir)
        else:
            print('------------------------')
            print("No new songs found for download, you have them all already.")

print("This window will automatically close in 30 seconds..")
time.sleep(30)
