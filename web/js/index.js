var leftMenu = new Vue({
    el: '#leftMenu',
    data: {
        mode: 'vertical',
        theme: 'light',
        width: '100%',
        activeName: 5,
        footingActiveName: [0, 5],
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
        ],
        // screenSizeSwitch
        wideMode: false,
        screenSizeSwitchTextWide: "展开",
        BodyWidthWide: "100%",
        contentNavWidthWide: "5%", // "60px",
        contentBodyWidthWide: "95%",
        screenSizeSwitchTextBak: "",
        BodyWidthBak: "",
        contentNavWidthBak: "",
        contentBodyWidthBak: ""
    },
    conputed: {},
    methods: {
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
        },
        switchScreenSize: function(){
            if(this.wideMode){
                for(var i = 0; i < this.items.length; i++){
                    this.items[i]['title'] = this.items[i]['titleBak'];
                }
                document.getElementById("contentBody").style.width = this.contentBodyWidthBak;
                document.getElementById("screenSizeSwitch").innerText = this.screenSizeSwitchTextBak;
                document.getElementById("container").style.width = this.BodyWidthBak;
                document.getElementById("contentNav").style.width = this.contentNavWidthBak;
                this.wideMode = false;
            }
            else{
                for(var i = 0; i < this.items.length; i++){
                    this.items[i]['title'] = "";
                }
                document.getElementById("screenSizeSwitch").innerText = this.screenSizeSwitchTextWide;
                document.getElementById("container").style.width = this.BodyWidthWide;
                document.getElementById("contentNav").style.width = this.contentNavWidthWide;
                document.getElementById("contentBody").style.width = this.contentBodyWidthWide;
                this.wideMode = true;
            }
        }
    },
    created: function(){
        document.getElementById(this.items[this.activeName].contentID).hidden = false;
        for(var i = 0; i < this.items.length; i++){
            this.items[i]['titleBak'] = this.items[i]['title'];
        }
        this.BodyWidthBak = document.getElementById("container").style.width;
        this.contentNavWidthBak = document.getElementById("contentNav").style.width;
        this.contentBodyWidthBak = document.getElementById("contentBody").style.width;
        this.screenSizeSwitchTextBak = document.getElementById("screenSizeSwitch").innerText;
    }
});