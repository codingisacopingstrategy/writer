Aloha.ready( function() {
    var $ = Aloha.jQuery;

    $('article').aloha();
    Aloha.bind('aloha-smart-content-changed', function(jQueryEvent, eventArgument) {
        console.log(jQueryEvent, eventArgument)

        var e = eventArgument.editable;
        var entryId = e.obj.attr('id').replace('entry-','');
        var postData = { 
            'entry_text' : Aloha.activeEditable.getContents() }

        console.log(JSON.stringify(postData))

        var request = jQuery.ajax({
            url: "/api/entry/" + entryId + "/",
            type: "PATCH",
            data: JSON.stringify(postData),
            dataType: "json",
            contentType: "application/json",
            processData: false,
            error: function(xhr, status, error) {
                console.log("error!");
                console.log(xhr, status, error);
                },
            });

        });
 });