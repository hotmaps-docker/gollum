import sys

langs = {
        'html': {
                'start': 'href="#',
                'stop': '">'
        },
        'html_2': {
                'start': "href='#",
                'stop': "'>"
        },
        'markdown': {
                'start': '(#',
                'stop': ')'
        }
}

# this function converts all markdown as well as html linkages of the following forms
# markdown: (#Some-Header-In-The-File)
# html: <a href="#Some-Header-In-The-File">
# to lower case linkages.
def lower_case_linkage (lines, start_symbol = '(#', stop_symbol = ')'):
        processed = []
        for i in lines:
                start = 0
                # in each line there might be more than one reference, hence check the whole line
                # until there are no more occurences.
                # obviously the loop will never break at this point...
                while start >= 0:
                        # get the start index and stop index of '(#Some-Header-In-The-File)'
                        start = i.find(start_symbol, start)
                        stop  = i.find(stop_symbol, start)
                        
                        # ... but at this point.
                        if start < 0:
                                break
                        
                        # wrong is the anchor name with upper case symbols. indices are set
                        # such that start and stop symbol are not included in the string.
                        wrong = i[start : stop+1]
                        correct = wrong.lower()
                        
                        # change line from text file
                        i = i.replace(wrong, correct)
                        start = stop
                processed.append(i)
        return processed

# writes the array elementwise to file
def write_lines_to_file (output_file_path, lines):
        with open(output_file_path, 'rw') as f:
                for line in lines:
                        f.write(line)

def write_lines_to_stdout (lines):
        for line in lines:
            print(line[:-1])

def handle_file (filename):
        input_file = open(filename, 'r')
        lines = input_file.readlines()
        
        for lang in langs:
            lines = lower_case_linkage(lines, langs[lang]['start'], langs[lang]['stop'])
       
        write_lines_to_stdout(lines)

handle_file(sys.argv[1])
