console.log("Init PyGDO.js v8.0.2");

window.gdo = {

    init: function() {
        console.log('Inited PyGDO JS Engine v8.0.2');
        document.addEventListener('DOMContentLoaded', () => {
            for(mod of window.gdo) {
                if(mod.gdo_init) {
                    mod.gdo_init();
                }
            }
            document.body.classList.remove('no-js');
            document.body.classList.add('has-js');
        });
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
}

window.onerror = window.gdo.error_js
