# External resources

Download or clone the following repositories and place them parallel to this
folder:

https://github.com/necolas/normalize.css.git
https://github.com/theleagueof/league-spartan/archive/master.zip
https://github.com/theleagueof/league-spartan.git
https://github.com/leemark/better-simple-slideshow.git


# Automatic page creation

The files `<pagename>.html` are created automatically using `make.py`.
Only `template.html` and `<pagename>_content.html` are to be edited.

To create pages, run:

`python3 make.py`


# Open website:

Either open `index.html`

or:

`cd path/to/this/directory/../`
`python3 -m http.server`

and open:

`localhost:8000/romhp/index.html`

Reference:  
https://developer.mozilla.org/en-US/docs/Learn/Common_questions/set_up_a_local_testing_server
