let elemInfo = {
    live: {
        title: '站点实况',
        iconType: 'ios-home',
        contentID: 'live',
        url: 'live.html',
        desc: '站点最新数据信息展示和对比'
    },
    historyGraph: {
        title: '数据图表',
        iconType: 'ios-stats',
        contentID: 'historyGraph',
        url: 'historyGraph.html',
        desc: '数据项目的时间序列作图'
    },
    historyTable: {
        title: '数据条目',
        iconType: 'ios-paper',
        contentID: 'historyTable',
        url: 'historyTable.html',
        desc: '数据项目实测数据表在线展示'
    },
    download: {
        title: '数据下载',
        iconType: 'ios-cloud-download',
        contentID: 'download',
        url: 'download.html',
        desc: 'CSV格式数据导出和下载'
    },
    setting: {
        title: '设置',
        iconType: 'ios-settings',
        contentID: 'setting',
        url: 'setting.html',
        desc: '网页相关约束设置'
    },
    account: {
        title: '账户',
        iconType: 'ios-person',
        contentID: 'account',
        url: 'account.php',
        desc: '账号信息'
    },
    about: {
        title: '关于',
        iconType: 'ios-at',
        contentID: 'about',
        url: 'about.html',
        desc: '网页信息和更新历史'
    },
    footingInfo: {
        title: '页脚',
        contentID: 'footingInfo',
        url: 'footingInfo.html',
        desc: '页脚'
    },
    afterLoad: {
        title: '加载完成设置',
        contentID: 'afterLoad',
        url: 'afterLoad.php',
        desc: '加载完成设置'
    }
}

let menuElem = ['live', 'historyGraph', 'historyTable', 'download', 'setting', 'account', 'about']
let layoutElem = ['about', 'account', 'footingInfo', 'live', 'historyTable', 'historyGraph', 'download', 'setting', 'afterLoad']
// let elemAuth = ['about', 'account', 'footingInfo', 'live', 'historyTable', 'historyGraph', 'download', 'setting', 'afterLoad']

function eAuth(elemName) {
    return elemAuth.indexOf(elemName) >= 0
}

let menuElemAuth = []
for (let i = 0, len = menuElem.length; i < len; i++) {
    let elem = menuElem[i]
    if (eAuth(elem)) {
        menuElemAuth.push({
            title: elemInfo[elem]['title'],
            contentID: elemInfo[elem]['contentID'],
            iconType: elemInfo[elem]['iconType']
        })
    }
}

let layoutElemAuth = []
for (let i = 0, len = layoutElem.length; i < len; i++) {
    let elem = layoutElem[i]
    if (eAuth(elem)) {
        layoutElemAuth.push({
            url: elemInfo[elem]['url'],
            id: '#' + elemInfo[elem]['contentID']
        })
    }
}

function loadDivRef() {
    let divRefStack = layoutElemAuth.reverse()

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
