let liveCard = new Vue({
    el: "#liveCard",
    data: {
        titleIconType: 'ios-home',
        refreshIconType: 'ios-refresh-circle-outline',
        stations: [],
        colNames: [],
        firstLines: [],
        lastLines: [],
        statusCounter: 0,
        emptyPlaceHolder: '--',
    },
    computed: {
        stationInfo: function(){
            let stationInfo = [], info;
            let keyItem = settingProp.keyCols;
            let title, key;
            if(this.statusCounter == 2 * this.stations.length){
                info = {};
                for(let stationNo = 0, stationNum = this.stations.length; stationNo < stationNum; stationNo++){
                    info['title'] = this.stations[stationNo]['station_name2'];
                    info['dtBegStr'] = this.firstLines[stationNo]['datetime'];
                    info['dtEndStr'] = this.lastLines[stationNo]['datetime'];

                    info['lastData'] = [];
                    for(let dataNo = 0, dataNum = keyItem.length; dataNo < dataNum; dataNo++){
                        key   = keyItem[dataNo];
                        title = settingProp.colsByKeys[key].title;
                        data  = this.lastLines[stationNo][key];
                        if(data == undefined){
                            data = this.emptyPlaceHolder;
                        }
                        info['lastData'].push({'key': key, 'title': title, 'data': data});
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

                xhrFirst[stationNo].send();
                xhrLast[stationNo].send();
            }
        },
        getColNames: function(){
            let link;
            let xhr = [];
            let colNames = [];
            this.colNames = [];
            for(let stationNo = 0, stationNum = this.stations.length; stationNo < stationNum; stationNo++){
                link = "../php/qGET.php?q=SELECT en_name AS title, db_name AS `key` FROM col_info WHERE station" + stationNo + "=1";
                xhr[stationNo] = new XMLHttpRequest();
                xhr[stationNo].open("GET", link, true);
                xhr[stationNo].onload = function(){
                    if (this.status == 200){
                        colNames = JSON.parse(this.responseText);
                        if(colNames['phpErrorCode'] == undefined){
                            liveCard.colNames[stationNo] = colNames;
                            graphDataSearchBox.colNames[stationNo] = colNames;
                        }
                    }
                }
                xhr[stationNo].send();
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
            queryDetailLimited();
        },
    },
    created: function(){
        let q = "SELECT * FROM station_info";
        let xhr = new XMLHttpRequest();
        xhr.open("GET", "../php/qGET.php?q=" + q, true);
        xhr.onload = function(){
            if (this.status == 200){
                let stations = JSON.parse(this.responseText);
                if(stations['phpErrorCode'] == undefined){
                    liveCard.stations = stations;
                    liveCard.refresh();
                    liveCard.getColNames();
                    graphDataSearchBox.stations = stations;
                    dataSearchBox.stations = stations;
                    dataSearchBox.stationName = stations[0]['station_name2'];
                    dataDownloadingBox.stations = stations;
                }
            }
        }
        xhr.send();
    }
})
