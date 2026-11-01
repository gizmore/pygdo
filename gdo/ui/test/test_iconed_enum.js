const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

let change;
global.window = {gdo: {}};
global.document = {addEventListener(name, handler) { if (name === 'change') change = handler; }};
vm.runInThisContext(fs.readFileSync('gdo/ui/js/pygdo-ui.js', 'utf8'));
const icon = {innerHTML: 'old'};
const select = {
    matches: selector => selector === 'select[data-iconed-enum]',
    closest: () => ({querySelector: () => icon}),
    selectedOptions: [{dataset: {iconHtml: '<i>new</i>'}}],
};
change({target: select});
assert.equal(icon.innerHTML, '<i>new</i>');
select.selectedOptions = [];
change({target: select});
assert.equal(icon.innerHTML, '');
