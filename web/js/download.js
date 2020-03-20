let dataDownloadingBox = new Vue({
    el: "#dataDownloadingBox",
    data: {
        stations: [{station_name2: "错误"}],
        stationNoSelected: [],
        dtBegStr: "",
        dtEndStr: "",
        dataStatus: 0,
        colNames: [],
        dataArrays: [],
        csvInfo: [],
        csvData: [],
    },
    computed: {
        dataRequesting: function(){
            return this.dataStatus > 1;
        },
        dataReady: function(){
            return this.dataStatus == this.stationNoSelected.length + 1;
        }
    },
    methods: {
        requestData: function(){
            if(this.stationNoSelected.length){
                this.dataStatus++;
                this.dataArrays = [];
                this.csvInfo = [];
                this.csvData = [];
    
                let stationTb, link, data;
                let xhr = [];
                for(let stationKey = 0, stationNum = this.stationNoSelected.length; stationKey < stationNum; stationKey++){
                    this.csvInfo[stationKey] = {
                        stationInfo : this.stations[this.stationNoSelected[stationKey]],
                        dtBeg       : new Date(this.dtBegStr),
                        dtEnd       : new Date(this.dtEndStr)
                    };
                    this.csvInfo[stationKey].dtBegStr = this.csvInfo[stationKey].dtBeg.Format("yyyy-MM-dd hh:mm");
                    this.csvInfo[stationKey].dtEndStr = this.csvInfo[stationKey].dtEnd.Format("yyyy-MM-dd hh:mm");

                    stationTb = this.stations[this.stationNoSelected[stationKey]].db_table_name;
                    link = "../php/qGET.php?q=SELECT * FROM " + stationTb + " WHERE datetime >= '" + this.dtBegStr + "' AND datetime <= '" + this.dtEndStr + "'" + "&dtype=num";
    
                    xhr[stationKey] = new XMLHttpRequest();
                    xhr[stationKey].open("GET", link, true);
                    xhr[stationKey].onload = function(){
                        if (this.status == 200){
                            data = JSON.parse(this.responseText);
                            if(data['phpErrorCode'] != undefined){
                                console.log("phpErrorCode", data['phpErrorCode']);
                                data = [];
                            }
                            dataDownloadingBox.dataArrays[stationKey] = data;
                            dataDownloadingBox.dataStatus++;
                        }
                    }
    
                    xhr[stationKey].send();
                }
            }
        },
        genCsvData: function(){
            if(this.dataArrays.length){
                let stationNo;
                console.log('a');
                for(let i = 0, len = this.dataArrays.length, headertmp; i < len; i++){
                    stationNo = this.stationNoSelected[i];
                    this.csvData[i] = "";
                    headertmp = [];
                    for(let j = 0, len2 = this.colNames[stationNo].length; j < len2; j++){
                        if(this.colNames[stationNo][j].unit.length){
                            headertmp.push(this.colNames[stationNo][j].title + " (" + this.colNames[stationNo][j].unit + ")");
                        }
                        else{
                            headertmp.push(this.colNames[stationNo][j].title);
                        }
                    }
                    this.csvData[i] += headertmp.join(",") + "\n";
                    for(let j = 0, len2 = this.dataArrays[i].length; j < len2; j++){
                        this.csvData[i] += this.dataArrays[i][j].join(",") + "\n";
                    }
                }
            }
        },
        downloadCsv: function(){
            if(!this.csvData.length){
                this.genCsvData();
            }
            if(this.csvData.length && this.csvData.length == this.csvInfo.length){
                let stationName, dtBegStr, dtEndStr;
                for(let i = 0, len = this.csvInfo.length; i < len; i++){
                    stationName = this.csvInfo[i].stationInfo.station_name2;
                    dtBegStr = this.csvInfo[i].dtBeg.Format("yyyy-MM-dd_hh-mm");
                    dtEndStr = this.csvInfo[i].dtEnd.Format("yyyy-MM-dd_hh-mm");
                    downFile(this.csvData[i], stationName + "_" + dtBegStr + dtEndStr + ".csv");
                }
            }
        }
    },
    watch: {
        dtBegStr: function(){
            this.dataStatus = 0;
        },
        dtEndStr: function(){
            this.dataStatus = 0;
        },
        stationNoSelected: function(){
            this.dataStatus = 0;
        }
    },
    created: function(){
        this.dtBegStr = new Date().add(0, -24).Format("yyyy-MM-ddThh:mm");
        this.dtEndStr = new Date().Format("yyyy-MM-ddThh:mm");
    }
})