let cip = [0, 0, 0, 0]
let clocation = ''
if (typeof returnCitySN != 'undefined') {
    cip = returnCitySN['cip'].split('.')
    clocation = returnCitySN['cname']
}
let cdt = new Date().Format('yyyy-MM-ddThh:mm:ss')
let xhr = new XMLHttpRequest()
xhr.open('GET', 'php/qGETip.php?datetime=' + cdt + '&ip0=' + cip[0] + '&ip1=' + cip[1] + '&ip2=' + cip[2] + '&ip3=' + cip[3] + '&location=' + clocation, true)
xhr.onload = function() {}
xhr.send()
