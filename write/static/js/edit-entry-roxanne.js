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
        const meta = document.querySelector('meta[property~="og:description"]');
        return meta ? meta.content : '';
    }

    preview_image() {
        const meta = document.querySelector('meta[property~="og:image"]');
        return meta ? meta.content : '';
    }

    published() {
        const input = document.querySelector('input[property="mt:entry_status"]');
        return input ? input.checked : false;
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

        const postData = this.makeHash(['author','title','slug','published','created_on','modified_on','excerpt','preview_image','body']);
        postData.body = this.editor.getHTML();
        const entryId = this.id();
        const url = entryId ? `/api/entry/${entryId}/` : '/api/entry/';
        const method = entryId ? 'PATCH' : 'POST';
        console.log(postData);
        fetch(url, {
            method,
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(postData)
        })
        .then(res => res.json())
        .then(data => {
            console.log(entryId ? 'Updated entry' : 'Created entry', data);
            if (!entryId) location.reload(true);
        })
        .catch(err => console.error(err));

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
            fetch(this.resource_uri(), {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(postData)
            })
            .then(res => res.json())
            .then(data => console.log('Updated comment', data))
            .catch(err => console.error(err));
        } else {
            // New comment
            fetch(this.resource_uri(), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(postData)
            })
            .then(res => res.json())
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
        fetch(this.resource_uri(), { method: 'DELETE' })
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
