console.log("Init PyGDO.js v8.0.0");

window.gdo = {

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
}

window.onerror = window.gdo.error_js
