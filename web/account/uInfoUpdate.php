<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width,height=device-height,inital-scale=1.0,maximum-scale=2.0,user-scalable=no" />
    <title>修改用户资料</title>
    <link rel="shortcut icon" href="../pic/icon2.64.ico" />
    <link rel="stylesheet" type="text/css" href="../css/account.css" />
    <?php
    session_start();
    $ID = $_SESSION['id'];
    $username = $_SESSION['username'];
    if ($username == "visitor") {
        echo "<script>alert('用户\"$username\"无此权限。');history.back();</script>";
        exit;
    }

    require_once('conn.php');
    $sql = mysqli_query($conn, "SELECT * FROM `member` WHERE id='$ID'");
    $info = mysqli_fetch_array($sql);
    ?>
    <script type="text/javascript">
        function formSelectQuestion(question_id) {
            document.getElementById("question").value = question_id
        }

        function formResetSelectQuestion(event, question_id) {
            event.preventDefault()
            document.getElementById("updateForm").reset()
            formSelectQuestion(question_id)
        }
    </script>
</head>

<body>
    <form class="regForm uForm" id="updateForm" name="updateForm" method="post" action="uInfoUpdateResult.php">
        <div class="title">
            <img class="icon" src="../pic/icon2.dark.small.png" alt="" />
            <p>SURFES<span>上海城市森林生态站数据库管理系统</span></p>
        </div>
        <p class="uTitle">更新用户信息</p>
        <p class="t">
            <label class="tLabel" for="user_name">用户名：</label>
            <input class="tBox" type="text" name="user_name" id="user_name" autocomplete="nickname" pattern="[0-9a-zA-Z_]{3,50}" placeholder="3-50位数字、字母下划线" title="请输入3-50位数字、字母下划线" required value="<?php echo $info['username']; ?>">*
        </p>
        <p class="t">
            <label class="tLabel" for="password">密码：</label>
            <input class="tBox" type="password" name="password" id="password" autocomplete="password" pattern="[0-9a-zA-Z_]{6,50}" placeholder="6-50位数字、字母下划线" title="请输入6-50位数字、字母下划线" required>*
            <span class="showPwd" onmousedown="document.getElementById('password').type = 'text'" onmouseup="document.getElementById('password').type = 'password'" ontouchstart="document.getElementById('password').type = 'text'" ontouchend="document.getElementById('password').type = 'password'">👁</span>
        </p>
        <p class="t">
            <label class="tLabel" for="password1">确认密码：</label>
            <input class="tBox" type="password" name="password1" id="password1" pattern="[0-9a-zA-Z]{6,50}" placeholder="请再次输入密码" title="再次输入密码" required>*
            <span class="showPwd" onmousedown="document.getElementById('password1').type = 'text'" onmouseup="document.getElementById('password1').type = 'password'" ontouchstart="document.getElementById('password1').type = 'text'" ontouchend="document.getElementById('password1').type = 'password'">👁</span>
        </p>
        <p class="t">
            <label class="tLabel" for="email">电子邮箱：</label>
            <input class="tBox" type="email" name="email" id="email" autocomplete="email" title="请输入您的常用电子邮箱地址，便于您的密码找回和管理员联系您" required value="<?php echo $info['email']; ?>">*
        </p>
        <p class="t">
            <label class="tLabel" for="true_name">真实姓名：</label>
            <input class="tBox" type="text" name="true_name" id="true_name" autocomplete="name" title="请输入您的真实姓名，便于管理员联系您和权限审核" required value="<?php echo $info['truename']; ?>">*
        </p>
        <p class="t">
            <label class="tLabel" for="address">单位和地址：</label>
            <input class="tBox" type="text" name="address" id="address" autocomplete="organization" title="请输入您的单位和（或）地址，便于管理员联系您和权限审核" required value="<?php echo $info['address']; ?>">*
        </p>
        <p class="t">
            <label class="tLabel" for="question">密码提示问题：</label>
            <?php require_once('echoQueOptions.php'); ?>
            <script type="text/javascript">
                formSelectQuestion(<?php echo $info['question_id']; ?>)
            </script>
        </p>
        <p class="t">
            <label class="tLabel" for="answer">密码提示答案：</label>
            <input class="tBox" type="text" name="answer" id="answer" title="请输入上述问题的答案，便于您的密码找回" value="<?php echo $info['answer']; ?>">
        </p>
        <div class="formOption">
            <input type="submit" name="formSubmit" id="formSubmit" value="更新信息" title="提交您的信息并且完成信息更新">
            <input type="reset" name="formReset" id="formReset" value="重写" title="重写表单" onclick="formResetSelectQuestion(event,<?php echo $info['question_id']; ?>)">
            <input type="button" name="formReturn" id="formReturn" value="返回" title="取消信息修改并返回" onclick="history.back()">
        </div>
    </form>
</body>

</html>