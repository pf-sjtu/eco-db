<!DOCTYPE html>
<html lang="en" class="full">

<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width,height=device-height,inital-scale=1.0,maximum-scale=2.0,user-scalable=no" />
    <title>找回密码</title>
    <link rel="shortcut icon" href="../pic/icon2.64.ico" />
    <link rel="stylesheet" type="text/css" href="../css/account.css" />
</head>

<body class="full">
    <form class="loginForm uForm" name="findPwdForm" method="post" action="showQuestion.php">
        <div class="title">
            <img class="icon" src="../pic/icon2.dark.small.png" alt="" />
            <p>SURFES<span>上海城市森林生态站数据库管理系统</span></p>
        </div>
        <p class="uTitle">密码查询</p>
        <p class="t">
            <label class="tLabel" for="user_name">用户名：</label>
            <input class="tBox" type="text" name="user_name" id="user_name" autocomplete="nickname" pattern="[0-9a-zA-Z_]{3,50}" placeholder="3-50位数字、字母下划线" title="您需要找回的账号的用户名（昵称），请输入3-50位数字、字母下划线" required>*
        </p>
        <div class="formOption">
            <input type="submit" name="formSubmit" id="formSubmit" value="提交">
            <input type="reset" name="formReset" id="formReset" value="重置">
            <input type="button" name="login" id="login" onclick="history.back()" value="返回">
        </div>
    </form>
</body>

</html>