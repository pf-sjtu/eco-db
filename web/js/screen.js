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

 
if(isPC()){
    document.getElementById("container").className = "pc";
}
else{
    document.getElementById("container").className = "phone";
}

document.getElementById("settingBox").hidden = false;
document.getElementById("resultBox").hidden = false;
document.getElementById("dataTab").hidden = false;
document.getElementById("footing").hidden = false;
document.getElementById("loading").hidden = true;

// https://blog.csdn.net/liyede2008/article/details/78213054