// <div property="mt:comment_id" content="{{ c.pk }}" id="comment-{{ c.pk }}" resource="/and/{{ e.slug }}#comment-{{ c.pk }}" class="comment{% if c.parent %} comment-reply{% endif %}{% if c.mt_author and c.mt_author.pk in author_ids %} {{ c.mt_author }}{% endif %}">
function newCommentElement() {
    const template = document.createElement('template');
    template.innerHTML = `
<div class="comment">
    <div class="comment-editor" property="comment_text">
        <p>Welcome</p>
    </div>
    <p class="byline" property="mt:comment_email" content="eric@ericschrijver.nl">
        by
        <select>
            <option value="3">glit</option>
            <option value="4">jenseits</option>
            <option value="5">habitus</option>
            <option value="6">tellyou</option>
            <option value="7">baseline</option>
            <option value="8" selected="true">bnf</option>
        </select>- <span property="dc:created" content="">October 12, 2012 10:27 AM</span>
        <br /> <button type="button" title="Reply" href="#reply">Reply</button> <button type="button" href="#delete"><b>×</b></button>
    </p>
</div>
`;

    const el = template.content.firstElementChild;

    const d = new Date();
    const created = el.querySelector('[property="dc:created"]');
    created.setAttribute("content", new Date().toISOString());
    created.textContent = d.toLocaleString();

    const editor = el.querySelector('.comment-editor');
    if (editor && editor.aloha) {
        editor.aloha();
    }

    return el;
}

/* Handle the insertion of nested comment elements */
document.querySelector(".comments-content").addEventListener("click", function (e) {
    const replyLink = e.target.closest('[href="#reply"]');
    if (!replyLink) return;

    e.preventDefault();

    const el = newCommentElement();
    console.log("adding a comment");

    const parentComment = replyLink.closest(".comment");

    if (parentComment) {
        console.log("not a root level comment");

        let container = parentComment.nextElementSibling;

        if (container && container.classList.contains("comments-parent-container")) {
            console.log("there is already a container for children");
        } else {
            console.log("there is no container for children, adding one");
            container = document.createElement("div");
            container.className = "comments-parent-container";
            container.style.marginLeft = "20px";
            parentComment.after(container);
        }

        container.appendChild(el);
    } else {
        console.log("root level comment");
        document.querySelector(".comments-content").appendChild(el);
    }

    const editorHTML = el.querySelector(".comment-editor").innerHTML;
    const c = new Comment(el, editorHTML);

    console.log(c.created_on());

    c.update(function (id) {
        el.setAttribute("property", "mt:comment_id");
        el.setAttribute("content", id);
    });
});

document.querySelector(".comments-content").addEventListener("click", function (e) {
    const deleteLink = e.target.closest('[href="#delete"]');
    if (!deleteLink) return;

    e.preventDefault();

    const parent = deleteLink.closest(".comment");
    const c = new Comment(parent);

    const confirmed = confirm("Delete?");
    if (confirmed) {
        c.delete();
    }
});

function bindMetaField(input, field, metaSelector) {
    if (!input) return;
    input.dataset.saved = input.value;
    const row = input.closest(".meta-field");
    if (!row) return;
    const cancel = row.querySelector(".meta-cancel");
    const save = row.querySelector(".meta-save");

    function dirty() {
        return input.value !== input.dataset.saved;
    }

    function syncButtons() {
        const on = dirty();
        cancel.disabled = !on;
        save.disabled = !on;
    }

    input.addEventListener("input", syncButtons);
    cancel.addEventListener("click", function () {
        input.value = input.dataset.saved;
        syncButtons();
    });
    save.addEventListener("click", function () {
        if (!dirty()) return;
        const value = input.value;
        if (metaSelector) {
            document.querySelectorAll(metaSelector).forEach(function (meta) {
                meta.setAttribute("content", value);
            });
        }
        if (field === "custom_css") {
            let style = document.getElementById("entry-custom-css");
            if (!value) {
                if (style) style.remove();
            } else {
                if (!style) {
                    style = document.createElement("style");
                    style.id = "entry-custom-css";
                    document.head.appendChild(style);
                }
                style.textContent = value;
            }
        }
        entry.patchFields({ [field]: value })
            .then(function () {
                input.dataset.saved = value;
                syncButtons();
            })
            .catch(function (err) {
                console.error(err);
            });
    });
    syncButtons();
}

bindMetaField(
    document.getElementById("excerpt-input"),
    "excerpt",
    'meta[property~="og:description"], meta[name="description"]'
);
bindMetaField(
    document.getElementById("thumbnail-input"),
    "preview_image",
    'meta[property~="og:image"]'
);
bindMetaField(document.getElementById("custom-css-input"), "custom_css");

const publishBtn = document.getElementById("publish-entry");
if (publishBtn) {
    publishBtn.addEventListener("click", function () {
        entry.publishNow();
    });
}

// ---- Squire toolbar ----
(function () {
    const toolbar = document.getElementById("squire-toolbar");
    const htmlSource = document.getElementById("squire-html-source");
    if (!toolbar || !htmlSource) return;

    const editorEl = document.querySelector("article > section");
    const editor = entry.editor;
    let sourceMode = false;

    // -- Show / hide toolbar on article focus --
    editorEl.addEventListener("focus", function () {
        toolbar.hidden = false;
        toolbar.classList.add("visible");
    });

    editorEl.addEventListener("blur", function () {
        if (sourceMode) return;
        if (typeof window.assetPickerOpen === "function" && window.assetPickerOpen()) return;
        toolbar.classList.remove("visible");
    });

    // Format‐tag to Squire method pairs (toggle style)
    const formatActions = {
        bold:           { tag: "B",   on: "bold",         off: "removeBold" },
        italic:         { tag: "I",   on: "italic",       off: "removeItalic" },
        underline:      { tag: "U",   on: "underline",    off: "removeUnderline" },
        strikethrough:  { tag: "S",   on: "strikethrough",off: "removeStrikethrough" },
        subscript:      { tag: "SUB", on: "subscript",    off: "removeSubscript" },
        superscript:    { tag: "SUP", on: "superscript",  off: "removeSuperscript" },
    };

    // -- Update active states from Squire's path --
    function updateActiveStates() {
        for (const [action, fmt] of Object.entries(formatActions)) {
            const btn = toolbar.querySelector(`[data-action="${action}"]`);
            if (btn) {
                btn.classList.toggle("active", editor.hasFormat(fmt.tag));
            }
        }
        // Link active state
        const linkBtn = toolbar.querySelector('[data-action="link"]');
        if (linkBtn) {
            linkBtn.classList.toggle("active", editor.hasFormat("A"));
        }
    }

    editor.addEventListener("pathChange", updateActiveStates);
    editor.addEventListener("select", updateActiveStates);
    editor.addEventListener("cursor", updateActiveStates);

    // -- Button click handler --
    toolbar.addEventListener("mousedown", function (e) {
        // Prevent toolbar clicks from stealing focus from the editor
        e.preventDefault();
    });

    toolbar.addEventListener("click", function (e) {
        const btn = e.target.closest("button[data-action]");
        if (!btn) return;
        const action = btn.dataset.action;

        // HTML source toggle
        if (action === "html") {
            sourceMode = !sourceMode;
            btn.classList.toggle("active", sourceMode);
            if (sourceMode) {
                htmlSource.value = editor.getHTML();
                htmlSource.hidden = false;
                editorEl.hidden = true;
                htmlSource.focus();
            } else {
                editor.setHTML(htmlSource.value);
                htmlSource.hidden = true;
                editorEl.hidden = false;
                editorEl.focus();
                entry.update();
            }
            return;
        }

        // Remove all formatting
        if (action === "removeAllFormatting") {
            editor.removeAllFormatting();
            editorEl.focus();
            return;
        }

        if (action === "image") {
            if (typeof window.openAssetPicker === "function") {
                window.openAssetPicker();
            }
            return;
        }

        // Link
        if (action === "link") {
            if (editor.hasFormat("A")) {
                editor.removeLink();
            } else {
                const url = prompt("URL:");
                if (url) editor.makeLink(url);
            }
            editorEl.focus();
            return;
        }

        // Inline format toggles
        const fmt = formatActions[action];
        if (fmt) {
            if (editor.hasFormat(fmt.tag)) {
                editor[fmt.off]();
            } else {
                editor[fmt.on]();
            }
            editorEl.focus();
        }
    });
})();
