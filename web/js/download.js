let dataDownloadingBox = new Vue({
    el: '#dataDownloadingBox',
    data: {
        stations: [{ station_name2: '错误' }],
        stationNoSelected: [],
        dtBegStr: '',
        dtEndStr: '',
        colNames: [],
        dataArrays: [],
        csvInfo: [],
        csvData: [],
        xhrArr: [],
        xhrCur: [],
        xhrCount: 0,
        xhrFinishedCount: 0,
        dataStatus: 0
    },
    computed: {
        progress: function () {
            if (this.xhrCount) {
                return this.xhrFinishedCount / this.xhrCount
            } else {
                return 0
            }
        },
        progressStr: function () {
            return Math.floor(this.progress * 100) + '%'
        },
        dataLength: function () {
            if (this.dataStatus == 2) {
                let dataLength = 0
                for (let i = 0, len = this.dataArrays.length; i < len; i++) {
                    dataLength += this.dataArrays[i].length
                }
                return dataLength
            } else {
                return -1
            }
        },
        dataEmpty: function () {
            let i = this.dataLength
            if (i > 1) {
                i = 1
            }
            return i
        },
        dataColor: function () {
            let colors = ['#43adf3', '#ff5500', '#5cb85c']
            return colors[this.dataEmpty + 1]
        }
    },
    methods: {
        eAuth: eAuth,
        isPC: isPC,
        requestData: function () {
            if (this.stationNoSelected.length) {
                this.dataStatus = 1
                this.dataArrays = []
                this.csvInfo = []
                this.csvData = []
                this.xhrArr = []
                this.xhrCount = 0
                this.xhrFinishedCount = 0
                this.xhrCur = []

                let stationTb, args, tmp
                let dtBeg = new Date(this.dtBegStr)
                let dtEnd = new Date(this.dtEndStr)
                for (let stationKey = 0, stationNum = this.stationNoSelected.length; stationKey < stationNum; stationKey++) {
                    this.csvInfo[stationKey] = {
                        stationInfo: this.stations[this.stationNoSelected[stationKey]],
                        dtBeg: dtBeg,
                        dtEnd: dtEnd,
                        dtBegStr: dtBeg.Format('yyyy-MM-dd hh:mm'),
                        dtEndStr: dtEnd.Format('yyyy-MM-dd hh:mm')
                    }
                    this.dataArrays[stationKey] = []
                    stationTb = this.stations[this.stationNoSelected[stationKey]].db_table_name

                    // 切割时间段
                    this.xhrArr[stationKey] = []
                    for (let dtEndCur = dtEnd, dtBegCur; dtEndCur > dtBeg; dtEndCur = dtBegCur) {
                        dtBegCur = dtEndCur.add(-settingProp.downloadDaySpan)
                        if (dtBegCur < dtBeg) {
                            dtBegCur = dtBeg
                        }
                        tmp = new XMLHttpRequest()
                        tmp.open(
                            'GET',
                            '../php/qGETsta.php?tb=' +
                                stationTb +
                                '&dt_beg=' +
                                dtBegCur.Format('yyyy-MM-dd hh:mm') +
                                '&dt_end=' +
                                dtEndCur.Format('yyyy-MM-dd hh:mm') +
                                '&dtype=num',
                            true
                        )
                        tmp.onload = function () {
                            if (this.status == 200) {
                                if (this.responseText[0] != '[' && this.responseText.length) {
                                    console.log(this.responseText)
                                } else {
                                    let data = JSON.parse(this.responseText)
                                    if (data['phpErrorCode'] != undefined) {
                                        console.log('phpErrorCode', data['phpErrorCode'])
                                        data = []
                                    }
                                    dataDownloadingBox.dataArrays[stationKey] = dataDownloadingBox.dataArrays[stationKey].concat(data)
                                }
                                dataDownloadingBox.xhrFinishedCount++
                                dataDownloadingBox.xhrPop()
                            }
                        }
                        this.xhrArr[stationKey].push(tmp)
                        this.xhrCount++
                    }
                }
                this.xhrPop()
            }
        },
        xhrPop: function () {
            if (this.xhrCur.length) {
                // pop one
                let xhr = this.xhrCur.pop()
                xhr.send()
            } else if (this.xhrArr.length) {
                // pop an array then pop one and add status
                this.xhrCur = this.xhrArr.pop()
                this.xhrPop()
            } else {
                // finish
                this.dataStatus = 2
                console.log('All POST requests Finished.')
            }
        },
        genCsvData: function () {
            if (this.dataArrays.length) {
                let stationNo
                for (let i = 0, len = this.dataArrays.length, headertmp; i < len; i++) {
                    stationNo = this.stationNoSelected[i]
                    this.csvData[i] = ''
                    headertmp = []
                    for (let j = 0, len2 = this.colNames[stationNo].length; j < len2; j++) {
                        if (this.colNames[stationNo][j].unit.length) {
                            headertmp.push(this.colNames[stationNo][j].title + ' (' + this.colNames[stationNo][j].unit + ')')
                        } else {
                            headertmp.push(this.colNames[stationNo][j].title)
                        }
                    }
                    this.csvData[i] += headertmp.join(',') + '\n'
                    for (let j = 0, len2 = this.dataArrays[i].length; j < len2; j++) {
                        this.csvData[i] += this.dataArrays[i][j].join(',') + '\n'
                    }
                }
            }
        },
        downloadCsv: function () {
            if (!this.csvData.length) {
                this.genCsvData()
            }
            if (this.csvData.length && this.csvData.length == this.csvInfo.length) {
                let stationName, dtBegStr, dtEndStr
                for (let i = 0, len = this.csvInfo.length; i < len; i++) {
                    stationName = this.csvInfo[i].stationInfo.station_name2
                    dtBegStr = this.csvInfo[i].dtBeg.Format('yyyy-MM-dd_hh-mm')
                    dtEndStr = this.csvInfo[i].dtEnd.Format('yyyy-MM-dd_hh-mm')
                    downFile(this.csvData[i], stationName + '_' + dtBegStr + dtEndStr + '.csv')
                }
            }
        }
    },
    watch: {
        dtBegStr: function () {
            this.dataStatus = 0
        },
        dtEndStr: function () {
            this.dataStatus = 0
        },
        stationNoSelected: function () {
            this.dataStatus = 0
        }
    },
    created: function () {
        this.dtBegStr = new Date().add(0, -24).Format('yyyy-MM-ddThh:mm')
        this.dtEndStr = new Date().Format('yyyy-MM-ddThh:mm')
    }
})
