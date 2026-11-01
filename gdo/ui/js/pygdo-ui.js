"use strict"
window.gdo.ui = {
    srollToTop: function() {
    }
};

document.addEventListener('change', (event) => {
    const select = event.target;
    if (!select.matches('select[data-iconed-enum]')) return;
    const icon = select.closest('.gdt-iconed-enum')?.querySelector('[data-iconed-enum-icon]');
    if (icon) icon.innerHTML = select.selectedOptions[0]?.dataset.iconHtml || '';
});
