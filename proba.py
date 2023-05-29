from os import listdir
from os.path import isfile, join
path = r"C:\Users\emanu\OneDrive\uvt\anul_2\PMD\TabsOnSpot\note-prediction\saved"
onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]

print(onlyfiles)
