let settingProp = new Vue({
    el: "#settingProp",
    data: {
        pointNum: 30,
        pointNumMin: 10,
        pointNumMax: 300,
        
        legendNum: 18,
        legendNumMin: 0,
        legendNumMax: 30,

        dataHour: 24,
        dataHourMin: 1,
        dataHourMax: 24 * 30,

        keyCols: ['PM10', 'PM2p5', 'SO2', 'NOX', 'NO', 'CO', 'O3'],
        
        stations: [],
        cols: [],
        colNames: []
    },
    computed: {
        colsByKeys: function(){
            let colsByKeys = {};
            for(let i = 0, len = this.cols.length; i < len; i++){
                colsByKeys[this.cols[i].key] = this.cols[i];
            }
            return colsByKeys;
        }
    },
    methods: {
        getColNames: function(){
            let link;
            let xhrColArr = [];
            let colNames = [];
            for(let stationNo = 0, stationNum = this.stations.length; stationNo < stationNum; stationNo++){
                link = "../php/qGET.php?q=SELECT en_name AS title, db_name AS `key`, unit FROM col_info WHERE station" + stationNo + "=1";
                xhrColArr[stationNo] = new XMLHttpRequest();
                xhrColArr[stationNo].open("GET", link, true);
                xhrColArr[stationNo].onload = function(){
                    if (this.status == 200){
                        colNames = JSON.parse(this.responseText);
                        if(colNames['phpErrorCode'] != undefined){
                            console.log("INIT-colNames[" + stationNo + "]: phpErrorCode", colNames['phpErrorCode']);
                            colNames = [];
                        }
                        dataSearchBox.colNames[stationNo] = colNames;
                        graphDataSearchBox.colNames[stationNo] = colNames;
                        dataDownloadingBox.colNames[stationNo] = colNames;
                    }
                }
                xhrColArr[stationNo].send();
            }
        },
        getStations_getColNames: function(){
            let stations;
            let xhrStations = new XMLHttpRequest();
            xhrStations.open("GET", "../php/qGET.php?q=SELECT * FROM station_info;", true);
            xhrStations.onload = function(){
                if (this.status == 200){
                    stations = JSON.parse(this.responseText);
                    if(stations['phpErrorCode'] != undefined){
                        console.log("INIT-stations: phpErrorCode", data['phpErrorCode']);
                        stations = [];
                    }
                    settingProp.stations = stations;
                    settingProp.getColNames();
                    liveCard.stations = stations;
                    liveCard.refresh();
                    dataSearchBox.stations = stations;
                    dataSearchBox.stationName = stations[0]['station_name2'];
                    graphDataSearchBox.stations = stations;
                    dataDownloadingBox.stations = stations;
                }
            }
            xhrStations.send();
        },
        getCols_getStations_getColNames: function(){
            let cols;
            let xhrColAll = new XMLHttpRequest();
            xhrColAll.open("GET", "../php/qGET.php?q=SELECT en_name AS title, db_name AS `key`, unit FROM col_info;", true);
            xhrColAll.onload = function(){
                if (this.status == 200){
                    cols = JSON.parse(this.responseText);
                    if(cols['phpErrorCode'] != undefined){
                        console.log("INIT-cols: phpErrorCode", cols['phpErrorCode']);
                        cols = [];
                    }
                    let cmpKey = genCmpFunc('key');
                    settingProp.cols = cols.dropDuplicate(cmpKey);
                    settingProp.getStations_getColNames();
                }
            }
            xhrColAll.send();
        }
    },
    watch: {
        keyCols: function(){
            liveCard.keyCols = this.keyCols;
        }
    },
    created: function() {
        liveCard.keyCols = this.keyCols;
        this.getCols_getStations_getColNames();
    }
})