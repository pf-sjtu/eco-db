let settingProp = new Vue({
    el: '#settingProp',
    data: {
        //图像上的点数量
        pointNum: 60,
        pointNumMin: 10,
        pointNumMax: 300,
        //PC版本legend可滚动阈值数
        legendNum: 18,
        legendNumMin: 0,
        legendNumMax: 30,
        //数据图表时间跨度限制（小时）
        dataHour: 24 * 3,
        dataHourMin: 1,
        dataHourMax: 24 * 30,
        //实况页关键列
        keyCols: ['PM10', 'PM2p5', 'SO2', 'NOX', 'NO', 'CO', 'O3'],
        //数据下载页面天数跨度
        downloadDaySpan: 14,

        stations: [],
        cols: [],
        colNames: [],
    },
    computed: {
        colsByKeys: function () {
            let colsByKeys = {}
            for (let i = 0, len = this.cols.length; i < len; i++) {
                colsByKeys[this.cols[i].key] = this.cols[i]
            }
            return colsByKeys
        },
    },
    methods: {
        getColNames: function () {
            let link
            let xhrColArr = []
            let colNames = []
            for (let stationNo = 0, stationNum = this.stations.length; stationNo < stationNum; stationNo++) {
                // link = '../php/qGET.php?q=SELECT en_name AS title, db_name AS `key`, unit FROM col_info WHERE station' + stationNo + '=1'
                link = '../php/qGETcol.php?sta_i=' + stationNo
                xhrColArr[stationNo] = new XMLHttpRequest()
                xhrColArr[stationNo].open('GET', link, true)
                xhrColArr[stationNo].onload = function () {
                    if (this.status == 200) {
                        colNames = JSON.parse(this.responseText)
                        if (colNames['phpErrorCode'] != undefined) {
                            console.log('INIT-colNames[' + stationNo + ']: phpErrorCode', colNames['phpErrorCode'])
                            colNames = []
                        }
                        dataSearchBox.colNames[stationNo] = colNames
                        graphDataSearchBox.colNames[stationNo] = colNames
                        dataDownloadingBox.colNames[stationNo] = colNames
                    }
                }
                xhrColArr[stationNo].send()
            }
        },
        getStations_getColNames: function () {
            let stations
            let xhrStations = new XMLHttpRequest()
            // xhrStations.open('GET', '../php/qGET.php?q=SELECT * FROM station_info;', true)
            xhrStations.open('GET', '../php/qGETstaInfo.php', true)
            xhrStations.onload = function () {
                if (this.status == 200) {
                    stations = JSON.parse(this.responseText)
                    if (stations['phpErrorCode'] != undefined) {
                        console.log('INIT-stations: phpErrorCode', data['phpErrorCode'])
                        stations = []
                    }
                    settingProp.stations = stations
                    settingProp.getColNames()
                    liveCard.stations = stations
                    if (isPC()) {
                        liveCard.liveMap = genLiveMap()
                    }
                    liveCard.refresh()
                    loadingForward()
                    dataSearchBox.stations = stations
                    dataSearchBox.stationName = stations[0]['station_name2']
                    graphDataSearchBox.stations = stations
                    dataDownloadingBox.stations = stations
                }
            }
            xhrStations.send()
        },
        getCols_getStations_getColNames: function () {
            let cols
            let xhrColAll = new XMLHttpRequest()
            // xhrColAll.open('GET', '../php/qGET.php?q=SELECT en_name AS title, db_name AS `key`, unit FROM col_info;', true)
            xhrColAll.open('GET', '../php/qGETcol.php', true)
            xhrColAll.onload = function () {
                if (this.status == 200) {
                    cols = JSON.parse(this.responseText)
                    if (cols['phpErrorCode'] != undefined) {
                        console.log('INIT-cols: phpErrorCode', cols['phpErrorCode'])
                        cols = []
                    }
                    let cmpKey = genCmpFunc('key')
                    settingProp.cols = cols.dropDuplicate(cmpKey)
                    settingProp.getStations_getColNames()
                }
            }
            xhrColAll.send()
        },
    },
    watch: {
        keyCols: function () {
            liveCard.keyCols = this.keyCols
        },
    },
    created: function () {
        liveCard.keyCols = this.keyCols
        this.getCols_getStations_getColNames()
    },
})
