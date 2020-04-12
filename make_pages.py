"""Create pages by copying the index.html and replacing the html file name
to be included. That is, in a created file 'child.html', the included file
will be 'child_content.html'.
"""
import fileinput

input_filename = 'index.html'
textpattern = 'w3-include-html="{}_content.html"'
text_to_search = textpattern.format('index')

pages = [
    'live',
    'media',
    'booking',
    'imprint',
]

for page in pages:
    output_filename = page + '.html'
    replacement_text = textpattern.format(page)

    with open(output_filename, 'w') as outfile:
        print('create ' + output_filename)
        outfile.write('<!-- Automatically generated file by make_pages.py -->\n')
        with fileinput.FileInput(input_filename, inplace=False, backup='.bak') as file:
            for line in file:
                # set "active" and "noactive" classes, respectively:
                if 'noactive' in line and page in line:
                    line = line.replace('noactive', 'active')
                elif 'active' in line and 'index' in line:
                    line = line.replace('active', 'noactive')
                # insert pagename:
                outfile.write(line.replace(text_to_search, replacement_text))
