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
        dataLen: 0,
        tabUnitCols: [],
    },
    computed: {
        stationNo: function () {
            for (let i = 0; i < this.stations.length; i++) {
                if (this.stationName == this.stations[i]['station_name2']) {
                    return i
                }
            }
            return 0
        },
    },
    methods: {
        isPC: isPC,
        queryDetailLimited: function () {
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
                this.queryDetail()
                this.dataReady = true
            }
        },
        queryDetail: function () {
            function htmlTab(columns, data) {
                dataArr = simpleDeepCopy(data)
                let headTabLeft = '<div class="headTableLeft"><table><tbody><th>' + columns.reverse().pop() + '</th></tbody></table></div>'
                columns.reverse()
                let headTab = '<div class="headTable"><table><tbody><th>' + columns.join('</th><th>') + '</th></tbody></table></div>'
                headTab = '<div class="headTableGroup">' + headTabLeft + headTab + '</div>'

                let dataTabLeft = ''
                let dataTab = ''
                for (let i = 0, len = dataArr.length; i < len; i++) {
                    dataTabLeft += '<tr><td>' + dataArr[i].reverse().pop() + '</td></tr>'
                    dataArr[i].reverse()
                    dataTab += '<tr><td>' + dataArr[i].join('</td><td>') + '</td></tr>'
                }
                dataTabLeft = '<div class="dataTableLeft"><table><tbody>' + dataTabLeft + '</tbody></table></div>'
                dataTab = '<div class="dataTable"><table><tbody>' + dataTab + '</tbody></table></div>'
                dataTab = '<div class="dataTableGroup">' + dataTabLeft + dataTab + '</div>'

                return headTab + dataTab
            }

            this.tabUnitCols = []
            for (let i = 0, len = this.colNames[this.stationNo].length; i < len; i++) {
                this.tabUnitCols.push(this.colNames[this.stationNo][i].title)
                if (this.colNames[this.stationNo][i].unit.length) {
                    this.tabUnitCols[i] += ' (' + this.colNames[this.stationNo][i].unit + ')'
                }
            }

            let data
            let xhr2 = new XMLHttpRequest()
            xhr2.open(
                'GET',
                '../php/qGETsta.php?tb=' +
                    this.stations[this.stationNo]['db_table_name'] +
                    '&dt_beg=' +
                    this.dtBegStr +
                    '&dt_end=' +
                    this.dtEndStr +
                    '&dtype=num',
                true
            )
            xhr2.onload = function () {
                if (this.status == 200) {
                    data = JSON.parse(this.responseText)
                    if (data['phpErrorCode'] != undefined) {
                        data = []
                    }
                    dataSearchBox.colLen = dataSearchBox.tabUnitCols.length
                    dataSearchBox.dataLen = data.length
                    let tabElem = document.getElementById('dataTab')
                    tabElem.innerHTML = htmlTab(dataSearchBox.tabUnitCols, data)
                    let dataElem = tabElem.getElementsByClassName('dataTable')[0]
                    dataElem.removeEventListener('scroll', dataTabScrollSync)
                    dataElem.addEventListener('scroll', dataTabScrollSync)
                }
            }
            xhr2.send()
        },
    },
    watch: {
        dtBegStr: function () {
            this.dataReady = false
        },
        dtEndStr: function () {
            this.dataReady = false
        },
    },
    created: function () {
        this.dtBegStr = new Date().add(0, -24).Format('yyyy-MM-ddThh:mm')
        this.dtEndStr = new Date().Format('yyyy-MM-ddThh:mm')
    },
})

function dataTabScrollSync() {
    let dataElem = document.getElementById('dataTab').getElementsByClassName('dataTable')[0]
    let dataElemLeft = document.getElementById('dataTab').getElementsByClassName('dataTableLeft')[0]
    let headElem = document.getElementById('dataTab').getElementsByClassName('headTable')[0]
    dataElemLeft.scroll(0, dataElem.scrollTop)
    headElem.scroll(dataElem.scrollLeft, 0)
}
