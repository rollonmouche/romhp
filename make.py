"""Create pages by copying the index.html and replacing all content between two
defined markers with defined html code. In a created file 'child.html', the
included html code is taken from 'child_content.html'.
"""


def get_file_content(filename):
    with open(filename, 'r') as file:
        content = file.read()
    return content


def make_pages(pages, source_filename, begin_marker, end_marker):
    source_data = get_file_content(source_filename)
    idx_begin = source_data.find(begin_marker)
    idx_end = source_data.find(end_marker, idx_begin) + len(end_marker)
    indent_len = idx_begin - source_data.rfind('\n', 0, idx_begin) - 1
    indent = ' '*indent_len
    text_to_replace = source_data[idx_begin:idx_end]
    print('make pages …')
    for page in pages:
        output_filename = page + '.html'
        with open(output_filename, 'w') as outfile:
            print(output_filename)
            outfile.write('<!-- Automatically generated file by make.py -->\n')
            content = get_file_content(page + '_content.html')
            content = content.replace('\n', '\n' + indent)
            outdata = source_data.replace(text_to_replace, content)
            outfile.write(outdata)
        

def set_active_class(pages):
    """Set "active" and "noactive" classes in all files."""
    print('set active class …')
    for page in pages:
        filename = page + '.html'
        print(filename)
        lines = get_file_content(filename).split('\n')
        with open(filename, 'w') as file:
            for line in lines:
                if 'noactive' in line and page in line:
                    line = line.replace('noactive', 'active')
                elif 'active' in line and 'index' in line:
                    line = line.replace('active', 'noactive')
                file.write(line + '\n')


def main():
    pages = [
        'live',
        'media',
        'booking',
        'imprint',
    ]
    source_filename = 'index.html'
    begin_marker = '<!-- #include-html-begin -->'
    end_marker = '<!-- #include-html-end -->'
    make_pages(pages, source_filename, begin_marker, end_marker)
    set_active_class(pages)


if __name__ == '__main__':
    main()
