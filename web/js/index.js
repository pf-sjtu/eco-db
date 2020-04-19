let topNav = new Vue({
    el: '#topNav',
    data: {
        menuOpen: false,
        theme: 'light',
        menuWidth: '45rem',
        activeName: 0,
        items: menuElemAuth
    },
    conputed: {},
    methods: {
        eAuth: eAuth,
        isPC: isPC,
        updateHiddenState: function (onSelectName) {
            document.getElementById(this.items[this.activeName].contentID).hidden = true
            document.getElementById(this.items[onSelectName].contentID).hidden = false
            this.activeName = onSelectName
            this.menuOpen = false
            if (isPC()) {
                liveCard.liveMap.resize()
            }
        }
    },
    created: function () {
        document.getElementById(this.items[this.activeName].contentID).hidden = false
    }
})
