"use strict";
window.gdo = {

    lang: {},

    init: function() {
        window.onerror = window.gdo.error_js;
        window.gdo.loadLanguage();
        document.addEventListener('DOMContentLoaded', () => {
            document.body.classList.remove('no-js');
            document.body.classList.add('has-js');
            for (const key in window.gdo) {
                const mod = window.gdo[key];
                mod && mod.gdo_init && mod.gdo_init();
            }
        });
    },

    gdo_init: function() {
        console.log('Inited PyGDO JS Engine v8.0.3-r1337+');
    },

    autofocus: function() {
    },

    error: function(msg) {
        alert(msg);
    },

    error_fetch: function(a, b, c, d, e, f) {
       window.gdo.error(a)
    },

    error_js: function(a, b, c, d, e) {
        window.gdo.error(a)
    },

    fetch: async function(url, data) {
//        const url = window.gdo.config.webroot + module + "." + method + ".json";
        return await window.fetch(url).catch(window.gdo.error_fetch);
    },

    t: function(key, args) {
        args ||= []
        return sprintf(window.gdo.lang[key], ...args)
    },

    loadLanguage: async function() {
        window.gdo.fetch('/core.language.json').then(async function(result) {
            let text = await result.text();
            window.gdo.lang = JSON.parse(text).data;
        });
    },
};

window.gdo.init();
