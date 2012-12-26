#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Converting the MTML into django template the most straightforward way possible

subs = {u'<$mt:EntryBody$>' : u'{{ e.entry_text|safe }}',
}

def transform(template):
    for k, v in subs.iteritems():
        template = template.replace(k,v)
    return template


