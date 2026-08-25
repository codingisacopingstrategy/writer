function sanitize(html) {
    const container = document.createElement('div');
    container.innerHTML = html;
    const frag = document.createDocumentFragment();
    while (container.firstChild) frag.appendChild(container.firstChild);
    return frag;
}

function debounce(fn, delay) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
    };
}

const SaveStatus = {
    pending: 0,
    startedAt: 0,
    timer: 0,
    minSpin: 600,
    header() {
        return document.querySelector("header#site");
    },
    begin() {
        const header = this.header();
        if (!header) return;
        clearTimeout(this.timer);
        if (this.pending === 0) this.startedAt = Date.now();
        this.pending += 1;
        header.classList.remove("save-ok", "save-err");
        header.classList.add("save-pending");
    },
    end(ok) {
        const header = this.header();
        if (!header) return;
        this.pending = Math.max(0, this.pending - 1);
        if (this.pending > 0) return;
        const flash = () => {
            header.classList.remove("save-pending");
            header.classList.add(ok ? "save-ok" : "save-err");
            this.timer = setTimeout(() => {
                header.classList.remove("save-ok", "save-err");
            }, 900);
        };
        const wait = Math.max(0, this.minSpin - (Date.now() - this.startedAt));
        clearTimeout(this.timer);
        this.timer = setTimeout(flash, wait);
    },
};

function apiWrite(url, options) {
    SaveStatus.begin();
    return fetch(url, options)
        .then((res) => {
            if (!res.ok) {
                throw new Error(String(res.status));
            }
            if (res.status === 204 || (options && options.method === "DELETE")) {
                SaveStatus.end(true);
                return null;
            }
            return res.json().then((data) => {
                SaveStatus.end(true);
                return data;
            });
        })
        .catch((err) => {
            SaveStatus.end(false);
            throw err;
        });
}


// ---- Entry object ----
class Entry {
    constructor() {
        const meta = document.querySelector('meta[property="mt:entry_basename"]');
        this.slug = meta ? meta.getAttribute("content") : '';

        const editorEl = document.querySelector("article > section");
        const initialHTML = editorEl.innerHTML;
        let firstCall = true;

        //  make it editable
        this.editor = new Squire(editorEl, {
            blockTag: 'p',
            sanitizeToDOMFragment: html => {
                // Squire's constructor calls setHTML("") which would wipe
                // the server-rendered content. On that first call, return
                // the original DOM content instead.
                if (firstCall) {
                    firstCall = false;
                    return sanitize(initialHTML);
                }
                return sanitize(html);
            }
        });

        // sent edits to the API
        this.listener = editorEl.addEventListener(
            'input',
            debounce(() => this.update(), 1000)
        );

    }

    excerpt() {
        const input = document.getElementById("excerpt-input");
        if (input) return input.value;
        const meta = document.querySelector('meta[property~="og:description"]');
        return meta ? meta.content : '';
    }

    preview_image() {
        const input = document.getElementById("thumbnail-input");
        if (input) return input.value;
        const meta = document.querySelector('meta[property~="og:image"]');
        return meta ? meta.content : '';
    }

    custom_css() {
        const input = document.getElementById("custom-css-input");
        return input ? input.value : '';
    }

    rememberMeta() {
        document.querySelectorAll(".meta-field input, .meta-field textarea").forEach((input) => {
            input.dataset.saved = input.value;
            input.dispatchEvent(new Event("input"));
        });
    }

    patchFields(fields) {
        const entryId = this.id();
        if (!entryId) return this.update();
        return apiWrite(`/api/entry/${entryId}/`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(fields),
        });
    }

    published() {
        const btn = document.getElementById("publish-entry");
        if (btn) return btn.dataset.published === "true";
        const article = document.querySelector("article");
        return !!(article && article.dataset.published === "true");
    }

    markPublished() {
        const btn = document.getElementById("publish-entry");
        if (btn) {
            btn.dataset.published = "true";
            btn.textContent = "Save Modifications";
        }
        const article = document.querySelector("article");
        if (article) article.dataset.published = "true";
    }

    publishNow() {
        const btn = document.getElementById("publish-entry");
        const updateAll = !!(document.getElementById("publish-all") || {}).checked;
        if (btn) btn.disabled = true;
        return this.update()
            .then(() => {
                const entryId = this.id();
                if (!entryId) return;
                return apiWrite(`/api/entry/${entryId}/publish/`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ update_all: updateAll }),
                });
            })
            .then(() => this.markPublished())
            .catch((err) => console.error(err))
            .then(() => {
                if (btn) btn.disabled = false;
            });
    }

    id() {
        const e = document.querySelector('[property="mt:entry_id"]');
        return e ? parseInt(e.getAttribute("content")) : false;
    }

    title() {
        const e = document.querySelector('[property="mt:entry_title"]');
        return e ? e.textContent : '';
    }

    author() {
        const sel = document.querySelector('select[property="mt:entry_author_id"]');
        return sel ? parseInt(sel.value) : null;
    }

    created_on() {
        const e = document.querySelector('[property="dc:created"]');
        return e ? e.getAttribute("content") : '';
    }

    modified_on() {
        const meta = document.querySelector('meta[property="dc:modified"]');
        return meta ? meta.getAttribute("content") : '';
    }

    body() {
        const articleEditor = editors['main-article'];
        let txt = articleEditor ? articleEditor.getHTML() : document.querySelector('article').innerHTML;
        return txt;
    }

    toHash() {
        return {
            author: this.author(),
            title: this.title(),
            slug: this.slug,
            published: this.published(),
            created_on: this.created_on(),
            modified_on: this.modified_on(),
            excerpt: this.excerpt(),
            preview_image: this.preview_image(),
            custom_css: this.custom_css(),
            body: this.body()
        };
    }

    makeHash(keys) {
        const hash = {};
        for (const key of keys) {
            if (typeof this[key] === 'function') hash[key] = this[key]();
            else hash[key] = this[key];
        }
        return hash;
    }

    update() {
        console.log("update called");
        const modifiedEl = document.querySelector('[property="dc:modified"]');
        if (modifiedEl) modifiedEl.setAttribute('content', new Date().toISOString());

        const postData = this.makeHash(['author','title','slug','published','created_on','modified_on','excerpt','preview_image','custom_css','body']);
        postData.body = this.editor.getHTML();
        const entryId = this.id();
        const url = entryId ? `/api/entry/${entryId}/` : '/api/entry/';
        const method = entryId ? 'PATCH' : 'POST';
        console.log(postData);
        return apiWrite(url, {
            method,
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(postData)
        })
        .then(data => {
            console.log(entryId ? 'Updated entry' : 'Created entry', data);
            this.rememberMeta();
            if (!entryId) location.reload(true);
            return data;
        })
        .catch(err => {
            console.error(err);
            throw err;
        });

    }
}

// ---- Comment object ----
class Comment {
    constructor(el) {
        this.el = el;

        //  make it editable
        const editorEl = el.querySelector(".comment-editor");
        const initialHTML = editorEl.innerHTML;
        let firstCall = true;
        this.editor = new Squire(editorEl, {
            blockTag: 'p',
            sanitizeToDOMFragment: html => {
                if (firstCall) {
                    firstCall = false;
                    return sanitize(initialHTML);
                }
                return sanitize(html);
            }
        });

        // sent edits to the API
        this.listener = editorEl.addEventListener(
            'input',
            debounce(() => this.update(), 1000)
        );
    }

    id() {
        if (this.el.getAttribute('property') === 'mt:comment_id') {
            return parseInt(this.el.getAttribute("content"));
        }
        return null;
    }

    author() {
        const creator = this.el.querySelector('[property="dc:creator"]');
        if (creator) return creator.textContent;
        const sel = this.el.querySelector('select option:checked');
        return sel ? sel.textContent : '';
    }

    mt_author() {
        const sel = this.el.querySelector('select option:checked');
        return sel ? parseInt(sel.value) : null;
    }

    created_on() {
        const e = this.el.querySelector('[property="dc:created"]');
        return e ? e.getAttribute('content') : '';
    }

    email() {
        const e = this.el.querySelector('[property="mt:comment_email"]');
        return e ? e.getAttribute('content') : '';
    }

    entry() { return entry.id(); }

    parent() {
        const parentContainer = this.el.closest('.comments-parent-container');
        if (!parentContainer) return null;
        const prevComment = parentContainer.previousElementSibling;
        return prevComment ? new Comment(prevComment).id() : null;
    }

    text() {
        return this.editor ?
            this.editor.getHTML() :
            (this.el.querySelector('[property="mt:comment_text"]')?.innerHTML || '');
    }

    url() {
        const el = this.el.querySelector('[property="dc:creator"]');
        return el ? el.href : '';
    }

    visible() { return true; }

    resource_uri() {
        const id = this.id();
        return id ? `/api/comment/${id}/` : '/api/comment/';
    }

    update(createdCallback) {
        const modifiedEl = document.querySelector('[property="dc:modified"]');
        if (modifiedEl) modifiedEl.setAttribute('content', new Date().toISOString());

        const id = this.id();
        const postData = this.toHash();
        if (id) {
            apiWrite(this.resource_uri(), {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(postData)
            })
            .then(data => console.log('Updated comment', data))
            .catch(err => console.error(err));
        } else {
            apiWrite(this.resource_uri(), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(postData)
            })
            .then(data => {
                const id = data.id;
                console.log("Succesfully created Comment " + id);
                console.log(location);
                if (createdCallback) createdCallback(id);
            })
            .catch(err => console.error(err));
        }
    }

    delete() {
        const id = this.id();
        if (!id) return;
        apiWrite(this.resource_uri(), { method: 'DELETE' })
            .then(() => this.el.remove())
            .catch(err => console.error(err));
    }

    toHash() {
        let data = {
            id: this.id(),
            entry: this.entry(),
            author: this.author(),
            mt_author: this.mt_author(),
            created_on: this.created_on(),
            email: this.email(),
            ip: '192.168.0.1',
            parent: this.parent(),
            text: this.text(),
            url: this.url(),
            visible: this.visible()
        };
        if (!data.id) delete data.id;
        return data;
    }
}

// ---- Initialize editors ----
let entry = new Entry();
const editors = {}; // Store Squire editors by element id

const comments = {}
document.querySelectorAll("div.comment").forEach(el => {
    comments[el.id] = new Comment(el);
})
