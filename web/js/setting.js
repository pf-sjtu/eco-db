var settingProp = new Vue({
    el: "#settingProp",
    data: {
        pointNum: 30,
        pointNumMin: 10,
        pointNumMax: 1000,
        
        dataHour: 24,
        dataHourMin: 1,
        dataHourMax: 24 * 30,

        keyCols: ['PM10', 'PM2p5', 'SO2', 'NOX', 'NO', 'CO', 'O3'],
        cols: []
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
    created: function() {
        let link  = "../php/qGET.php?q=SELECT en_name AS title, db_name AS `key` FROM col_info;";
        let xhr = new XMLHttpRequest();
        xhr.open("GET", link, true);
        xhr.onload = function(){
            if (this.status == 200){
                data = JSON.parse(this.responseText);
                if(data['phpErrorCode'] == undefined){
                    settingProp.cols = data.dropDuplicate();
                }
            }
        }
        xhr.send();
    }
})