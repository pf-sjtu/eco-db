<!DOCTYPE html>
<html lang="en" class="full">

<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width,height=device-height,inital-scale=1.0,maximum-scale=2.0,user-scalable=no" />
    <title>登录到SURFES</title>
    <link rel="shortcut icon" href="pic/icon2.64.ico" />
    <link rel="stylesheet" type="text/css" href="css/account.css" />
</head>

<body class="full">
    <script>
        function visitorLogin() {
            document.getElementById("user_name").value = "visitor";
            document.getElementById("password").value = "visitor";
            document.getElementById("formSubmit").click();
        }
    </script>
    <form class="loginForm uForm" name="loginForm" method="post" action="account/chkUser.php">
        <div class="title">
            <img class="icon" src="pic/icon2.dark.small.png" alt="" />
            <p>SURFES<span>上海城市森林生态站数据库管理系统</span></p>
        </div>
        <p class="uTitle">登录系统</p>
        <p class="t">
            <label class="tLabel" for="user_name">用户名：</label>
            <input class="tBox" type="text" name="user_name" id="user_name" autocomplete="nickname" pattern="[0-9a-zA-Z_]{3,50}" placeholder="3-50位数字、字母下划线" title="请输入3-50位数字、字母下划线" required>*
        </p>
        <p class="t">
            <label class="tLabel" for="password">密码：</label>
            <input class="tBox" type="password" name="password" id="password" autocomplete="password" pattern="[0-9a-zA-Z_]{6,50}" placeholder="6-50位数字、字母下划线" title="请输入6-50位数字、字母下划线" required>*
            <span class="showPwd" onmousedown="document.getElementById('password').type = 'text'" onmouseup="document.getElementById('password').type = 'password'" ontouchstart="document.getElementById('password').type = 'text'" ontouchend="document.getElementById('password').type = 'password'">👁</span>
        </p>
        <div class="formOption">
            <input type="submit" name="formSubmit" id="formSubmit" value="登录" title="登录到SURFES系统">
            <input type="reset" name="formReset" id="formReset" value="重置" title="充值登录信息">
        </div>
        <div class="formOption2">
            <a class="loginOption" onclick="visitorLogin()" href="#">访客登录</a>&nbsp;&nbsp;
            <a class="loginOption" href="account/register.php">注册新用户</a>&nbsp;&nbsp;
            <a class="loginOption" href="account/lostPassword.php">找回密码</a>
        </div>

    </form>
</body>

</html>