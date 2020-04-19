function loadingForward() {
    document.getElementById('loadingProgressBar').value += 1
    if (document.getElementById('loadingProgressBar').value >= document.getElementById('loadingProgressBar').max) {
        let loadingProgress = document.getElementById('loadingProgress')
        loadingProgress.className += 'loadingProgressFade'
        loadingProgress.addEventListener('animationend', function () {
            loadingProgress.hidden = true
        })
    }
}
