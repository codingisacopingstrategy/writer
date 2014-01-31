Date.prototype.getWeek = function() {
    var onejan = new Date(this.getFullYear(),0,1);
    return Math.ceil((((this - onejan) / 86400000) + onejan.getDay()+1)/7);
};

Date.prototype.toISOish = function() {
    // like http://stackoverflow.com/questions/2573521/how-do-i-output-an-iso-8601-formatted-string-in-javascript
    // but we explicitly don’t want to use UTC time
    // ( maybe we should, at some time? )
    function pad(n) { return n < 10 ? '0' + n : n; }
    return this.getFullYear() + '-'
        + pad(this.getMonth() + 1) + '-'
        + pad(this.getDate()) + 'T'
        + pad(this.getHours()) + ':'
        + pad(this.getMinutes()) + ':'
        + pad(this.getSeconds());
};

var parseNum = function(n){
    var result = parseInt(n);
    return isNaN(result) ? null : result;
};

var Entry = function() {
    this.entry_allow_comments = 1;
    this.entry_allow_pings = 1;
    this.entry_atom_id = "";
    this.entry_basename = $("meta[property=entry_basename]").attr("content");
    this.entry_blog_id = 1;
    this.entry_category_id = null;
    this.entry_class = "entry";
    this.entry_convert_breaks = 0;
    this.entry_created_by = 3;
    this.entry_created_on = $("meta[property=entry_created_on]").attr("content");
    this.entry_current_revision = 0;
    this.entry_modified_by = parseNum($("meta[property=entry_modified_by]").attr("content"));
    this.entry_ping_count = 0;
    this.entry_pinged_urls = "";
    this.entry_tangent_cache = "";
    this.entry_template_id = null;
    this.entry_text_more = "";
    this.entry_to_ping_urls = "";
    // find properties set in body (user editable)
    this.entry_excerpt =        function(){
                                    /** The Facebook description */
                                   return $("meta[property=og:description").attr("content");
    };
    this.entry_keywords =       function( ){
                                    /** Actually used for the Facebook preview image*/
                                    return $("meta[property=og:image]").attr("content");
                                };
    this.entry_status =         function() {
                                    if ($("[property=entry_status]").is(':checked')) {
                                        // published:
                                        return 2;
                                    } else {
                                        return 1;
                                    }
                                };
    this.entry_id =             function() {
                                    if ($("[property=entry_id]").length == 0) {
                                        return false;
                                    } else {
                                        return parseInt($("[property=entry_id]").
                                                attr("content"));
                                    }
                                };
    this.entry_title =          function() {
                                    return $("[property=entry_title]").
                                            text();
                                };
    this.entry_author_id =      function() {
                                    return parseInt($("[property=entry_author_id]").
                                            find("option:selected").
                                                attr('value'));
                                };
    this.entry_authored_on =    function() {
                                    return $("[property=entry_authored_on]").
                                            attr("content");
                                };
    this.entry_modified_on =    function() {
                                    return $("meta[property=entry_modified_on]")
                                    .attr("content");
                                };
    this.entry_week_number =    function() {
                                    var d = new Date(this.entry_authored_on());
                                    var year = d.getFullYear();
                                    var week = d.getWeek();
                                    var weekNumber = year.toString() + week;
                                    return parseInt(weekNumber);
                                };
    this.entry_comment_count =  function() {
                                    return $("div.comment").length;
                                };
};

var Comment = function(el, text) {
    this.el =         el;
    this.comment_id =          function() {
                                    if (this.el.attr('property') === 'comment_id') {
                                        return parseInt(this.el.
                                            attr('content'));
                                    }
                                    return false;
                                };
    this.comment_author =      function() {
                                    if (this.el.find("[property=comment_author]").length === 0) {
                                        return this.el.find("select option:selected").
                                                text();
                                    }
                                    return this.el.find("[property=comment_author]").
                                                text();
                                };
    this.comment_blog_id = 1;
    this.comment_commenter_id = function() {
                                    if (this.el.find("select").length === 0) {
                                        return null;
                                    }
                                    return parseInt(this.el.find("select option:selected").
                                                attr('value'));
                                };

    this.comment_created_by = this.comment_commenter_id;
    this.comment_created_on =   function() {
                                    return this.el.find("[property=comment_created_on]").
                                            attr("content");
                                };
    this.comment_email =    function() {
                                    return this.el.find("[property=comment_email]").
                                            attr("content");
                                };
    this.comment_entry_id = entry.entry_id;
    this.comment_ip = "192.168.0.1";
    this.comment_junk_log = "";
    this.comment_junk_score = null;
    this.comment_junk_status = 1;
    this.comment_last_moved_on = "2000-01-01T00:00:00";
    this.comment_modified_by = null;
    this.comment_modified_on = null;
    this.comment_parent_id =    function() {
                                    if (this.el.parents(".comments-parent-container").length === 0) {
                                        return null;
                                    };
                                    return new Comment(this.el.parents(".comments-parent-container").first().prev(), "").comment_id();
                                };
    this.comment_text = text;
    this.comment_url =          function() {
                                    if (this.el.find("select").length === 0) {
                                        return this.el.find("[property=comment_url]").
                                                    attr('href');
                                    }
                                    return "";
                                };;
    this.comment_visible = 1;
    this.resource_uri =         function() {
                                    if (this.comment_id()) { 
                                        return "/api/comment/" + this.comment_id() + "/";
                                    }
                                    return "/api/comment/";
                                };
};

Entry.prototype.toHash = Comment.prototype.toHash = function() {
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

Entry.prototype.makeHash = Comment.prototype.makeHash = function(keys) {
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

Comment.prototype.update = function() {
    if (this.comment_id()) {
        console.log("it is an existing Comment object");
        var postData = this.makeHash(["comment_author", "comment_commenter_id", "comment_created_by", "comment_text", "comment_created_on", "comment_email",
 "comment_parent_id", "comment_url"]);
 
         console.log(JSON.stringify(postData));
         var url = this.resource_uri();
         
         var request = jQuery.ajax({
            url: url,
            type: "PATCH",
            data: JSON.stringify(postData),
            dataType: "json",
            contentType: "application/json",
            processData: false,
            success: function(data) {
                console.log("Succesfully updated Comment nr " + comment.comment_id());
            },
            error: function(xhr, status, error) {
                console.log("error!");
                console.log(xhr, status, error);
                },
            });
 
    } else {
        console.log("creating a new Comment object");
        console.log("to be implemented");
        
        var postData = this.toHash();
        delete postData.comment_id;
        delete postData.resource_uri;
        delete postData.el;
        
        var url = this.resource_uri();
        
        console.log(JSON.stringify(postData));
        
        var request = jQuery.ajax({
        url: url,
        type: "POST",
        data: JSON.stringify(postData),
        dataType: "json",
        contentType: "application/json",
        processData: false,
        success: function(data, textStatus, jqXHR) {
            console.log("Succesfully created Comment" + postData.comment_id);
            console.log(jqXHR.getResponseHeader('Location'));
            // I’m seeing some weird errors which I think are related to the
            // fact that we’re using a non-standard primary key (`comment_id`)
            // the url returned by the API doesn’t contain an id
            // (i.e. /api/comment/None/). So we can’t learn the id.
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
};



var entry;

var smartUpdate = function(jQueryEvent, eventArgument) {
    console.log(jQueryEvent, eventArgument);

    $("[property=entry_modified_on]").attr("content", new Date().toISOish());

    var e = eventArgument.editable;
    if (e.obj.hasClass("entry")) {
        console.log("started updating an Entry object");
        
        var entryId = entry.entry_id();
        
        if (entryId) {
            console.log("it is an existing Entry object");
            
            var postData = entry.makeHash(['entry_title', 'entry_status', 'entry_author_id', 'entry_authored_on', 'entry_modified_on', 'entry_week_number', 'entry_comment_count'] );
            postData.entry_text = cleanWhiteSpace(Aloha.activeEditable.originalObj[0], { indentationLevel : 2 }, document).innerHTML;
            
            console.log(JSON.stringify(postData));
            
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
            
            console.log('creating a new entry object');
            
            var postData = entry.toHash();
            postData.entry_text = Aloha.activeEditable.getContents();
            delete postData.entry_id;
            
            console.log(JSON.stringify(postData));
            
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
    } else if (e.obj.hasClass("comment-editor")) {
        console.log("started updating a Comment object");
        comment = new Comment(  e.obj.parents(".comment").first(), 
                                Aloha.activeEditable.getContents()  );
        comment.update();
    }
    
    };

Aloha.ready( function() {
    var $ = Aloha.jQuery;
    entry = new Entry();
    $('article, div.comment-editor').aloha();
    Aloha.bind('aloha-smart-content-changed', smartUpdate);
 });
