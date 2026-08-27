"use strict";
window.gdo.date = {

    gdo_init: function() {
        console.log("Loading date module")
        setInterval(window.gdo.date.updateTimes, 1000)
    },

    humanDuration: function(seconds, nUnits, withMillis) {
        const factors = {
            tu_us: 1000000,
            tu_ms: 1000,
            tu_s: 60,
            tu_m: 60,
            tu_h: 24,
            tu_d: 7,
            tu_w: 52.14,
            tu_y: 9999,
        };

        const values = [];
        const factorKeys = Object.keys(factors);
        const unitLabel = function(unit) {
            // Language JSON is loaded asynchronously. Never render a bare
            // number while it is still on its way; the stable unit suffix is
            // both readable and replaced by the translation on the next tick.
            return window.gdo.lang[unit] || unit.substring(3);
        };

        if (withMillis) {
            let remainder = seconds;
            for (const unit of factorKeys.slice(0, 2)) {
                let scaled = remainder * factors[unit];
                const value = Math.floor(scaled % 1000);
                remainder = Math.floor(scaled / 1000);
                if (value >= 1) {
                    values.push([value, unit]);
                }
            }
        }

        let remainder = Math.round(seconds);
        for (const unit of factorKeys.slice(2)) { // s and above
            const factor = factors[unit];
            const value = remainder % factor;
            remainder = Math.floor(remainder / factor);
            if (value) {
                values.push([value, unitLabel(unit)]);
            }
        }

        const result = values
            .slice(-nUnits)
            .reverse()
            .filter(([v]) => v)
            .map(([v, u]) => `${v}${u}`)
            .join(" ");

        return result || "0s";
    },

    updateTimes: function() {
        for(const tse of document.querySelectorAll('.ago[gdo-ts]')) {
            const ts = tse.getAttribute('gdo-ts')
            const t = (new Date().getTime()) / 1000.0 - parseFloat(ts)
            const ago = window.gdo.lang.ago ? ` ${gdo.t('ago')}` : '';
            tse.textContent = window.gdo.date.humanDuration(t, 2, false) + ago;
        }
    },

};
