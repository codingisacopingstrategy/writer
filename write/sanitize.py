from html import escape
from html.parser import HTMLParser
from urllib.parse import urlparse


ALLOWED_TAGS = {
    "p": set(),
    "br": set(),
    "a": {"href", "title"},
    "em": set(),
    "strong": set(),
    "b": set(),
    "i": set(),
    "u": set(),
    "s": set(),
    "sub": set(),
    "sup": set(),
    "ul": set(),
    "ol": set(),
    "li": set(),
    "blockquote": set(),
    "div": set(),
}
VOID_TAGS = {"br"}
DROP_CONTENTS = {"script", "style", "iframe", "object", "embed", "noscript", "template"}
SAFE_HREF_SCHEMES = {"http", "https", "mailto"}


def safe_href(value):
    if not value:
        return None
    value = value.strip()
    if value.startswith("/") and not value.startswith("//"):
        return value
    parsed = urlparse(value)
    if parsed.scheme.lower() in SAFE_HREF_SCHEMES:
        return value
    return None


class _Sanitizer(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.stack = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in DROP_CONTENTS:
            self.skip += 1
            return
        if self.skip or tag not in ALLOWED_TAGS:
            return
        bits = [tag]
        for name, value in attrs:
            name = name.lower()
            if name not in ALLOWED_TAGS[tag]:
                continue
            if name == "href":
                value = safe_href(value)
                if not value:
                    continue
            bits.append('%s="%s"' % (name, escape(value or "", quote=True)))
        opened = "<%s>" % " ".join(bits)
        self.parts.append(opened)
        if tag not in VOID_TAGS:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in DROP_CONTENTS and self.skip:
            self.skip -= 1
            return
        if self.skip or tag in VOID_TAGS or tag not in ALLOWED_TAGS:
            return
        if tag not in self.stack:
            return
        while self.stack:
            opened = self.stack.pop()
            self.parts.append("</%s>" % opened)
            if opened == tag:
                break

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag.lower() not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_data(self, data):
        if self.skip:
            return
        self.parts.append(escape(data))

    def close(self):
        super().close()
        while self.stack:
            self.parts.append("</%s>" % self.stack.pop())


def sanitize_comment_html(html):
    if not html:
        return ""
    parser = _Sanitizer()
    parser.feed(html)
    parser.close()
    return "".join(parser.parts)
