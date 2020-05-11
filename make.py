"""Create pages by copying the _template.html and inserting content at defined
markers. In a created file 'page.html', the included html code is taken from
'_page.html'.
"""

BASE_FILE = 'html/_template.html'
PAGES = [
    'index',
    'live',
    'media',
    'booking',
    'imprint',
]
PAGETITLE_SUFFIXES = {
    'live': 'Live',
    'media': 'Media',
    'booking': 'Booking',
    'imprint': 'Impressum & Datenschutz',
}
INCLUDE_MARKER = '<!-- #include:page_content -->'
GIGTABLE_MARKER = '<!-- #include:gigtable -->'
PAGETITLE_MARKER = '<!-- #include:page_title -->'

PAGEFILE_PATTERN = '{}.html'  # format with PAGES[n]
CONTENTFILE_PATTERN = 'html/_{}.html'  # format with PAGES[n]

ACTIVE_CLASS = 'active'
NOACTIVE_CLASS = 'noactive'

GIGFILE_UPCOMING = 'data/gigs_upcoming.txt'
GIGFILE_DONE = 'data/gigs_done.txt'
UPCOMING_TITLE = 'Kommende Shows'
DONE_TITLE = 'Vergangene Shows'
NOGIGS = 'momentan keine'


def get_file_content(filename):
    with open(filename, 'r') as file:
        content = file.read()
    return content


def include_snippet(infile, outfile, snippet, marker):
    """Include a snippet into a file at marked place.

    Parameters:
    -----------
    infile : str
        Name of file into which snippet shall be included
    outfile : str
        Name of new created file with included snippet
    snippet : str
        Snippet to be included
    marker : str
        Text to be replaced by snippet
    """
    source_data = get_file_content(infile)
    idx_begin = source_data.find(marker)
    indent_len = idx_begin - source_data.rfind('\n', 0, idx_begin) - 1
    snippet = snippet.replace('\n', '\n' + ' '*indent_len)
    outdata = source_data.replace(marker, snippet)
    with open(outfile, 'w') as ofile:
        ofile.write(outdata)


def make_pages(
    pages=PAGES,
    basefile=BASE_FILE,
    marker=INCLUDE_MARKER,
    pagefile_pattern=PAGEFILE_PATTERN,
    includefile_pattern=CONTENTFILE_PATTERN,
):
    for page in pages:
        outfile = pagefile_pattern.format(page)
        includefile = includefile_pattern.format(page)
        snippet = get_file_content(includefile)
        include_snippet(basefile, outfile, snippet, marker)
        

def set_active_class(
    pages=PAGES,
    active_class=ACTIVE_CLASS,
    noactive_class=NOACTIVE_CLASS,
    pagefile_pattern=PAGEFILE_PATTERN,
):
    """Set active and noactive classes in all files."""
    for page in pages:
        filename = pagefile_pattern.format(page)
        lines = get_file_content(filename).split('\n')
        with open(filename, 'w') as file:
            for line in lines:
                if noactive_class in line and page in line:
                    line = line.replace(noactive_class, active_class)
                file.write(line + '\n')


def include_page_titles(
    pages=PAGES,
    title_suffixes=PAGETITLE_SUFFIXES,
    pagefile_pattern=PAGEFILE_PATTERN,
    marker=PAGETITLE_MARKER,
):
    for page in pages:
        suffix = title_suffixes.get(page)
        if suffix:
            snippet = ' | {}'.format(suffix)
        else:
            snippet = ''
        filename = pagefile_pattern.format(page)
        include_snippet(filename, filename, snippet, marker)
        

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
        add_html = '<p class="tabvalueadd">{}</p>'.format(add)
    else:
        add_html = ''

    html_lines = [
        '<tr>',
        '    <td class="tabkey">{}</td>'.format(date),
        '    <td class="tabvalue">',
        '        ' + venue_html,
        '        ' + add_html,
        '    </td>',
        '</tr>',
    ]
    # remove 'add' line, if empty:
    html_lines = [l for l in html_lines if len(l.strip())]
    return '\n'.join(html_lines)


def create_gig_table(
    gigfile,
    title,
    set_hyperlink=True,
    alt=NOGIGS,
    css_class=None,
):
    keys = ['date', 'venue', 'url', 'add']
    gigs = load_gigs(gigfile, keys)
    if gigs:
        gigs_html = []
        for gig in gigs:
            gigs_html += [gig2html(gig, set_hyperlink=set_hyperlink)]
    else:
        gigs_html = ['<tr><td style="text-align: center">{}</td></tr>'.format(alt)]
    class_str = 'class="{}"'.format(css_class) if css_class else ''
    html_lines = [
        '<table {} role="table" aria-label="{}">'.format(class_str, title),
        '    <caption>{}</caption>'.format(title),
        '    <tbody>',
        *gigs_html,
        '    </tbody>',
        '</table>',
    ]
    return '\n'.join(html_lines)


def write_gig_tables_html(tables, outfile):
    html_lines = [
        '<div class="content">',
        *tables,
        '</div>',
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
        css_class='gig_table',
    )
    done_table = create_gig_table(
        gigfile=GIGFILE_DONE,
        title=DONE_TITLE,
        set_hyperlink=False,
        css_class='gig_table',
    )
    upcoming_table_home = create_gig_table(
        gigfile=GIGFILE_UPCOMING,
        title=UPCOMING_TITLE,
        set_hyperlink=True,
        css_class='gigs_home',
    )
    gigtable_file = CONTENTFILE_PATTERN.format('live')
    write_gig_tables_html([upcoming_table, done_table], gigtable_file)

    make_pages()
    index_file = PAGEFILE_PATTERN.format('index')
    include_snippet(index_file, index_file, upcoming_table_home, GIGTABLE_MARKER)
    
    set_active_class()
    include_page_titles()


if __name__ == '__main__':
    main()
