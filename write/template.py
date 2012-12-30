#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Converting the MTML into django template the most straightforward way possible

header = """
<div id="header" class="container_7">
  <div class="grid_2">
  <h1><a href="/or/">i . like tight pants . net</a></h1>
  </div>
  <div class="grid_3">
<!--  <ul>
    
    <li class="current">latest</li>
    
    <li><a href="/and/about">about</a></li>
    <li><a href="/and/archives">index</a></li>
  </ul> -->&nbsp;
  </div>
  <div class="grid_2">
  <p class="byline">New entries published Monday and Thursday, 22:00 CET (<a href="/and/feed/us/recent_entries.xml">RSS</a>)</p>
  </div>
</div>
"""
pre_subs = {u"""    <mt:EntryPrevious><link rel="prev bookmark" href="<$mt:EntryPermalink regex_replace="/^http://i\.liketightpants\.net(.*)\.html/","$1"$>" title="I like tight pants and <$mt:EntryTitle encode_html="1" lower_case="1"$>" /></mt:EntryPrevious>
    <mt:EntryNext><link rel="next bookmark" href="<$mt:EntryPermalink regex_replace="/^http://i\.liketightpants\.net(.*)\.html/","$1"$>" title="I like tight pants and <$mt:EntryTitle encode_html="1" lower_case="1"$>" /></mt:EntryNext>
    <$mt:EntryTrackbackData$>
    <meta property="og:title" content="I like tight pants and <$mt:EntryTitle encode_html="1" lower_case="1"$>"/>
    <meta property="og:type" content="article"/>
    <meta property="og:url" content="<$mt:EntryPermalink replace=".html","" encode_xml="1"$>"/>
    <$mt:AuthorUserpicURL setvar="author_img"$>
    <meta property="og:image" content="<$mt:EntryKeywords _default="$author_img"$>"/>
    <meta property="og:site_name" content="<$mt:BlogName$>"/>
    <meta property="og:description"
          content="<$mt:EntryExcerpt$>"/>
    <meta property="fb:admins" content="1488294875"/>""" : u''}

subs = {u'<$mt:EntryBody$>' : u'{{ e.entry_text|safe }}',
u'<$mt:Include module="HTML Head"$>' : u"""<link rel="stylesheet" href="/and/style/in/style.css" type="text/css" />
<link rel="stylesheet" href="/and/style/in/reset.css" type="text/css" />
<link rel="stylesheet" href="/and/style/in/grid.css" type="text/css" />
<link rel="stylesheet" href="/and/style/in/style.css" type="text/css" />
<link rel="start" href="/and/" title="Home" />
<link rel="alternate" type="application/atom+xml" title="Recent Entries" href="/and/feed/us/recent_entries.xml" />
<script type="text/javascript" src="/and/scripts/being/jquery-1.5.min.js"></script>
<script type="text/javascript" src="/and/scripts/being/jquery.syntaxhighlighter.min.js"></script>
<script type="text/javascript" src="/and/scripts/being/scripts.js"></script>
<script type="text/javascript" src="/and/mt.js"></script>""",
u'<$mt:Include module="Header"$>' : header,
u'<$mt:EntryTrackbackData$>' : u'',
u'<$mt:Include module="Analytics"$>' : u'',
u'<$mt:Include module="Comments"$>' : u'',
u'<$mt:AuthorUserpicURL setvar="author_img"$>' : u'',
u'<$mt:EntryAuthorUsername setvar="entry_author_username"$>' : u'',
u'<$mt:EntryTitle encode_html="1" lower_case="1"$>' : u'{{ e.entry_title|lower }}',
u'<mt:EntryPrevious>' : u'{% with e=previous %}',
u'<mt:EntryNext>' : u'{% with e=next %}',
u'</mt:EntryPrevious>' : u'{% endwith %}',
u'</mt:EntryNext>' : u'{% endwith %}',
u'<$mt:EntryTitle$>' : u'{{ e.entry_title }}',
u'<$mt:EntryAuthorUsername$>' : u'{{ a.author_basename}}',
u'<$mt:EntryAuthorDisplayName$>' : u'{{ a.author_nickname }}',
u'<$mt:EntryPermalink regex_replace="/^http://i\.liketightpants\.net(.*)\.html/","$1"$>' : u'/or/{{ e.entry_basename }}',
u'<$mt:AuthorUserpic$>' : u'<img src="{{ a_thumbnail_url }}" style="width:100px;height:100px;" alt="" />',
u'<mt:Authors>' : u'{% for a in authors %}',
u'</mt:Authors>' : u'{% endfor %}',
u'<$mt:AuthorDisplayName$>' : u'{{ a.author_nickname }}',
u'<mt:Entries lastn="10">' : u'{% for e in recent_entries %}',
u'<mt:Entries author="$entry_author_username">' : u'{% for e in a_entries %}',
u'</mt:Entries>' : u'{% endfor %}',
u'<$mt:EntryDate $>' : u'{{ e.entry_authored_on|date:"F j, Y f A" }}',
 }

def transform(template):
    for k, v in pre_subs.iteritems():
        template = template.replace(k,v)
    for k, v in subs.iteritems():
        template = template.replace(k,v)
    return template


