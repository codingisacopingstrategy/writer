# -*- coding: utf-8 -*-

from html5lib import HTMLParser, treebuilders
from cStringIO import StringIO

def tidy_html(text):
    p = HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
    dom_tree = p.parse(text)
    serialised = dom_tree.toprettyxml(indent='  ')
    # Remove unnecessary newlines: http://code.activestate.com/recipes/576750-pretty-print-xml/
    # And the [1:] is to remove the <? xml declaration
    return '\n'.join([line for line in serialised.split('\n') if line.strip()][1:])
    
def tidy_html_fragment(text):
    """
    Returns a well-formatted version of input HTML.
    http://stackoverflow.com/questions/2279404/how-can-i-add-consistent-whitespace-to-existing-html-using-python#answer-2284971
    """

    p = HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
    dom_tree = p.parseFragment(text)

    # using cStringIO for fast string concatenation
    pretty_HTML = StringIO()

    node = dom_tree.firstChild
    while node:
        node_contents = node.toprettyxml(indent='  ')
        pretty_HTML.write(node_contents)
        node = node.nextSibling

    output = pretty_HTML.getvalue()
    pretty_HTML.close()
    return output

class TidyMiddleware(object):
    # cf http://pyevolve.sourceforge.net/wordpress/?p=814
    def process_response(self, request, response):
        if response.status_code == 200:
            if response["content-type"].startswith("text/html"):
                response.content = tidy_html(response.content)
        return response
