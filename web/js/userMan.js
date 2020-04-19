let userMan = new Vue({
    el: '#userMan',
    data: {
        UserInfoArr: [],
        colInfo: [
            {
                key: 'id',
                title: '编号'
            },
            {
                key: 'username',
                title: '昵称'
            },
            {
                key: 'password',
                title: '密码'
            },
            {
                key: 'truename',
                title: '真名'
            },
            {
                key: 'address',
                title: '地址'
            },
            {
                key: 'email',
                title: '邮箱'
            },
            {
                key: 'authority',
                title: '权限'
            }
        ]
    },
    computed: {},
    methods: {
        refreshUserInfoArr: function () {
            let xhr = new XMLHttpRequest()
            xhr.open('GET', '../account/userMan/getUserInfoArr.php', true)
            xhr.onload = function () {
                if (this.status == 200) {
                    userMan.UserInfoArr = JSON.parse(this.responseText)
                    if (userMan.UserInfoArr.length > 0) {
                        userMan.refreshHtml()
                    }
                }
            }
            xhr.send()
        },
        refreshHtml: function () {
            function hDelete(i) {
                return "<td><select name='delete" + i + "'><option value='0'>无操作</option><option value='1'>删除</option></select></td>"
            }

            let hHead = ''
            let hData = []
            let tmp
            for (let i = 0, len = this.colInfo.length; i < len; i++) {
                hHead += '<th class="' + this.colInfo[i]['key'] + '">' + this.colInfo[i]['title'] + '</th>'
                for (let j = 0, len2 = this.UserInfoArr.length; j < len2; j++) {
                    if (this.colInfo[i]['key'] == 'id') {
                        tmp =
                            '<td class="' +
                            this.colInfo[i]['key'] +
                            '">' +
                            this.UserInfoArr[j][this.colInfo[i]['key']] +
                            '<input type="hidden" name="' +
                            this.colInfo[i]['key'] +
                            j +
                            '" value="' +
                            this.UserInfoArr[j][this.colInfo[i]['key']] +
                            '" required>' +
                            '</td>'
                    } else if (this.colInfo[i]['key'] == 'authority') {
                        tmp =
                            '<td class="' +
                            this.colInfo[i]['key'] +
                            '"><select name="' +
                            this.colInfo[i]['key'] +
                            j +
                            '"><option value="0">冻结</option><option value="1">访客</option><option value="2">科研人员</option><option value="3">管理员</option></select></td>'
                    } else {
                        tmp = '<td class="' + this.colInfo[i]['key'] + '">' + this.UserInfoArr[j][this.colInfo[i]['key']] + '</td>'
                    }
                    if (i == 0) {
                        hData.push([tmp])
                    } else {
                        hData[j].push(tmp)
                    }
                }
            }
            hHead += '<th>删除</th>'

            for (let i = 0, len = hData.length; i < len; i++) {
                hData[i] = '<tr>' + hData[i].join('') + hDelete(i) + '</tr>'
            }
            hData = hData.join('')
            let h = '<tr>' + hHead + '</tr>' + hData
            document.getElementById('userManTable').innerHTML = h

            for (let i = 0, len = this.UserInfoArr.length; i < len; i++) {
                document.getElementsByName('authority' + i)[0].value = this.UserInfoArr[i]['authority']
            }
        }
    },
    watch: {},
    created: function () {
        this.refreshUserInfoArr()
    }
})
