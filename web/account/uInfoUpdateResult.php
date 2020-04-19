<!DOCTYPE html>
<html lang="en" class="full">

<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width,height=device-height,inital-scale=1.0,maximum-scale=2.0,user-scalable=no" />
    <title>账号信息修改结果</title>
    <link rel="shortcut icon" href="../pic/icon2.64.ico" />
    <link rel="stylesheet" type="text/css" href="../css/account.css" />
</head>

<body class="full">
    <?php
    session_start();
    $ID = $_SESSION['id'];

    function strLenFlag($str)
    {
        return strlen($str) > 0 && strlen($str) <= 50;
    }
    $fmt_flag = true;
    require_once('conn.php');
    $sql = mysqli_query($conn, "SELECT * FROM `member` WHERE id='$ID'");
    $info = mysqli_fetch_array($sql);

    $user_name = mysqli_escape_string($conn, $_POST['user_name']);
    $fmt_flag &= preg_match('/[0-9a-zA-Z_]{3,50}/', $user_name);
    echo "<script>console.log('user_name','$fmt_flag');</script>";

    $email = strtolower(mysqli_escape_string($conn, $_POST['email']));
    $fmt_flag &= strLenFlag($email) && preg_match('/[0-9a-z_\.]+@[0-9a-z_\.]+/', $email);
    echo "<script>console.log('email','$fmt_flag');</script>";

    $sql = mysqli_query($conn, "SELECT COUNT(*) FROM `member` WHERE `username`='$user_name'");
    $name_aval = mysqli_fetch_row($sql)[0];
    $sql = mysqli_query($conn, "SELECT COUNT(*) FROM `member` WHERE `email`='$email'");
    $email_aval = mysqli_fetch_row($sql)[0];
    if ($info['username'] != $user_name && $name_aval > 0) {
        echo "<script>alert('对不起，该用户名已经被占用了。');history.back();</script>";
        exit;
    } elseif ($info['email'] != $email && $email_aval > 0) {
        echo "<script>alert('对不起，该电子邮箱地址已经被占用了。');history.back();</script>";
        exit;
    } else {
        $password = mysqli_escape_string($conn, $_POST['password1']);
        $fmt_flag &= preg_match('/[0-9a-zA-Z_]{6,50}/', $password);
        echo "<script>console.log('password','$fmt_flag');</script>";

        $true_name = mysqli_escape_string($conn, $_POST['true_name']);
        $fmt_flag &= strLenFlag($true_name);
        echo "<script>console.log('true_name','$fmt_flag');</script>";

        $address = mysqli_escape_string($conn, $_POST['address']);
        $fmt_flag &= strLenFlag($address);
        echo "<script>console.log('address','$fmt_flag');</script>";

        $question = $_POST['question'];
        $sql = mysqli_query($conn, "SELECT COUNT(*) FROM `question`");
        $question_num = mysqli_fetch_row($sql)[0];
        $fmt_flag &= preg_match('/[0-9]+/', $question) && $question > 0 && $question <= $question_num;
        echo "<script>console.log('question', '$fmt_flag');</script>";

        $answer = mysqli_escape_string($conn, $_POST['answer']);
        $fmt_flag &= strlen($answer) <= 50;
        echo "<script>console.log('answer','$fmt_flag');</script>";

        if (!$fmt_flag) {
            echo "<script>alert('参数错误。');history.back();</script>";
            exit;
        }

        mysqli_query($conn, "UPDATE `member` SET `username`='$user_name',`password`='$password',`question_id`=$question,`answer`='$answer',`truename`='$true_name',`address`='$address',`email`='$email' WHERE `id`='$ID'");
    }
    ?>
    <div class="loginForm uForm">
        <div class="title">
            <img class="icon" src="../pic/icon2.dark.small.png" alt="" />
            <p>SURFES<span>上海城市森林生态站数据库系统</span></p>
        </div>
        <p class="uTitle">账号信息修改成功</p>
        <p class="center">恭喜您！您已成功修改账号信息。</p>
        <div class="formOption2">
            <a class='loginOption' href='logout.php'>注销账号</a>
            <a class='loginOption' href='../home.php'>返回SURFES</a>
        </div>
    </div>
</body>

</html>