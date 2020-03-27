// yyyy-MM-ddThh:mm:ss
Date.prototype.Format = function(fmt) {
    //author: meizz
    let o = {
        'M+': this.getMonth() + 1, //月份
        'd+': this.getDate(), //日
        'h+': this.getHours(), //小时
        'm+': this.getMinutes(), //分
        's+': this.getSeconds(), //秒
        'q+': Math.floor((this.getMonth() + 3) / 3), //季度
        S: this.getMilliseconds() //毫秒
    }
    if (/(y+)/.test(fmt)) fmt = fmt.replace(RegExp.$1, (this.getFullYear() + '').substr(4 - RegExp.$1.length))
    for (let k in o) {
        if (new RegExp('(' + k + ')').test(fmt)) fmt = fmt.replace(RegExp.$1, RegExp.$1.length == 1 ? o[k] : ('00' + o[k]).substr(('' + o[k]).length))
    }
    return fmt
}
Date.prototype.add = function(d = 0, h = 0, m = 0, s = 0, ms = 0) {
    let ts = Date.parse(this) + ms + 1000 * s + 1000 * 60 * m + 1000 * 60 * 60 * h + 1000 * 60 * 60 * 24 * d
    let dt = new Date()
    dt.setTime(ts)
    return dt
}

function rDigit(digit) {
    return Math.ceil(Math.random() * 10 ** digit)
}

// @param name { String } 需要返回的属性名
// @param arr { Array } 原始数据
// @return ret { Array } 返回值
function getParamValues(name, arr) {
    let ret = []
    for (let i = 0, len = arr.length; i < len; i++) {
        ret.push(arr[i][name])
    }
    return ret
}

// @param name { String } 需要添加的属性名
// @param value { any } 需要添加的属性值
// @param arr { Array } 原始数据
function createParamValues(name, value, arr) {
    if (value.length == arr.length) {
        for (let i = 0, len = arr.length; i < len; i++) {
            arr[i][name] = value[i]
        }
    } else {
        for (let i = 0, len = arr.length; i < len; i++) {
            arr[i][name] = value
        }
    }
    return arr
}

function qGET(q = 'SELECT * FROM station_info', dtype = '') {
    let xhr = new XMLHttpRequest()
    xhr.open('GET', '../php/qGET.php?q=' + q + '&dtype=' + dtype, true)
    xhr.onload = function() {
        if (this.status == 200) {
            let result = JSON.parse(this.responseText)
            console.log(result)
        }
    }
    xhr.send()
}

function simpleDeepCopy(obj) {
    return JSON.parse(JSON.stringify(obj))
}
Array.prototype.simpleDeepCopy = function() {
    return JSON.parse(JSON.stringify(this))
}

function powerSet(arr) {
    let ps = [[]]
    for (let i = 0, indexMax = arr.length; i < indexMax; i++) {
        for (let j = 0, len = ps.length; j < len; j++) {
            ps.push(ps[j].concat(arr[i]))
        }
    }
    return ps
}

Array.prototype.swap = function(digit1, digit2) {
    let tmp = this[digit1]
    this[digit1] = this[digit2]
    this[digit2] = tmp
}

// 全排列
function needSwap(arr, beg, end) {
    for (let i = beg; i < end; i++) {
        if (arr[i] == arr[end]) {
            return false
        }
    }
    return true
}
function perm(arr) {
    let p = []
    if (arr.length > 1) {
        for (let i = 0, numNum = arr.length; i < numNum; i++) {
            if (needSwap(arr, 0, i)) {
                arr.swap(0, i)
                permStep(arr, 1, p)
                arr.swap(0, i)
            }
        }
    } else {
        p.push(arr.simpleDeepCopy())
    }
    return p
}
function permStep(arr, beg, resultArr) {
    if (beg == arr.length - 1) {
        resultArr.push(arr.simpleDeepCopy())
    } else {
        for (let i = beg, numNum = arr.length; i < numNum; i++) {
            if (needSwap(arr, beg, i)) {
                arr.swap(beg, i)
                permStep(arr, beg + 1, resultArr)
                arr.swap(beg, i)
            }
        }
    }
}

function deepEquel(obj1, obj2) {
    return JSON.stringify(obj1) == JSON.stringify(obj2)
}

Array.prototype.dropDuplicate = function(sortby) {
    let sortedArr = this.simpleDeepCopy()
    if (typeof sortby == 'function') {
        sortedArr.sort(sortby)
    } else {
        sortedArr.sort()
    }
    for (let i = 1, len = sortedArr.length; i < len; i++) {
        if (deepEquel(sortedArr[i - 1], sortedArr[i])) {
            i--
            len--
            sortedArr.splice(i, 1)
        }
    }
    return sortedArr
}

function nDimOption(dim, optionArray) {
    let optionArrayLength = optionArray.length
    let stepMax = optionArrayLength ** dim
    let result = []
    for (let step = 0; step < stepMax; step++) {
        let digitPos = []
        for (let digit = 0; digit < dim; digit++) {
            digitPos[digit] = step
            for (let numDivision = 0; numDivision < digit; numDivision++) {
                digitPos[digit] = Math.floor(digitPos[digit] / optionArrayLength)
            }
            digitPos[digit] %= optionArrayLength
            digitPos[digit] = optionArray[digitPos[digit]]
        }
        result.push(digitPos.simpleDeepCopy())
    }
    return result
}

function genCmpFunc(key) {
    comKey = function(a, b) {
        let x = a[key]
        let y = b[key]
        if (x < y) {
            return -1
        }
        if (x > y) {
            return 1
        }
        return 0
    }
    return comKey
}

function downFile(content, filename) {
    // 创建隐藏的可下载链接
    let eleLink = document.createElement('a')
    eleLink.download = filename
    eleLink.style.display = 'none'
    // 字符内容转变成blob地址
    let blob = new Blob([content])
    eleLink.href = URL.createObjectURL(blob)
    // 触发点击
    document.body.appendChild(eleLink)
    eleLink.click()
    // 然后移除
    document.body.removeChild(eleLink)
}

// function isPC() {
//     let userAgentInfo = navigator.userAgent;
//     let Agents = ["Android", "iPhone", "SymbianOS", "Windows Phone", "iPod"];
//     let flag = true;
//     for (let v = 0; v < Agents.length; v++) {
//         if (userAgentInfo.indexOf(Agents[v]) > 0) {
//             flag = false;
//             break;
//         }
//     }
//     if (window.screen.width >= 768) {
//         flag = true;
//     }
//     return flag;
// }
function isPC() {
    let flag = false
    if (document.body.clientWidth >= 768) {
        flag = true
    }
    return flag
}

function geoCoordConvert(geoArray) {
    let arr,
        tmp,
        fixedDigits = 2
    if (typeof geoArray != 'object') {
        arr = [geoArray]
    } else {
        arr = simpleDeepCopy(geoArray)
    }
    for (let i = 0, len = arr.length; i < len; i++) {
        if (typeof arr[i] == 'string' && arr[i].indexOf('°') > 0) {
            tmp = arr[i]
                .replace(/′/g, '°')
                .replace(/″/g, '')
                .split('°')
            arr[i] = parseFloat(tmp[0])
            for (let j = 1, len2 = tmp.length; j < len2; j++) {
                arr[i] += parseFloat(tmp[j]) / 60 ** j
            }
        } else {
            if (typeof arr[i] == 'string') {
                arr[i] = parseFloat(arr[i])
            }
            tmp = arr[i] >= 0 ? '' : '-'
            arr[i] = Math.abs(arr[i])
            tmp += Math.floor(arr[i]) + '°'

            arr[i] = (arr[i] - Math.floor(arr[i])) * 60
            tmp += Math.floor(arr[i]) + '′'

            arr[i] = (arr[i] - Math.floor(arr[i])) * 60
            tmp += arr[i].toFixed(fixedDigits) + '″'

            arr[i] = tmp
        }
    }
    return arr
}

let GB2312UnicodeConverter = {
    ToUnicode: function(str) {
        return escape(str)
            .toLocaleLowerCase()
            .replace(/%u/gi, '\\u')
    },
    ToGB2312: function(str) {
        return unescape(str.replace(/\\u/gi, '%u'))
    }
}
