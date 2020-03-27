let graphDataSearchBox = new Vue({
    el: '#graphDataSearchBox',
    data: {
        dtBegStr: '',
        dtEndStr: '',
        stations: [],
        colNames: [],
        selectedStations: [],
        colKeySelected: [],
        setMode: 'mode0',
        dataSimplified: [],
        xAxis: '0',
        colRate: [],
        defaultColRate: '1',
        graphFrameID: 'graphFrame',
        graphSmooth: false,
        colMenuOpen: false,
        colMenuWidth: '90',
        colSets: [
            {
                title: '清空',
                set: []
            },
            {
                title: '日期',
                set: ['datetime']
            },
            {
                title: '大气污染物时序',
                set: ['datetime', 'PM10', 'PM2p5', 'SO2', 'NOX', 'NO', 'CO', 'O3']
            }
        ],
        graphOption: {},
        settingChange: false,
        dataReady: false,
        dataReadyStatus: 0,
        graphDataReady: false,
        graphReady: false,
        dataSpan: {}
    },
    computed: {
        settingReady: function() {
            if (this.dtBegStr != '' && this.dtEndStr != '' && this.dtBegStr < this.dtEndStr && this.selectedStations.length && this.colKeySelected.length) {
                return true
            }
            return false
        },
        colDisplayArr: function() {
            let cmpKey = genCmpFunc('key')
            let colArr = []
            if (this.setMode == 'mode0') {
                this.selectedStations.forEach(stationNo => {
                    colArr = colArr.concat(this.colNames[stationNo])
                })
                colArr = colArr.dropDuplicate(cmpKey)
            } else {
                this.selectedStations.forEach(stationNo => {
                    colArr = colArr.concat(this.colNames[stationNo])
                })
                colArr.sort(cmpKey)
                if (this.selectedStations.length > 1) {
                    let tmpArr = [],
                        tmp,
                        flag
                    for (let i = 0, len = colArr.length; i < len; i++) {
                        if (deepEquel(tmp, colArr[i])) {
                            flag++
                        } else {
                            tmp = colArr[i]
                            flag = 1
                        }
                        if (flag == this.selectedStations.length) {
                            tmpArr.push(simpleDeepCopy(tmp))
                        }
                    }
                    colArr = tmpArr
                }
            }
            return colArr
        },
        colSelected: function() {
            let colSelected = []
            for (let i = 0, len = this.colKeySelected.length; i < len; i++) {
                colSelected.push(settingProp.colsByKeys[this.colKeySelected[i]])
            }
            return colSelected
        }
    },
    methods: {
        isPC: isPC,
        changeSetting: function() {
            this.settingChange = !this.settingChange
        },
        changeDataSetting: function() {
            this.dataReady = false
            this.graphDataReady = false
            this.graphReady = false
            this.changeSetting()
        },
        changeGraphDataSetting: function() {
            this.graphDataReady = false
            this.graphReady = false
            this.changeSetting()
        },
        getDataSimplified: function() {
            let pointNum = settingProp.pointNum
            let stationTb, link, data
            let xhr = []
            for (let stationNo = 0, stationNum = this.stations.length; stationNo < stationNum; stationNo++) {
                stationTb = this.stations[stationNo]['db_table_name']
                link = '../php/qGETsimpData.php?table_name=' + stationTb + '&dtBegStr=' + this.dtBegStr + '&dtEndStr=' + this.dtEndStr + '&num=' + pointNum
                xhr[stationNo] = new XMLHttpRequest()
                xhr[stationNo].open('GET', link, true)
                xhr[stationNo].onload = function() {
                    if (this.status == 200) {
                        data = JSON.parse(this.responseText)
                        if (data['phpErrorCode'] != undefined) {
                            console.log('phpErrorCode', data['phpErrorCode'])
                            data = []
                        } else {
                            let keys = Object.keys(data[0]),
                                key
                            for (let i = 0, len = keys.length; i < len; i++) {
                                key = keys[i]
                                if (key != 'datetime') {
                                    for (let j = 0, len2 = data.length; j < len2; j++) {
                                        data[j][key] = parseFloat(data[j][key])
                                    }
                                }
                            }
                        }

                        console.log('auto dataready')
                        graphDataSearchBox.dataSimplified[stationNo] = data
                        graphDataSearchBox.dataReadyStatus++
                        if (graphDataSearchBox.dataReadyStatus == stationNum) {
                            graphDataSearchBox.dataReady = true
                            graphDataSearchBox.dataReadyStatus = 0
                        }
                    }
                }
                xhr[stationNo].send()
            }
        },
        genDataSpan: function() {
            let dataSpan = {},
                tmp,
                keys,
                key,
                len2,
                len3
            for (let iIndex = 0, i, len = this.selectedStations.length; iIndex < len; iIndex++) {
                i = this.selectedStations[iIndex]
                len2 = this.dataSimplified[i].length
                if (len2) {
                    keys = Object.keys(this.dataSimplified[i][0])
                    len3 = keys.length
                    for (let j = 0; j < len2; j++) {
                        for (let k = 0; k < len3; k++) {
                            key = keys[k]
                            tmp = this.dataSimplified[i][j][key]
                            // tmp = parseFloat(this.dataSimplified[i][j][this.colKeySelected[k]]);
                            if (tmp != undefined) {
                                if (dataSpan[key] == undefined) {
                                    dataSpan[key] = {
                                        min: tmp,
                                        max: tmp
                                    }
                                } else {
                                    if (dataSpan[key].min > tmp) {
                                        dataSpan[key].min = tmp
                                    }
                                    if (dataSpan[key].max < tmp) {
                                        dataSpan[key].max = tmp
                                    }
                                }
                            }
                        }
                    }
                }
            }
            // console.log(dataSpan);
            this.dataSpan = dataSpan
        },
        updateGraph: function() {
            let data = this.dataSimplified
            colRate = {}
            for (let i = 0, len = this.colSelected.length; i < len; i++) {
                if (this.colRate[i] != undefined && this.colRate[i] != 1 && this.xAxis != i) {
                    colRate[this.colSelected[i].key] = this.colRate[i]
                }
            }

            // 以key表示的自变量和应变量数组
            xAxis = this.colSelected[this.xAxis].key
            let yAxis = simpleDeepCopy(this.colSelected)
            yAxis.splice(this.xAxis, 1)
            for (let i = 0, len = yAxis.length; i < len; i++) {
                yAxis[i] = yAxis[i].key
            }
            let cmpX = genCmpFunc(xAxis)

            // 检查每个站点是否有此x轴
            let stationXpos = {},
                dataset = [],
                stationNum = 0
            for (let iIndex = 0, i, len = this.selectedStations.length; iIndex < len; iIndex++) {
                i = this.selectedStations[iIndex]
                if (data[i].length && data[i][0][xAxis] != undefined) {
                    stationXpos[i] = stationNum
                    data[i].sort(cmpX)
                    for (let j = 0, len2 = data[i].length; j < len2; j++) {
                        if (typeof dataset[j] != 'object') {
                            dataset[j] = []
                        }
                        dataset[j][stationNum] = data[i][j][xAxis]
                    }
                    stationNum++
                }
            }

            // 检查图线legend
            let legendInfo = [],
                info
            for (let i = 0, len = yAxis.length; i < len; i++) {
                for (let jIndex = 0, j, len2 = this.selectedStations.length; jIndex < len2; jIndex++) {
                    j = this.selectedStations[jIndex]
                    if (stationXpos[j] != undefined && data[j].length && data[j][0][yAxis[i]] != undefined) {
                        info = {
                            stationNo: j,
                            stationName: this.stations[j]['station_name2'],
                            colKey: yAxis[i],
                            colName: settingProp.colsByKeys[yAxis[i]].title,
                            rate: colRate[yAxis[i]]
                        }
                        legendInfo.push(simpleDeepCopy(info))
                    }
                }
            }

            let legend = [],
                series = [],
                dataGroup
            let longLegendFlag = this.selectedStations.length > 1
            for (let i = 0, len = legendInfo.length; i < len; i++) {
                if (longLegendFlag) {
                    legend[i] = legendInfo[i].stationName.slice(0, 2) + ' ' + legendInfo[i].colName
                } else {
                    legend[i] = legendInfo[i].colName
                }
                if (legendInfo[i].rate != undefined && legendInfo[i].rate != '') {
                    legend[i] += ' ×' + legendInfo[i].rate
                }
                dataGroup = data[legendInfo[i].stationNo]
                for (let j = 0, len2 = dataGroup.length; j < len2; j++) {
                    if (legendInfo[i].rate != undefined && legendInfo[i].rate != '') {
                        dataset[j][stationNum + i] = dataGroup[j][legendInfo[i].colKey] * legendInfo[i].rate
                    } else {
                        dataset[j][stationNum + i] = dataGroup[j][legendInfo[i].colKey]
                    }
                    series[i] = {
                        name: legend[i],
                        type: 'line',
                        encode: {
                            x: stationXpos[legendInfo[i].stationNo],
                            y: stationNum + i
                        },
                        smooth: this.graphSmooth
                    }
                }
            }

            let legendType = 'plain'
            let fontSize = 12
            if (!isPC()) {
                fontSize = 10
            }
            if (!isPC() || legend.length > settingProp.legendNum) {
                legendType = 'scroll'
            }

            this.graphOption = {
                title: {
                    text: ''
                },
                tooltip: {
                    trigger: 'axis'
                },
                legend: {
                    type: legendType,
                    data: legend
                },
                grid: {
                    top: '48px',
                    left: '15px',
                    right: '50px',
                    bottom: '25px',
                    // right: '4%',
                    // bottom: '3%',
                    containLabel: true
                },
                toolbox: {
                    orient: 'vertical',
                    top: '60px',
                    right: '10px',
                    feature: {
                        saveAsImage: {
                            show: true,
                            excludeComponents: ['toolbox'],
                            pixelRatio: 3
                        }
                    }
                },
                xAxis: {
                    type: xAxis == 'datetime' ? 'time' : 'value',
                    name: xAxis,
                    nameLocation: 'center',
                    nameTextStyle: {
                        // fontWeight: 'bold',
                        fontSize: 1.5 * fontSize,
                        padding: [2 * fontSize, 0, 0, 0]
                    }
                    // axisLabel: { interval:0, rotate:40 }
                },
                yAxis: {
                    type: 'value'
                },
                dataset: {
                    source: dataset
                },
                series: series
            }
            this.graphDataReady = true
            console.log('updateGraph')
            // genGraph();
        },
        genGraph: function() {
            if (this.graphDataReady && this.graphOption.legend.data.length) {
                this.graphReady = true
                let dom = document.getElementById(this.graphFrameID)
                let myChart = echarts.init(dom)
                if (this.graphOption && typeof this.graphOption === 'object') {
                    myChart.setOption(this.graphOption, true)
                }
            } else {
                this.graphReady = false
            }
        }
    },
    watch: {
        // 需要重新读取数据的
        dtBegStr: function() {
            this.changeDataSetting()
        },
        dtEndStr: function() {
            this.changeDataSetting()
        },
        selectedStations: function() {
            this.changeDataSetting()
        },
        // 需要重新生成数据矩阵的
        colKeySelected: function() {
            if (this.colKeySelected.length) {
                this.changeGraphDataSetting()
            }
        },
        colRate: function() {
            this.changeGraphDataSetting()
        },
        xAxis: function() {
            this.changeGraphDataSetting()
        },
        // 需要进行个别图像设置的
        graphSmooth: function() {
            if (this.graphDataReady) {
                for (let i = 0, len = this.graphOption.series.length; i < len; i++) {
                    this.graphOption.series[i].smooth = this.graphSmooth
                }
                this.genGraph()
            }
        },

        // 响应函数
        settingChange: function() {
            if (this.settingReady && !this.dataReady) {
                this.getDataSimplified()
            }
        },
        dataReady: function() {
            if (this.dataReady) {
                this.genDataSpan()
                if (!this.graphDataReady) {
                    this.updateGraph()
                    this.genGraph()
                }
            }
        },
        graphDataReady: function() {
            if (this.dataReady && !this.graphDataReady) {
                this.updateGraph()
                this.genGraph()
            }
        }
    },
    created: function() {
        this.dtBegStr = new Date().add(0, -24).Format('yyyy-MM-ddThh:mm')
        this.dtEndStr = new Date().Format('yyyy-MM-ddThh:mm')
    }
})
