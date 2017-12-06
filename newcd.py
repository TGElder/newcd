import configparser
from os import listdir, remove, devnull, makedirs, linesep
from os.path import join, splitext, exists
from shutil import copyfile
import subprocess
import argparse

config = configparser.ConfigParser()
config.readfp(open("config.cfg"))

flac_program = config.get("Paths", "flac_program")
metaflac_program = config.get("Paths", "metaflac_program")
lame_program = config.get("Paths", "lame_program")
adb_program = config.get("Paths", "adb_program")
download_root = config.get("Paths", "download_root")

stdout = open(devnull, 'wb')

def read_tag(file, tag):
    output = subprocess.check_output([metaflac_program, "--show-tag="+tag, file], universal_newlines=True)
    return output.split("\n")[0].split("=")[1]

def expand_flac_directory(artist, album):
    return join(config.get("Paths", "flac_root"), artist, album)
    
def expand_mp3_directory(mp3_type, artist, album):
    return join(config.get("Paths", "mp3_root"), mp3_type, artist, album)

def expand_phone_directory(mp3_type, artist, album):
    return "/".join([config.get("Paths", "phone_root"), mp3_type, artist, album])
    
def read_tags_from_flac(directory):   
    print("Reading FLAC tags from " + directory)
    out = {}
    
    for file in listdir(directory):
        if splitext(file)[1] == ".flac":
            tags = {}
            for tag in config.get("Tags", "tags").split(","):
                tags[tag] = read_tag(join(directory, file), tag)
            out[splitext(file)[0]] = tags
    
    print(out)
    
    return out
    
    
def decode_flac(directory):    
    print("Decoding FLAC to WAV")
    out = {}
    
    for file in listdir(directory):
        subprocess.call([flac_program, "-d", join(directory, file)], stdout = stdout, stderr = stdout)

def delete_files(directory, extension):   
    print("Deleting " + extension + " files in " + directory)
    for file in listdir(directory):
        if splitext(file)[1] == extension:
            remove(join(directory, file))
            
def delete_all_files(directory):   
    print("Deleting all files in " + directory)
    for file in listdir(directory):
        remove(join(directory, file))            

def ensure_directory_exists(directory):            
    if not exists(directory):
        print("Creating " + directory)
        makedirs(directory)
            
def encode_mp3(directory_in, directory_out, tags):
    print("Encoding WAV files in " + directory_in + " to MP3 files in " + directory_out)
    for file, tag_dictionary in tags.items():
        command = [
        lame_program,
        "-V5",
        join(directory_in, file) + ".wav",
        join(directory_out, file) + ".mp3",
        "--add-id3v2", 
        "--tt", tag_dictionary["TITLE"],
        "--ta", tag_dictionary["ARTIST"],
        "--tl", tag_dictionary["ALBUM"],
        "--ty", tag_dictionary["DATE"],
        "--tn", tag_dictionary["TRACKNUMBER"],
        "--tg", tag_dictionary["GENRE"],
        "--tv", "TPE2=" + tag_dictionary["ALBUMARTIST"]
        ]
        subprocess.call(command, stdout = stdout, stderr = stdout)
        
def push_all(files):
    for file in files:
        push(mp3_directory + "/" + file + ".mp3", phone_directory + "/" + file + ".mp3")
    
    push(mp3_directory + "/" + picture_file, phone_directory + "/" + picture_file)
        
def copy(source, destination):
    print("Copying " + source + " to " + destination)
    copyfile(source, destination)        

def get_picture_file(file):
    return "folder" + splitext(file)[1]
    
def push(source, destination):
    print("Pushing " + source + " to " + destination)
    subprocess.call([adb_program, "push", source, destination], stdout = stdout, stderr = stdout)
    
    print("Media scanning " + destination)
    command = [
        adb_program, "shell",
        "am", "broadcast",
        "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
        "-d", r'"file://' + destination + '"']
    subprocess.call(command, stdout = stdout, stderr = stdout)

parser = argparse.ArgumentParser(description = 'New CD Tool')
parser.add_argument('artist', action = 'store')
parser.add_argument('album', action = 'store')
parser.add_argument('picture', action = 'store')
parser.add_argument('-album_type', action = 'store', default = "Normal Releases")
args = parser.parse_args()
        
artist = args.artist
album = args.album
mp3_type = args.album_type
picture = args.picture

flac_directory = expand_flac_directory(artist, album)
mp3_directory = expand_mp3_directory(mp3_type, artist, album)
phone_directory = expand_phone_directory(mp3_type, artist, album)

picture_file = get_picture_file(picture)

#ensure_directory_exists(mp3_directory)
#delete_all_files(mp3_directory)
#copy(join(download_root, picture), join(mp3_directory, picture_file))
#delete_files(flac_directory, ".wav")
#decode_flac(flac_directory)
tags = read_tags_from_flac(flac_directory)
#encode_mp3(flac_directory, mp3_directory, tags)
#delete_files(flac_directory, ".wav")
#push_all(tags.keys())
