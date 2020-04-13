function loadDivRef() {
    let divRefStack = [
        {
            url: 'about.html',
            id: '#about'
        },
        {
            url: 'footingInfo.html',
            id: '#footingInfo'
        },
        {
            url: 'live.html',
            id: '#live'
        },
        {
            url: 'historyTable.html',
            id: '#historyTable'
        },
        {
            url: 'historyGraph.html',
            id: '#historyGraph'
        },
        {
            url: 'download.html',
            id: '#download'
        },
        {
            url: 'setting.html',
            id: '#setting'
        },
        {
            url: 'afterLoad.html',
            id: '#afterLoad'
        }
    ].reverse()

    function divRefStackPop() {
        if (divRefStack.length) {
            let divRef = divRefStack.pop()
            $(divRef['id']).load(divRef['url'], null, divRefStackPop)
            console.log(divRef['id'], 'loaded')
        }
    }
    divRefStackPop()
}

$(loadDivRef)

// 每一段时间运行站点实况页面刷新 5min
function timer5minFunc() {
    liveCard.refresh()
    console.log('Refresh 5min')
}

let timer5min = self.setInterval('timer5minFunc()', 1000 * 60 * 5)
