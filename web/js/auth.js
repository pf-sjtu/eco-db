for (let i = 0, len = menuElem.length, elem = document.getElementById('authHeadRow'); i < len; i++) {
    elem.innerHTML += '<th>' + elemInfo[menuElem[i]]['title'] + '</th>'
}
for (let i = 0, len = menuElem.length, elem = document.getElementById('authFlagRow'); i < len; i++) {
    let data = elemAuth.indexOf(menuElem[i]) >= 0 ? '√' : '×'
    elem.innerHTML += '<td>' + data + '</td>'
}
for (let i = 0, len = menuElem.length, elem = document.getElementById('authDescRow'); i < len; i++) {
    elem.innerHTML += '<td>' + elemInfo[menuElem[i]]['desc'] + '</td>'
}
