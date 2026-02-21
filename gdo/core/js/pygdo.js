"use strict";
window.gdo = {

    init: function() {
        window.onerror = window.gdo.error_js
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
       debugger;
    },

    error_js: function(a, b, c, d, e) {
        window.gdo.error(a)
    },

    fetch: function(module, method, data) {
        const url = window.gdo.config.webroot + module + "." + method + ".json";
        return window.fetch(url).catch(window.gdo.error_fetch);
    }
};
window.gdo.init();
