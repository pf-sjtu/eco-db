document.getElementById('loadingProgressBar').value += 1
if (document.getElementById('loadingProgressBar').value >= document.getElementById('loadingProgressBar').max) {
    document.getElementById('loadingProgress').hidden = true
    document.getElementById('container').hidden = false
    document.getElementById('topNav').hidden = false
}
