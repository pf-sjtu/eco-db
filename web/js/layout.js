function isPC() {
    let userAgentInfo = navigator.userAgent;
    let Agents = ["Android", "iPhone", "SymbianOS", "Windows Phone", "iPod"];
    let flag = true;
    for (let v = 0; v < Agents.length; v++) {
        if (userAgentInfo.indexOf(Agents[v]) > 0) {
            flag = false;
            break;
        }
    }
    if(window.screen.width>=768){
         flag = true;
    }
    return flag;
}

var isPCflag = isPC();

$(function(){  
    // 加载各部分内容
    $('#about').load('about.html');
    $('#footingInfo').load('footingInfo.html');
    $('#setting').load('setting.html');
    $('#historyGraph').load('historyGraph.html');
    $('#historyTable').load('historyTable.html');
    $('#download').load('download.html');
    $('#live').load('live.html');
})

// 每一段时间运行站点实况页面刷新 5min
function timer5minFunc(){
    liveCard.refresh();
    console.log("Refresh 5min");
}

let timer5min=self.setInterval("timer5minFunc()", 1000 * 60 * 5);
