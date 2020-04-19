<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width,height=device-height,inital-scale=1.0,maximum-scale=2.0,user-scalable=no" />
    <title>登录到SURFES</title>
    <link rel="shortcut icon" href="pic/icon2.64.ico" />
    <link rel="stylesheet" type="text/css" href="css/account.css" />
</head>

<body>
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
    <div class="uForm">
        <p><?php echo $name; ?>您好!您已经登录到SURFES系统，您可以：<br /></p>
        <div class="formOption2">
            <a class='loginOption' href='home.php'>进入系统</a>
            <a class='loginOption' href='account/logout.php'>注销</a>
        </div>
    </div>
</body>

</html>