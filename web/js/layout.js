$(function(){  
    // 加载各部分内容
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

var timer5min=self.setInterval("timer5minFunc()", 1000 * 60 * 5);
