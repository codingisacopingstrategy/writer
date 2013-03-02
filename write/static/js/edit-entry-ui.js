var newCommentElement = function() { var el = $('<div class="comment">\n    <div class="comment-editor" property="comment_text">\n        <p>Welcome</p>\n    </div>\n    <p class="byline" property="comment_email" content="eric@ericschrijver.nl">\n        <img src="/and/assets/that/are/pictures/of/author/glit.png" width="18"\n        height="18" />by\n        <select>\n            <option value="3">glit</option>\n            <option value="4">jenseits</option>\n            <option value="5">habitus</option>\n            <option value="6">tellyou</option>\n            <option value="7">baseline</option>\n            <option value="8" selected="true">bnf</option>\n        </select>- <span property="comment_created_on" content="">October 12, 2012 10:27 AM</span>\n        <br\n        /> <a title="Reply" href="#reply">Reply</a>\n    </p>\n</div>\n');
    d = new Date();
    el.find("[property=comment_created_on]").attr("content", d.toISOish()).text(d.toLocaleString());
    el.find(".comment-editor").aloha();
    return el;
};

$(function() {
    $(".comments-content").on("click", "a[href=#reply]", function(e){
        var parent;
        var el = newCommentElement();
        e.preventDefault();
        console.log("adding a comment");
        if ($(this).parents(".comment").length !== 0) {
            console.log("not a root level comment");
            var parent = $(this).parents(".comment").first();
            if (parent.next().hasClass("comments-parent-container")) {
                console.log("there is already a container for children")
            } else {
                console.log("there is no container for children, adding one")
                parent.after('<div class="comments-parent-container" style="margin-left: 20px;" />')
            }
            parent.next().append(el);
        } else {
            console.log("root level comment");
            $(".comments-content").append(el);
        }
        c = new Comment(el,el.find(".comment-editor").text());
        console.log(c.comment_created_on());
        c.update();
        // how to find id?
        el.attr("property","comment_id");
        el.attr("content","");
    });
});
