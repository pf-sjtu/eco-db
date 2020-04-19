function chkinput(form) {
    if (form.user_name.value == '') {
        form.user_name.style.backgroundColor = 'red'
        document.getElementById('error_note').innerText = '提示：请输入昵称。'
        form.user_name.select()
        return false
    }

    if (form.password.value == '') {
        form.password.style.backgroundColor = 'red'
        document.getElementById('error_note').innerText = '提示：请输入密码。'
        form.password.select()
        return false
    }
    if (form.password1.value == '') {
        form.password1.style.backgroundColor = 'red'
        document.getElementById('error_note').innerText = '提示：请输入确认密码。'
        form.password1.select()
        return false
    }
    if (form.password.value.length < 3) {
        form.password.style.backgroundColor = 'red'
        document.getElementById('error_note').innerText = '提示：密码长度应该大于3位。'
        form.password.select()
        return false
    }
    if (form.password.value != form.password1.value) {
        form.password1.style.backgroundColor = 'red'
        document.getElementById('error_note').innerText = '提示：密码与重复密码不一致。'
        form.password.select()
        return false
    }
    if (form.email.value == '') {
        form.email.style.backgroundColor = 'red'
        document.getElementById('error_note').innerText = '提示：请填写电子邮箱地址。'
        form.email.select()
        return false
    }
    if (form.email.value.indexOf('@') < 0) {
        form.email.style.backgroundColor = 'red'
        document.getElementById('error_note').innerText = '提示：请输入正确的电子邮箱地址。'
        form.email.select()
        return false
    }
    if (form.address.value == '') {
        form.address.style.backgroundColor = 'red'
        document.getElementById('error_note').innerText = '提示：请输入单位和地址。'
        form.address.select()
        return false
    }
    if (form.true_name.value == '') {
        form.true_name.style.backgroundColor = 'red'
        document.getElementById('error_note').innerText = '提示：请输入真实姓名。'
        form.true_name.select()
        return false
    }
    if (form.answer.value == '') {
        form.answer.style.backgroundColor = 'red'
        document.getElementById('error_note').innerText = '提示：请输入密码提示答案。'
        form.answer.select()
        return false
    }
    document.getElementById('error_note').innerHTML = '&nbsp;'
    return true
}
