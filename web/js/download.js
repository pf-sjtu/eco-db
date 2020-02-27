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
            return this.dataStatus == this.stationNoSelected.length * 2 + 1;
        }
    },
    methods: {
        requestData: function(){
            if(this.stationNoSelected.length){
                this.dataStatus++;
                this.csvInfo = [];
                this.csvData = [];
    
                let stationTb, link, link2, colNames, data;
                let xhr = [], xhr2 = [];
                for(let stationKey = 0, stationNum = this.stationNoSelected.length; stationKey < stationNum; stationKey++){
                    this.csvInfo[stationKey] = {};
                    this.csvInfo[stationKey].stationInfo = this.stations[this.stationNoSelected[stationKey]];
                    this.csvInfo[stationKey].dtBeg = new Date(this.dtBegStr);
                    this.csvInfo[stationKey].dtEnd = new Date(this.dtEndStr);
                    this.csvInfo[stationKey].dtBegStr = this.csvInfo[stationKey].dtBeg.Format("yyyy-MM-dd hh:mm");
                    this.csvInfo[stationKey].dtEndStr = this.csvInfo[stationKey].dtEnd.Format("yyyy-MM-dd hh:mm");

                    stationTb = this.stations[this.stationNoSelected[stationKey]]['db_table_name'];
                    link = "../php/qGET.php?q=SELECT en_name AS title, db_name AS `key` FROM col_info WHERE station" + this.stationNoSelected[stationKey] + "=1";
                    link2 = "../php/qGET.php?q=SELECT * FROM " + stationTb + " WHERE datetime >= '" + this.dtBegStr + "' AND datetime <= '" + this.dtEndStr + "'" + "&dtype=num";
                    
                    xhr[stationKey] = new XMLHttpRequest();
                    xhr[stationKey].open("GET", link, true);
                    xhr[stationKey].onload = function(){
                        if (this.status == 200){
                            colNames = JSON.parse(this.responseText);
                            if(colNames['phpErrorCode'] != undefined){
                                console.log("phpErrorCode", colNames['phpErrorCode']);
                                colNames = [];
                            }
                            dataDownloadingBox.colNames[stationKey] = colNames;
                            dataDownloadingBox.dataStatus++;
                        }
                    }
    
                    xhr2[stationKey] = new XMLHttpRequest();
                    xhr2[stationKey].open("GET", link2, true);
                    xhr2[stationKey].onload = function(){
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
                    xhr2[stationKey].send();
                }
            }
        },
        genCsvData: function(){
            let headertmp;
            
            // console.log("this.colNames.length", this.colNames.length, "this.dataArrays.length", this.dataArrays.length);
            if(this.colNames.length && this.colNames.length == this.dataArrays.length){
                for(let i = 0, len = this.colNames.length; i < len; i++){
                    // console.log("Loading data", i);
                    this.csvData[i] = "";
                    headertmp = [];
                    for(let j = 0, len2 = this.colNames[i].length; j < len2; j++){
                        headertmp.push(this.colNames[i][j].title);
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
        this.dtEndStr = new Date().Format("yyyy-MM-ddThh:mm");
        let tsBeg = Date.parse(new Date()) - 24 * 3600 * 1000;
        let dtBeg = new Date()
        dtBeg.setTime(tsBeg);
        this.dtBegStr = dtBeg.Format("yyyy-MM-ddThh:mm");
    }
})