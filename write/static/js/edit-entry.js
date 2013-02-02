Date.prototype.getWeek = function() {
    var onejan = new Date(this.getFullYear(),0,1);
    return Math.ceil((((this - onejan) / 86400000) + onejan.getDay()+1)/7);
}

Date.prototype.toISOish = function() {
    // like http://stackoverflow.com/questions/2573521/how-do-i-output-an-iso-8601-formatted-string-in-javascript
    // but we explicitly don’t want to use UTC time
    // ( maybe we should, at some time? )
    function pad(n) { return n < 10 ? '0' + n : n }
    return this.getFullYear() + '-'
        + pad(this.getMonth() + 1) + '-'
        + pad(this.getDate()) + 'T'
        + pad(this.getHours()) + ':'
        + pad(this.getMinutes()) + ':'
        + pad(this.getSeconds());
};

var parseNum = function(n){
    var result = parseInt(n);
    return isNaN(result) ? null : result
}

var Entry = function() {
    // find properties set in metadata
    this.entry_allow_comments = parseNum($("meta[property=entry_allow_comments]").attr("content"));
    this.entry_allow_pings = parseNum($("meta[property=entry_allow_pings]").attr("content"));
    this.entry_atom_id = $("meta[property=entry_atom_id]").attr("content");
    this.entry_basename = $("meta[property=entry_basename]").attr("content");
    this.entry_blog_id = parseNum($("meta[property=entry_blog_id]").attr("content"));
    this.entry_category_id = parseNum($("meta[property=entry_category_id]").attr("content"));
    this.entry_class = $("meta[property=entry_class]").attr("content");
    this.entry_convert_breaks = $("meta[property=entry_convert_breaks]").attr("content");
    this.entry_created_by = parseNum($("meta[property=entry_created_by]").attr("content"));
    this.entry_created_on = $("meta[property=entry_created_on]").attr("content");
    this.entry_current_revision = parseNum($("meta[property=entry_current_revision]").attr("content"));
    this.entry_excerpt = $("meta[property=entry_excerpt]").attr("content");
    this.entry_keywords = $("meta[property=entry_keywords]").attr("content");
    this.entry_modified_by = parseNum($("meta[property=entry_modified_by]").attr("content"));
    this.entry_ping_count = parseNum($("meta[property=entry_ping_count]").attr("content"));
    this.entry_pinged_urls = $("meta[property=entry_pinged_urls]").attr("content");
    this.entry_status = parseNum($("meta[property=entry_status]").attr("content"));
    this.entry_tangent_cache = $("meta[property=entry_tangent_cache]").attr("content");
    this.entry_template_id = parseNum($("meta[property=entry_template_id]").attr("content"));
    this.entry_text_more = $("meta[property=entry_text_more]").attr("content");
    this.entry_to_ping_urls = $("meta[property=entry_to_ping_urls]").attr("content");
    this.entry_week_number = $("meta[property=entry_week_number]").attr("content");
    // find properties set in body (user editable)
    this.entry_id =          function() {
                                    if ($("[property=entry_id]").length == 0) {
                                        return false;
                                    } else {
                                        return parseInt($("[property=entry_id]").
                                                attr("content"));
                                    }
                                }
    this.entry_title =          function() {
                                    return $("[property=entry_title]").
                                            text();
                                }
    this.entry_author_id =      function() {
                                    return parseInt($("[property=entry_author_id]").
                                            attr("content"));
                                }
    this.entry_authored_on =    function() {
                                    return $("[property=entry_authored_on]").
                                            attr("content");
                            },
    this.entry_modified_on =    function() {
                                    return $("meta[property=entry_modified_on]")
                                    .attr("content");
                            },
    this.entry_week_number =    function() {
                                    var d = new Date(this.entry_authored_on())
                                    var year = d.getFullYear();
                                    var week = d.getWeek();
                                    var weekNumber = year.toString() + week;
                                    return parseInt(weekNumber);
                                }
    this.entry_comment_count =  function() {
                                    return $("div.comment").length
                                }
}

Entry.prototype.toHash = function() {
    var result = {};
    for (var property in this) {
    if (this.hasOwnProperty(property))
        if (typeof this[property] == "function") {
            result[property] = this[property]();
        } else {
            result[property] = this[property];
        }
        
    }
    return result;
};

Entry.prototype.makeHash = function(keys) {
    var result = {};
    for (i=0; i < keys.length; i++) {
        var property = keys[i];
        if (this.hasOwnProperty(property))
            if (typeof this[property] == "function") {
                result[property] = this[property]();
            } else {
                result[property] = this[property];
            }
    }
    return result;
};

var entry;

var smartUpdate = function(jQueryEvent, eventArgument) {
    console.log(jQueryEvent, eventArgument)

    $("[property=entry_modified_on]").attr("content", new Date().toISOish());

    var e = eventArgument.editable;
    if (e.obj.hasClass("entry")) {
        console.log("started updating an Entry object")
        
        var entryId = entry.entry_id();
        
        if (entryId) {
            console.log("it is an existing Entry object")
            
            var postData = entry.makeHash(['entry_title', 'entry_author_id', 'entry_authored_on', 'entry_modified_on', 'entry_week_number'] )
            postData.entry_text = Aloha.activeEditable.getContents()
            
            console.log(JSON.stringify(postData))
            
            var request = jQuery.ajax({
                url: "/api/entry/" + entryId + "/",
                type: "PATCH",
                data: JSON.stringify(postData),
                dataType: "json",
                contentType: "application/json",
                processData: false,
                success: function(data) {
                    console.log("Succesfully updated " + entry.entry_title());
                },
                error: function(xhr, status, error) {
                    console.log("error!");
                    console.log(xhr, status, error);
                    },
                });
        } else {
            
            console.log('creating a new entry object')
            
            var postData = entry.toHash()
            postData.entry_text = Aloha.activeEditable.getContents()
            delete postData.entry_id
            
            console.log(JSON.stringify(postData))
            
            var request = jQuery.ajax({
                url: "/api/entry/",
                type: "POST",
                data: JSON.stringify(postData),
                dataType: "json",
                contentType: "application/json",
                processData: false,
                success: function(data, textStatus, jqXHR) {
                    console.log("Succesfully created " + entry.entry_title());
                    console.log(jqXHR.getResponseHeader('Location'));
                    // I’m seeing some weird errors which I think are related to the
                    // fact that we’re using a non-standard primary key (`entry_id`)
                    // the url returned by the API doesn’t contain an id
                    // (i.e. /api/entry/None/). So we can’t learn the id.
                    // should reproduce on a smaller model and file a bug.
                    // for now we reload the page when a new post is created.
                    location.reload(true);
                },
                error: function(xhr, status, error) {
                    console.log("error!");
                    console.log(xhr, status, error);
                    },
                });
            
        }
    }
    
    };

Aloha.ready( function() {
    var $ = Aloha.jQuery;
    entry = new Entry();
    $('article').aloha();
    Aloha.bind('aloha-smart-content-changed', smartUpdate);
 });
