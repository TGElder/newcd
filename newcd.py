import configparser
from os import listdir
from os.path import join, splitext
import subprocess

config = configparser.ConfigParser()
config.readfp(open("config.cfg"))

flac_program = config.get("Paths", "flac_program")
metaflac_program = config.get("Paths", "metaflac_program")

def read_tag(file, tag):
    bytes = subprocess.check_output([metaflac_program, "--show-tag="+tag, file])
    return bytes.decode('utf-8').split("\r\n")[0].split("=")[1]

def read_tags(directory):

    abs_directory = join(config.get("Paths", "flac_root"), directory)
    
    out = {}
    
    for file in listdir(abs_directory):
        tags = {}
        for tag in config.get("Tags", "tags").split(","):
            tags[tag] = read_tag(join(abs_directory, file), tag)
        out[splitext(file)[0]] = tags
    
    return out
    
print(read_tags("Four Tet\\New Energy"))    
    
def decode_flac(directory):
    abs_directory = join(config.get("Paths", "flac_root"), directory)
    
    out = {}
    
    for file in listdir(abs_directory):
        subprocess.call([flac_program, "-d", join(abs_directory, file)])
    
    
decode_flac("Four Tet\\New Energy")