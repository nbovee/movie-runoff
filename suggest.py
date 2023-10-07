import io
import os
import csv
import glob
import argparse
import tkinter as tk
from random import randint
from zipfile import ZipFile
from tkinter.filedialog import askopenfilename

class Suggest:
    def __init__(self, args) -> None:
        self.select = not args.select
        self.filepath = self.acquire_file()
        self.file_contents = self.parse_file()

    def acquire_file(self):
        if self.select is True:
            files = glob.glob('../Suggest a Movie.csv*.zip')
            return max(files, key=os.path.getctime)
        else:
            root = tk.Tk()
            root.withdraw()
            return askopenfilename()

    def parse_file(self):
        with ZipFile(self.filepath, 'r') as zipfile:
            with zipfile.open(zipfile.namelist()[0], 'r') as csvfile:
                reader = csv.reader(
                    io.TextIOWrapper(csvfile, 'utf-8'))
                return list(reader)
                
    def pretty_print(self):
        div = '\n\n'
        ballot_desc = []
        question_key = []
        question_desc = []
        for _, title, pitch, runtime, year, notes in self.file_contents[1:]: # this freaked out as a comprehension for some reason
            title = title.strip()
            runtime = runtime.split(':')
            notes = '\n[' + notes.strip() + ']' if notes else ''
            pitch = pitch.strip()
            ballot_desc.append(title)
            question_key.append(f'{title} ({year}, {int(runtime[0])}h{runtime[1]}m)')
            question_desc.append(f'{title} ({year}, {int(runtime[0])}h{runtime[1]}m) - {pitch}{notes}')

        ballot_desc = ', '.join(ballot_desc)
        question_key = '\n'.join(question_key)
        question_desc = '\n\n'.join(question_desc)
        return div.join([ballot_desc, question_key, question_desc])
    
    def __str__(self) -> str:
        return self.pretty_print()

def main():
    parser = argparse.ArgumentParser(description='Parse suggest movies into strings for usage in runoff ballots')
    parser.add_argument('-s','--select',help='select a file instead of using the most recent expected filename',action='store_true')
    args = parser.parse_args()
    print(Suggest(args))

if __name__ == "__main__":
    main()