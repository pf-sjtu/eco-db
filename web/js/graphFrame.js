let graphDataSearchBox = new Vue({
    el: "#graphDataSearchBox",
    data: {
        dtBegStr: "",
        dtEndStr: "",
        stations: [],
        colNames: [],
        selectedStations: [],
        colKeySelected: [],
        setMode: "0",
        dataReady: false,
        dataSimplified: [],
        xAxis: "0",
        colRate: [],
        defaultColRate: "1",
        graphOption: {},
        graphFrameID: "graphFrame",
        graphSmooth: false,
        colMenuOpen: false,
        colMenuWidth: "90",
        colSets: [
            {
                title: "清空",
                set: []
            },
            {
                title: "日期",
                set: ["datetime"]
            },
            {
                title: "大气污染物时序",
                set: ["datetime", "PM10", "PM2p5", "SO2", "NOX", "NO", "CO", "O3"]
            }
        ]
    },
    computed: {
        colDisplayArr: function(){
            let cmpKey = genCmpFunc('key');
            let colArr = []
            if(this.setMode == 0){
                this.selectedStations.forEach(stationNo =>{
                    colArr = colArr.concat(this.colNames[stationNo]);
                });
                colArr = colArr.dropDuplicate(cmpKey);
            }
            else{
                this.selectedStations.forEach(stationNo =>{
                    colArr = colArr.concat(this.colNames[stationNo]);
                });
                colArr.sort(cmpKey);
                if(this.selectedStations.length > 1){
                    let tmpArr = [], tmp, flag;
                    for(let i = 0, len = colArr.length; i < len; i++){
                        if(deepEquel(tmp, colArr[i])){
                            flag++;
                        }
                        else{
                            tmp = colArr[i];
                            flag = 1;
                        }
                        if(flag == this.selectedStations.length){
                            tmpArr.push(simpleDeepCopy(tmp));
                        }
                    }
                    colArr = tmpArr;
                }
            }
            return colArr;
        },
        colSelected: function(){
            let colSelected = [];
            for(let i = 0, len = this.colKeySelected.length; i < len; i++){
                colSelected.push(settingProp.colsByKeys[this.colKeySelected[i]]);
            }
            return colSelected;
        }
    },
    methods: {
        getDataSimplified: function(async = true){
            let pointNum = settingProp.pointNum;
            let stationTb, link, data;
            let xhr = [];
            for(let stationNo = 0, stationNum = this.stations.length; stationNo < stationNum; stationNo++){
                stationTb = this.stations[stationNo]['db_table_name'];
                link = "../php/qGETsimpData.php?table_name=" + stationTb + "&dtBegStr=" + this.dtBegStr + "&dtEndStr=" + this.dtEndStr + "&num=" + pointNum;
                xhr[stationNo] = new XMLHttpRequest();
                xhr[stationNo].open("GET", link, async);
                xhr[stationNo].onload = function(){
                    if (this.status == 200){
                        data = JSON.parse(this.responseText);
                        if(data['phpErrorCode'] != undefined){
                            console.log("phpErrorCode", data['phpErrorCode']);
                            data = [];
                        }
                        graphDataSearchBox.dataSimplified[stationNo] = data;
                    }
                }
                xhr[stationNo].send();
            }
            this.dataReady = true;
        },
        updateGraph: function(){
            // 获取数据
            this.getDataSimplified(false);
            let data = this.dataSimplified;
            colRate = {};
            for(let i = 0, len = this.colSelected.length; i < len; i++){
                if(this.colRate[i] != undefined && this.colRate[i] != 1 && this.xAxis != i){
                    colRate[this.colSelected[i].key] = this.colRate[i];
                }
            }
            

            // 以key表示的自变量和应变量数组
            xAxis = this.colSelected[this.xAxis].key;
            let yAxis = simpleDeepCopy(this.colSelected);
            yAxis.splice(this.xAxis, 1);
            for(let i = 0, len = yAxis.length; i < len; i++){
                yAxis[i] = yAxis[i].key;
            }
            let cmpX = genCmpFunc(xAxis);
            
            // 检查每个站点是否有此x轴
            let stationXpos = {}, dataset = [], stationNum = 0;
            for(let i = 0, len = this.selectedStations.length; i < len; i++){
                if(data[i].length && data[i][0][xAxis] != undefined){
                    stationXpos[i] = stationNum;
                    data[i].sort(cmpX);
                    for(let j = 0, len2 = data[i].length; j < len2; j++){
                        if(typeof(dataset[j]) != 'object'){
                            dataset[j] = [];
                        }
                        dataset[j][stationNum] = data[i][j][xAxis];
                    }
                    stationNum++;
                }
            }

            // 检查图线legend
            let legendInfo = [], info;
            for(let i = 0, len = yAxis.length; i < len; i++){
                for(let j = 0, len2 = this.selectedStations.length; j < len2; j++){
                    if(stationXpos[j] != undefined && data[j].length && data[j][0][yAxis[i]] != undefined){
                        info = {
                            'stationNo': j,
                            'stationName': this.stations[j]['station_name2'],
                            'colKey': yAxis[i],
                            'colName': settingProp.colsByKeys[yAxis[i]].title,
                            'rate': colRate[yAxis[i]]
                        };
                        legendInfo.push(simpleDeepCopy(info));
                    }
                }
            }

            let legend = [], series = [], dataGroup, dataRate;
            for(let i = 0, len = legendInfo.length; i < len; i++){
                legend[i] = legendInfo[i].stationName + " " + legendInfo[i].colName;
                if(legendInfo[i].rate != undefined){
                    legend[i] += " ×" + legendInfo[i].rate;
                }
                dataGroup = data[legendInfo[i].stationNo];
                for(let j = 0, len2 = dataGroup.length; j < len2; j++){
                    if(legendInfo[i].rate != undefined){
                        dataset[j][stationNum + i] = dataGroup[j][legendInfo[i].colKey] * legendInfo[i].rate;
                    }
                    else{
                        dataset[j][stationNum + i] = dataGroup[j][legendInfo[i].colKey];
                    }
                    series[i] = {
                        'name': legend[i],
                        'type': 'line',
                        'encode': {
                            'x': stationXpos[legendInfo[i].stationNo],
                            'y': stationNum + i
                        },
                        'smooth': this.graphSmooth
                    };
                }
            }

            let option = {
                title: {
                    text: ''
                },
                tooltip: {
                    trigger: 'axis'
                },
                legend: {
                    data: legend
                },
                grid: {
                    // left: '3%',
                    // right: '4%',
                    // bottom: '3%',
                    containLabel: true
                },
                toolbox: {
                    feature: {
                        saveAsImage: {}
                    }
                },
                xAxis: {
                    type: xAxis=='datetime' ? 'time' : 'value',
                    name: xAxis
                },
                yAxis: {
                    type: 'value'
                },
                dataset: {
                    source: dataset
                },
                series: series
            };
            // console.log("option", option);
            // console.log("optionStr", JSON.stringify(option));

            let dom = document.getElementById(this.graphFrameID);
            let myChart = echarts.init(dom);
            if (option && typeof option === "object") {
                myChart.setOption(option, true);
            }
        }
    },
    watch: {
        dtBegStr: function(){
            this.dataReady = false;
        },
        dtEndStr: function(){
            this.dataReady = false;
        },
    },
    created: function(){
        this.dtEndStr = new Date().Format("yyyy-MM-ddThh:mm");
        let tsBeg = Date.parse(new Date()) - 24 * 3600 * 1000;
        let dtBeg = new Date()
        dtBeg.setTime(tsBeg);
        this.dtBegStr = dtBeg.Format("yyyy-MM-ddThh:mm");
    }
})