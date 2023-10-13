import io
import os
import csv
import json
import glob
import tkinter as tk
from zipfile import ZipFile
from tkinter.filedialog import askopenfilename

def acquire_file(manual_select, pattern, path = ''):
    '''select a .csv.zip file from Google Forms either manually, or by creation date.'''
    if manual_select is False:
        return max(glob.glob(f'{path}{pattern}.csv*.zip'), key=os.path.getctime)
    else:
        root = tk.Tk()
        root.withdraw()
        return askopenfilename()

def parse_file(filepath):
    '''produce a nested list from a csv.zip export from Google Forms.'''
    with ZipFile(filepath, 'r') as zipfile:
        with zipfile.open(zipfile.namelist()[0], 'r') as csvfile:
            reader = csv.DictReader(io.TextIOWrapper(csvfile, 'utf-8')) # Dict form could be of use later
            suggestions = []
            for entry in list(reader):
                suggestions.append(entry.values())
            return suggestions
        
def log_contents(log_data, writepath):
    suggest_archive = writepath
    set_data = []
    with open(suggest_archive, 'r+') as outfile:
        past_suggestions = json.load(outfile)
        if past_suggestions is not None:
            past_suggestions = [tuple(item) for item in past_suggestions]
        else:
            past_suggestions = []
        set_data = set(past_suggestions).union(log_data)
    with open(suggest_archive+'.temp', 'w') as writefile:
        writefile.write(json.dumps(list([list(item) for item in set_data]), indent=2))
    os.replace(suggest_archive, suggest_archive+'.old')
    if os.stat(suggest_archive+'.temp').st_size > os.stat(suggest_archive+'.old').st_size : # assuming some error if it has less to write
        os.rename(suggest_archive+'.temp',suggest_archive)
        # keeps .old file until next call just in case
    else:
        os.rename(suggest_archive+'.old', suggest_archive)
        os.remove(suggest_archive+'.temp')