"""Create pages by copying the index.html and replacing all content between two
defined markers with defined html code. In a created file 'child.html', the
included html code is taken from 'child_content.html'.
"""

BASE_FILE = 'index.html'
PAGES = [
    'live',
    'media',
    'booking',
    'imprint',
]
INCLUDEMARKER_BEGIN = '<!-- #include-html-begin -->'
INCLUDEMARKER_END = '<!-- #include-html-end -->'
PAGEFILE_PATTERN = '{}.html'  # format with PAGES[n]
INCLUDEFILE_PATTERN = '{}_content.html'  # format with PAGES[n]

ACTIVE_CLASS = 'active'
NOACTIVE_CLASS = 'noactive'

GIGFILE_UPCOMING = 'gigs_upcoming.txt'
GIGFILE_DONE = 'gigs_done.txt'
UPCOMING_TITLE = 'Upcoming'
DONE_TITLE = 'Done'
NOGIGS = 'No upcoming shows'
GIG_TABLE_HTML_FILE = INCLUDEFILE_PATTERN.format('live')


def get_file_content(filename):
    with open(filename, 'r') as file:
        content = file.read()
    return content


def make_pages(
    pages=PAGES,
    basefile=BASE_FILE,
    begin_marker=INCLUDEMARKER_BEGIN,
    end_marker=INCLUDEMARKER_END,
    pagefile_pattern=PAGEFILE_PATTERN,
    includefile_pattern=INCLUDEFILE_PATTERN,
):
    source_data = get_file_content(basefile)
    idx_begin = source_data.find(begin_marker)
    idx_end = source_data.find(end_marker, idx_begin) + len(end_marker)
    indent_len = idx_begin - source_data.rfind('\n', 0, idx_begin) - 1
    indent = ' '*indent_len
    text_to_replace = source_data[idx_begin:idx_end]
    print('make pages …')
    for page in pages:
        output_filename = pagefile_pattern.format(page)
        with open(output_filename, 'w') as outfile:
            print(output_filename)
            outfile.write('<!-- Automatically generated file by make.py -->\n')
            content = get_file_content(includefile_pattern.format(page))
            content = content.replace('\n', '\n' + indent)
            outdata = source_data.replace(text_to_replace, content)
            outfile.write(outdata)
        

def set_active_class(
    pages=PAGES,
    active_class=ACTIVE_CLASS,
    noactive_class=NOACTIVE_CLASS,
    pagefile_pattern=PAGEFILE_PATTERN,
):
    """Set active and noactive classes in all files."""
    print('set active class …')
    for page in pages:
        filename = pagefile_pattern.format(page)
        print(filename)
        lines = get_file_content(filename).split('\n')
        with open(filename, 'w') as file:
            for line in lines:
                if noactive_class in line and page in line:
                    line = line.replace(noactive_class, active_class)
                elif active_class in line and 'index' in line:
                    line = line.replace(active_class, noactive_class)
                file.write(line + '\n')


def load_gigs(filename, keys):
    """Return list if gig dicts.
    
    Parameters:
    -----------
    filename : str
    keys : list of str
        Keys to search for, e.g., ['date', 'venue', 'url']
    """

    def parse_gig(gig_raw, keys):
        """Return dict representing one gig.
        
        Paramters:
        ----------
        gig_raw : str
            E.g.: 'date: 12.1.2018\nvenue: Meisenfrei\nurl: meisenfrei.de'
        keys :  list
        """
        gig = dict()
        lines = gig_raw.split('\n')
        for line in lines:
            for key in keys:
                key_ = key + ':'
                if line.startswith(key_):
                    gig[key] = line[len(key_):].strip()
        return gig

    data = get_file_content(filename)
    gigs_raw = data.split('#')
    gigs = []
    for gig_raw in gigs_raw:
        gig = parse_gig(gig_raw, keys)
        if gig:
            gigs.append(gig)
    return gigs


def gig2html(gig, set_hyperlink=True):
    """Create html representing a gig-table entry.
    
    Parameter:
    ----------
    gig : dict
        Required keys: date, venue
        Optional keys: url, add
    set_hyperlink : bool
        If False, don't use hyperlink, just display venue
    """
    date = gig['date']
    venue = gig['venue']
    url = gig.get('url')
    add = gig.get('add')
    
    if url and set_hyperlink:
        venue_html = '<p><a href="{}" target="_blank">{}</a></p>'.format(url, venue)
    else:
        venue_html = '<p>{}</p>'.format(venue)
    if add:
        add_html = '<p class="venueadd">{}</p>'.format(add)
    else:
        add_html = ''

    html_lines = [
        '<tr>',
        '    <td class="gigdate">{}</td>'.format(date),
        '    <td class="venue">',
        '        ' + venue_html,
        '        ' + add_html,
        '    </td>',
        '</tr>',
    ]
    # remove 'add' line, if empty:
    html_lines = [l for l in html_lines if len(l.strip())]
    return '\n'.join(html_lines)


def create_gig_table(gigfile, title, set_hyperlink, alt=NOGIGS):
    keys = ['date', 'venue', 'url', 'add']
    gigs = load_gigs(gigfile, keys)
    if gigs:
        gigs_html = []
        for gig in gigs:
            gigs_html += [gig2html(gig, set_hyperlink=set_hyperlink)]
    else:
        gigs_html = ['<tr><td style="text-align: center">{}</td></tr>'.format(alt)]
    
    html_lines = [
        '<table role="table" aria-label="{}">'.format(title),
        '    <caption>{}</caption>'.format(title),
        '    <tbody>',
        *gigs_html,
        '    </tbody>',
        '</table>',
    ]
    return '\n'.join(html_lines)


def write_gig_tables_html(tables, outfile):
    html_lines = [
        '<section>',
        *tables,
        '</section>',
        '',
    ]
    html = '\n'.join(html_lines)
    with open(outfile, 'w') as ofile:
        ofile.write(html)


def main():
    upcoming_table = create_gig_table(
        gigfile=GIGFILE_UPCOMING,
        title=UPCOMING_TITLE,
        set_hyperlink=True,
    )
    done_table = create_gig_table(
        gigfile=GIGFILE_DONE,
        title=DONE_TITLE,
        set_hyperlink=False,
    )
    write_gig_tables_html([upcoming_table, done_table], GIG_TABLE_HTML_FILE)

    make_pages()
    set_active_class()


if __name__ == '__main__':
    main()
