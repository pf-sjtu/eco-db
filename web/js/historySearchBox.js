let dataSearchBox = new Vue({
    el: '#dataSearchBox',
    data: {
        stations: [{ station_name2: '错误' }],
        stationName: '',
        dtBegStr: '',
        dtEndStr: '',
        dataReady: false,
        colNames: [],
        colLen: 0,
        dataLen: 0
    },
    computed: {
        stationNo: function() {
            for (let i = 0; i < this.stations.length; i++) {
                if (this.stationName == this.stations[i]['station_name2']) {
                    return i
                }
            }
            return 0
        }
    },
    methods: {
        isPC: isPC,
        queryDetailLimited: function() {
            let dtBeg = new Date(this.dtBegStr)
            let dtEnd = new Date(this.dtEndStr)
            let dtNow = new Date()
            if (dtEnd > dtNow) {
                dtEnd = dtNow
                this.dtEndStr = dtEnd.Format('yyyy-MM-ddThh:mm')
            }
            let tsBeg = Date.parse(dtBeg)
            let tsBegMin = Date.parse(dtEnd) - settingProp.dataHour * 3600 * 1000
            if (tsBegMin > tsBeg) {
                dtBeg.setTime(tsBegMin)
                this.dtBegStr = dtBeg.Format('yyyy-MM-ddThh:mm')
                alert('由于性能限制，查询的时间跨度应该在' + settingProp.dataHour + '小时以内，已将起始时间修正为' + this.dtBegStr)
            } else {
                this.queryDetail(dataTab)
                this.dataReady = true
            }
        },
        queryDetail: function(targetTab) {
            targetTab.loading = true

            let columns = simpleDeepCopy(this.colNames[this.stationNo])
            for (let i = 0, len = columns.length; i < len; i++) {
                columns[i].width = '90px'
                columns[i].sortable = true
                if (columns[i].unit.length) {
                    columns[i].title += ' (' + columns[i].unit + ')'
                }
            }
            // createParamValues('width', '85px', columns);
            // createParamValues('sortable', 'true', columns);
            columns[0]['width'] = '150px'
            columns[0]['fixed'] = 'left'
            targetTab.columns = columns

            let data
            let xhr2 = new XMLHttpRequest()
            let q =
                'SELECT * FROM ' +
                this.stations[this.stationNo]['db_table_name'] +
                " WHERE datetime >= '" +
                this.dtBegStr +
                "' AND datetime <= '" +
                this.dtEndStr +
                "'"
            xhr2.open('GET', '../php/qGET.php?q=' + q, true)
            xhr2.onload = function() {
                if (this.status == 200) {
                    data = JSON.parse(this.responseText)
                    if (data['phpErrorCode'] == undefined) {
                        targetTab.tableData = data
                    } else {
                        targetTab.tableData = []
                        targetTab.columns = []
                    }
                    dataSearchBox.colLen = targetTab.columns.length
                    dataSearchBox.dataLen = targetTab.tableData.length
                    targetTab.loading = false
                }
            }
            xhr2.send()
        }
    },
    watch: {
        dtBegStr: function() {
            this.dataReady = false
        },
        dtEndStr: function() {
            this.dataReady = false
        }
    },
    created: function() {
        this.dtBegStr = new Date().add(0, -3).Format('yyyy-MM-ddThh:mm')
        this.dtEndStr = new Date().Format('yyyy-MM-ddThh:mm')
    }
})

let dataTab = new Vue({
    el: '#dataTab',
    data: {
        columns: [],
        tableData: [],
        loading: false,
        stripe: false,
        border: true,
        size: 'small'
    }
})
