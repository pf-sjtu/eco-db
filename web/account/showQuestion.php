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
    <form class="loginForm uForm" name="findPwdInfoForm" method="post" action="showPwd.php">
        <div class="title">
            <img class="icon" src="../pic/icon2.dark.small.png" alt="" />
            <p>SURFES<span>上海城市森林生态站数据库管理系统</span></p>
        </div>
        <p class="uTitle">补充信息</p>
        <p class="tLine">
            <span>用户名：</span>
            <?php
            require_once('conn.php');
            $user_name = mysqli_escape_string($conn, $_POST['user_name']);
            echo $user_name;
            ?>
            <input type="hidden" name="user_name" id="user_name" value="<?php echo $user_name; ?>">
        </p>
        <p class="tLine">
            <span>问题提示：</span>
            <?php
            $sql = mysqli_query($conn, "SELECT `question_id` FROM `member` WHERE `username`='$user_name'");
            $que_id = mysqli_fetch_row($sql);
            if ($que_id == false) {
                echo "<script>alert('无此用户。');history.back();</script>;";
                exit;
            } else {
                $sql = mysqli_query($conn, "SELECT `question` FROM `question` WHERE `id`='$que_id[0]'");
                $question = mysqli_fetch_row($sql)[0];
                echo $question;
            }
            ?>
        </p>
        <p class="t">
            <label class="tLabel" for="answer">问题答案：</label>
            <input class="tBox" type="text" name="answer" id="answer" title="请输入上述问题的答案">
        </p>
        <p class="t">
            <label class="tLabel" for="email">电子邮箱：</label>
            <input class="tBox" type="email" name="email" id="email" autocomplete="email" title="请输入账号信息中的电子邮箱地址" required>*
        </p>
        <div class="formOption">
            <input type="submit" name="formSubmit" id="formSubmit" value="提交" title="提交您的信息并且查询密码">
            <input type="reset" name="formReset" id="formReset" value="重写" title="重写表单">
            <input type="button" name="login" id="login" onclick="history.back()" value="返回">
        </div>
    </form>
</body>

</html>