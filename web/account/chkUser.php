<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width,height=device-height,inital-scale=1.0,maximum-scale=2.0,user-scalable=no" />
    <title>登录到SURFES</title>
    <link rel="shortcut icon" href="../pic/icon2.64.ico" />
    <link rel="stylesheet" type="text/css" href="../css/account.css" />
</head>

<body>
    <?php
    $user_name = $_POST['user_name'];
    $password = $_POST['password'];

    class chkinput
    {
        var $m_username;
        var $m_password;
        function __construct($name, $pwd)
        {
            $this->m_username = $name;
            $this->m_password = $pwd;
        }

        function checkinput()
        {
            require_once('conn.php');
            $sql = mysqli_query($conn, "SELECT * FROM `member` WHERE username='$this->m_username'");
            $info = mysqli_fetch_array($sql);
            if ($info == false) {
                echo "<script>alert('用户不存在!');history.back();</script>";
                exit;
            } else {
                if ($info['authority'] == 0) {
                    echo "<script>alert('该用户已被冻结!');history.back();</script>";
                    exit;
                }
                if ($info['password'] == $this->m_password) {
                    session_start();
                    $_SESSION['username'] = $info['username'];
                    $_SESSION['id'] = $info['id'];
                    $_SESSION['auth'] = $info['authority'];
                    echo "<script>alert('登陆成功');</script>";
                    header("location:../home.php");
                    exit;
                } else {
                    echo "<script>alert('密码输入错误!');setTimeout(history.back(),1000);</script>";
                    exit;
                }
            }
        }
    }

    $obj = new chkinput($user_name, $password);
    $obj->checkinput();
    ?>
</body>

</html>