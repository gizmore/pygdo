window.gdo.user = {
    openOnlineUsers: function(url) {
        const width = Math.round(window.screen.availWidth * 0.9);
        const height = Math.round(window.screen.availHeight * 0.9);
        window.open(url, 'pygdo-online-users', `popup=yes,width=${width},height=${height},resizable=yes,scrollbars=yes`);
        return false;
    },
};
