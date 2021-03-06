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
    <?php
    session_start();
    if (isset($_SESSION['username']) && $_SESSION['username'] == 'visitor') {
        echo "<script>console.log('session_destroy')</script>";
        session_destroy();
        header("location:login.php");
        exit;
    }
    if (!isset($_SESSION['username'])) {
        header("location:login.php");
        exit;
    }
    $username = $_SESSION['username'];
    require_once('account/welcomeName.php');
    $name = wName($username);
    ?>
    <div class="loginForm uForm">
        <div class="title">
            <img class="icon" src="pic/icon2.dark.small.png" alt="" />
            <p>SURFES<span>上海城市森林生态站数据库管理系统</span></p>
        </div>
        <p class="name"><?php echo $name; ?>，</p>
        <p class="tips">您好！您已经登录到SURFES系统，接下来可以：<br /></p>
        <div class="formOption2">
            <a class='loginOption' href='home.php'>进入系统</a>
            <a class='loginOption' href='account/logout.php'>注销</a>
        </div>
    </div>
</body>

</html>