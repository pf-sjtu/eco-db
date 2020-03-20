let liveCard = new Vue({
    el: "#liveCard",
    data: {
        titleIconType: 'ios-home',
        refreshIconType: 'ios-refresh-circle-outline',
        stations: [],
        keyCols: [],
        firstLines: [],
        lastLines: [],
        statusCounter: 0,
        emptyPlaceHolder: '--',
    },
    computed: {
        stationInfo: function(){
            let stationInfo = [];
            let info, item;
            if(this.statusCounter == 2 * this.stations.length){
                info = {};
                for(let stationNo = 0, stationNum = this.stations.length; stationNo < stationNum; stationNo++){
                    info['title']    = this.stations[stationNo]['station_name2'];
                    info['dtBegStr'] = this.firstLines[stationNo]['datetime'];
                    info['dtEndStr'] = this.lastLines[stationNo]['datetime'];

                    info['lastData'] = [];
                    for(let dataNo = 0, dataNum = this.keyCols.length; dataNo < dataNum; dataNo++){
                        item = {};
                        item.key   = this.keyCols[dataNo];
                        item.title = settingProp.colsByKeys[item.key].title;
                        item.data  = this.lastLines[stationNo][item.key];
                        if(item.data == undefined){
                            item.data = this.emptyPlaceHolder;
                            item.unit = "";
                        }
                        else{
                            item.unit = settingProp.colsByKeys[item.key].unit;
                        }
                        info['lastData'].push(item);
                    }
                    stationInfo.push(simpleDeepCopy(info));
                }
            }
            return stationInfo;
        }
    },
    methods: {
        refresh: function(){
            let stationTb, linkFirst, linkLast;
            let xhrFirst = [];
            let xhrLast = [];
            this.statusCounter = 0;
            for(let stationNo = 0, stationNum = this.stations.length; stationNo < stationNum; stationNo++){
                stationTb = this.stations[stationNo]['db_table_name'];

                if(!liveCard.firstLines.length){
                    linkFirst = "../php/qGET.php?q=SELECT * FROM " + stationTb + " ORDER BY datetime ASC LIMIT 1;";
                    xhrFirst[stationNo] = new XMLHttpRequest();
                    xhrFirst[stationNo].open("GET", linkFirst, true);
                    xhrFirst[stationNo].onload = function(){
                        if (this.status == 200){
                            data = JSON.parse(this.responseText);
                            if(data['phpErrorCode'] == undefined){
                                liveCard.firstLines[stationNo] = data[0];
                                liveCard.statusCounter++;
                            }
                        }
                    }
                    xhrFirst[stationNo].send();
                }
                else{
                    liveCard.statusCounter++;
                }

                linkLast  = "../php/qGET.php?q=SELECT * FROM " + stationTb + " ORDER BY datetime DESC LIMIT 1;";
                xhrLast[stationNo] = new XMLHttpRequest();
                xhrLast[stationNo].open("GET", linkLast, true);
                xhrLast[stationNo].onload = function(){
                    if (this.status == 200){
                        data = JSON.parse(this.responseText);
                        if(data['phpErrorCode'] == undefined){
                            liveCard.lastLines[stationNo] = data[0];
                            liveCard.statusCounter++;
                        }
                    }
                }
                xhrLast[stationNo].send();
            }
        },
        jumpDetail: function(stationName2, dtBegStr){
            dataSearchBox.stationName = stationName2;
            let tmp = dtBegStr.replace(' ', 'T').split(':');
            tmp.length = 2;
            dtBegStr = tmp.join(':');
            dataSearchBox.dtBegStr = dtBegStr;
            dataSearchBox.dtEndStr = dtBegStr;
            topNav.updateHiddenState(2);
            dataSearchBox.queryDetailLimited();
        }
    }
})
