import argparse
import json
import os
from file_handling_common import acquire_file, parse_file, log_contents

class Suggest:
    def __init__(self, args) -> None:
        self.args = args
        self.filepath = acquire_file(args.select, 'Suggest a Movie', path='suggestions/')
        self.file_contents = parse_file(self.filepath)
        self.parse_suggestions()
        self.export()

    def export(self):
        if self.args.outfile:
            with open('exports/.latestBallot.txt', 'w', encoding='utf-8') as outfile:
                outfile.write(str(self))
        else:
            print(self)

    
    def parse_suggestions(self):
        self.parsed_suggestions = []
        suggestion_log = []
        for timestamp, title, pitch, runtime, year, notes in self.file_contents: # doesnt work with older suggestions, need to swap to dicts
            title = title.strip()
            h, m, s = map(int, runtime.split(':'))
            notes = f'\n[{notes.strip()}]' if notes else ''
            pitch = pitch.replace('\n+','\n').strip()
            self.parsed_suggestions.append([title, f'{title} ({year}, {h}h{m:0>2}m)', f'{pitch}{notes}'])
            suggestion_log.append((title, year, timestamp))
        
        if not self.args.log:
            log_contents(suggestion_log, 'exports/all_suggested.json')
            
    def pretty_print(self):
        desc_prefix = 'NOW PLAYING: '
        div = '\n\n'
        form_desc = []
        question_key = []
        question_desc = []
        for _header, _ballot, _pitch in self.parsed_suggestions:
            form_desc.append(_header)
            question_key.append(_ballot)
            question_desc.append(f'{_ballot} - {_pitch}')

        form_desc = desc_prefix + ', '.join(form_desc)
        question_key = '\n'.join(question_key)
        question_desc = '\n\n'.join(question_desc)
        return div.join([form_desc, question_key, question_desc])
    
    def __str__(self) -> str:
        return self.pretty_print()

def main():
    parser = argparse.ArgumentParser(description='Parse suggest movies into strings for usage in runoff ballots')
    parser.add_argument('-s','--select',help='select a file instead of using the most recent expected filename',action='store_true')
    parser.add_argument('-o','--outfile',help='save parsed ballots to a file instead of terminal',action='store_true')
    parser.add_argument('-l','--log',help='block logfile output',action='store_true')
    args = parser.parse_args()
    Suggest(args)

if __name__ == "__main__":
    main()