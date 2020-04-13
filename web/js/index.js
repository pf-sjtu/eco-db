let topNav = new Vue({
    el: '#topNav',
    data: {
        menuOpen: false,
        theme: 'light',
        menuWidth: '45rem',
        activeName: 0,
        footingActiveName: [0, 1, 2, 3, 4, 5],
        items: [
            {
                title: '站点实况',
                iconType: 'ios-home',
                contentID: 'live'
            },
            {
                title: '数据图表',
                iconType: 'ios-stats',
                contentID: 'historyGraph'
            },
            {
                title: '数据条目',
                iconType: 'ios-paper',
                contentID: 'historyTable'
            },
            {
                title: '数据下载',
                iconType: 'ios-cloud-download',
                contentID: 'download'
            },
            {
                title: '设置',
                iconType: 'ios-settings',
                contentID: 'setting'
            },
            {
                title: '关于',
                iconType: 'ios-at',
                contentID: 'about'
            }
        ]
    },
    conputed: {},
    methods: {
        isPC: isPC,
        updateHiddenState: function(onSelectName) {
            document.getElementById(this.items[this.activeName].contentID).hidden = true
            document.getElementById(this.items[onSelectName].contentID).hidden = false
            this.activeName = onSelectName
            let footingHiddenFlag = true
            if (this.footingActiveName.indexOf(onSelectName) >= 0) {
                footingHiddenFlag = false
            }
            document.getElementById('footing').hidden = footingHiddenFlag
            this.menuOpen = false
            if (isPC()) {
                liveCard.liveMap.resize()
            }
        }
    },
    created: function() {
        document.getElementById(this.items[this.activeName].contentID).hidden = false
    }
})
