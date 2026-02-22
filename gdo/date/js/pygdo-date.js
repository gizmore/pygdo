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
                values.push([value, window.gdo.t(unit)]);
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
            tse.innerHTML = window.gdo.date.humanDuration(t, 2, false) + gdo.t('ago');
        }
    },

};
