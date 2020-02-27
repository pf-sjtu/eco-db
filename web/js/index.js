let topNav = new Vue({
    el: '#topNav',
    data: {
        menuOpen: false,
        theme: 'light',
        menuWidth: '45rem',
        activeName: 5,
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
        isPC: function () {
            let userAgentInfo = navigator.userAgent;
            let Agents = ["Android", "iPhone", "SymbianOS", "Windows Phone", "iPod"];
            let flag = true;
            for (let v = 0; v < Agents.length; v++) {
                if (userAgentInfo.indexOf(Agents[v]) > 0) {
                    flag = false;
                    break;
                }
            }
            if(window.screen.width>=768){
                 flag = true;
            }
            return flag;
        },
        updateHiddenState: function(onSelectName){
            document.getElementById(this.items[this.activeName].contentID).hidden = true;
            document.getElementById(this.items[onSelectName].contentID).hidden = false;
            this.activeName = onSelectName;
            let footingHiddenFlag = true;
            for(let i = 0, len = this.footingActiveName.length; i < len; i++){
                if(onSelectName == this.footingActiveName[i]){
                    footingHiddenFlag = false;
                    break;
                }
            }
            document.getElementById("footing").hidden = footingHiddenFlag;
        }
    },
    created: function(){
        document.getElementById(this.items[this.activeName].contentID).hidden = false;
        for(let i = 0; i < this.items.length; i++){
            this.items[i]['titleBak'] = this.items[i]['title'];
        }
    }
});