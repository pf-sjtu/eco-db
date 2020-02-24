var rand4 = rDigit(4);

var dataSearchBox = new Vue({
    el: "#dataSearchBox",
    data: {
        stations: [{station_name2: "错误"}],
        stationName: "",
        dtBegStr: "",
        dtEndStr: "",
        dataReady: false
    },
    computed: {
        stationNo: function(){
            for(var i = 0; i < this.stations.length; i++){
                if(this.stationName == this.stations[i]['station_name2']){
                    return i;
                }
            }
            return 0;
        }
    },
    watch: {
        dtBegStr: function(){
            this.dataReady = false;
        },
        dtEndStr: function(){
            this.dataReady = false;
        }
    },
    created: function(){
        this.dtEndStr = new Date().Format("yyyy-MM-ddThh:mm");
        var tsBeg = Date.parse(new Date()) - 3 * 3600 * 1000;
        var dtBeg = new Date()
        dtBeg.setTime(tsBeg);
        this.dtBegStr = dtBeg.Format("yyyy-MM-ddThh:mm");
    }
})

var dataTab = new Vue({
    el: "#dataTab",
    data: {
        columns: [],
        tableData: [],
        loading: false,
        stripe: false,
        border: true,
        size: "small"
    }
})

function queryDetailLimited(){
    var dtBeg = new Date(dataSearchBox.dtBegStr);
    var dtEnd = new Date(dataSearchBox.dtEndStr);
    var dtNow = new Date();
    if(dtEnd > dtNow){
        dtEnd = dtNow;
        dataSearchBox.dtEndStr = dtEnd.Format("yyyy-MM-ddThh:mm");
    }
    var tsBeg = Date.parse(dtBeg);
    var tsBegMin = Date.parse(dtEnd) - settingProp.dataHour * 3600 * 1000;
    if(tsBegMin > tsBeg){
        dtBeg.setTime(tsBegMin)
        dataSearchBox.dtBegStr = dtBeg.Format("yyyy-MM-ddThh:mm");
        alert("由于性能限制，查询的时间跨度应该在" + settingProp.dataHour + "小时以内，已将起始时间修正为" + dataSearchBox.dtBegStr);
    }
    else{
        queryDetail(dataTab);
        dataSearchBox.dataReady = true;
    }
}

function queryDetail(targetTab){
    targetTab.loading = true;
    var selectedStationNo = dataSearchBox.stationNo;
    var dtBegStr = dataSearchBox.dtBegStr;
    var dtEndStr = dataSearchBox.dtEndStr;
    var selectedStationTb = dataSearchBox.stations[selectedStationNo]["db_table_name"];
    var colNames, data;
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "../php/qGETcolNames.php?table_name=" + selectedStationTb + "&rand=" + rand4, true);
    xhr.onload = function(){
        if (this.status == 200){
            colNames = JSON.parse(this.responseText);
            createParamValues('width', '85px', colNames);
            createParamValues('sortable', 'true', colNames);
            colNames[0]['width'] = '150px';
            colNames[0]['fixed'] = 'left';
            targetTab.columns = colNames;
        }
    }
    xhr.send();
    // col values
    var xhr2 = new XMLHttpRequest();
    var q = "SELECT * FROM " + selectedStationTb + " WHERE datetime >= '" + dtBegStr + "' AND datetime <= '" + dtEndStr + "'";
    xhr2.open("GET", "../php/qGET.php?q=" + q, true);
    xhr2.onload = function(){
        if (this.status == 200){
                data = JSON.parse(this.responseText);
                if(data['phpErrorCode'] == undefined){
                    targetTab.tableData = data;
                }
                else{
                    targetTab.tableData = [];
                    targetTab.columns = [];
                }
                targetTab.loading = false;
            }
        }
    xhr2.send();
}