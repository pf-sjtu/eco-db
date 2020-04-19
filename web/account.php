<?php
session_start();
$ID = $_SESSION['id'];
$auth = $_SESSION['auth'];
$username = $_SESSION['username'];
require_once('account/welcomeName.php');
$name = wName($username);
?>

<link rel="stylesheet" type="text/css" href="css/account.css" />

<div class="uInfo">
    <div class="uBox accountInfo">
        <div class="uIcon">
            <i class="ivu-icon ivu-icon-ios-person">
            </i>
        </div>
        <div class="uOption">
            <p class="wTitle"><span class="name"><?php echo $name; ?></span>您好!<br /></p>
            <div class="formOption3">
                <?php
                if ($username != "visitor")
                    echo '<a class="loginOption" href="account/uInfoUpdate.php">修改资料</a>';
                ?>
                <a class='loginOption' href='account/logout.php'>注销</a>
            </div>
        </div>
        <div class="clearFloat"></div>
    </div>

    <div class="uBox accountAuth">
        <p class="title">当前权限</p>
        <div class="auth">
            <table>
                <tbody>
                    <tr id="authHeadRow"></tr>
                    <tr id="authFlagRow"></tr>
                    <tr id="authDescRow"></tr>
                </tbody>
            </table>
        </div>
        <div class="tips">
            <div class="tw">提示：</div>
            <div class="tc" <?php echo ($auth < 2 && $username == "visitor") ? "" : "hidden"; ?>>
                <p>若需获得所有权限，请注销访客身份并且注册账号，等待管理员审核。</p>
            </div>
            <div class="tc" <?php echo ($auth < 2 && $username != "visitor") ? "" : "hidden"; ?>>
                <p>若需获得所有权限，请联系管理员。</p>
                <p><a target="_blank" href="mailto:<?php require_once('account\echoAdminEmail.php'); ?>"><?php echo $adminEmail; ?></a></p>
            </div>
            <div class="tc" <?php echo ($auth == 2) ? "" : "hidden"; ?>>
                <p>您已获得所有模块的查看权限。</p>
            </div>
            <div class="tc" <?php echo ($auth > 2) ? "" : "hidden"; ?>>
                <p>您是系统管理员，可以对用户账户进行操作。</p>
            </div>
            <div class="clearFloat"></div>
        </div>
        <div class="clearFloat"></div>
    </div>

    <div class="uBox" <?php echo ($auth > 2) ? "" : "hidden"; ?>>
        <p class="title">用户管理</p>
        <form class="userManForm" name="userManForm" method="post" action="account/userMan/postUserInfoArr.php">
            <div id="userMan">
                <table>
                    <tbody id="userManTable"></tbody>
                </table>
                <div class="formOption">
                    <input type="reset" name="formReset" id="formReset" value="复原" title="复原用户信息">
                    <input type="submit" name="formSubmit" id="formSubmit" value="提交" title="提交用户信息修改">
                </div>
            </div>
        </form>
        <script type='text/javascript' src='js/userMan.js'></script>
    </div>
</div>

<script type="text/javascript" src="js/auth.js"></script>