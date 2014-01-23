var sys = require('sys');
var jsdom = require("jsdom");
var cleanWhiteSpace = require('./preflight').cleanWhiteSpace;
var fs=require('fs');

var indentationLevel = parseInt(process.argv[2]) || 0;
var options = { indentationLevel : indentationLevel };
var document = jsdom.jsdom(fs.readFileSync('/dev/stdin').toString());

var e = document.querySelector("div.article");
e.removeChild(e.querySelector("h4"));
e.removeChild(e.querySelector("div.comments"));
cleanWhiteSpace(e, options, document);

sys.puts(e.innerHTML);
