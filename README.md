# BSync 

BSync is a tool made in python for easily syncing the Beat Saber CustomLevels folder with friends.
Give the program the location of your CustomLevels folder and it will create a .txt file of all the present IDs.
Use your friends' .txt files to download their songs. 


* bsaber.com is the only supported repository for songs, any IDs that can't be found there won't be downloaded
* Program supports multiple ID text files


## How It Works

### Sharing your ID text file

1. Run bsync.exe and select option 1
2. Enter the filepath to your CustomLevels Folder
(ex: C:\Program Files\Steam\steamapps\common\Beat Saber\Beat Saber_Data\CustomLevels)
3. Enter your name to be used in the .txt filename
4. Share the text file that was generated in the bsync folder with your friends (ex: ids_{your name}_{timestamp}.txt)

**Do not change this filename** 

### Downloading songs from a shared text file

1. Move the .txt files of IDs into the folder with bsync.exe
2. Run bsync.exe and select option 2
3. Enter the filepath to your CustomLevels Folder
4. Wait for the downloads to finish, the zips will automatically unzip into the CustomLevels folder.
Zips are saved to downloaded_zips folder, this folder can be deleted after the program is finished

## Download

[Download v1.1.0](https://github.com/launchd/bsync/releases/download/v1.1.0/bsync-1.1.0.zip) - the latest runnable version

## Common Issues

Check log.txt for more information if something fails. 

1. Some songs have characters in different languages than your PC. In this case, the download will partially fail. You will notice .tmp files in the program directory. You can change the .tmp extension to .zip and still open the file. The filename will also contain the ID of the song as it appears on bsaber.com/songs/{song ID here}. 

