<script>
    let elemAuth = [];
</script>

<?php
require_once('account/conn.php');

$ID = $_SESSION['id'];
$sql = mysqli_query($conn, "SELECT * FROM `member` WHERE id=$ID");
$info = mysqli_fetch_array($sql);
$_SESSION['auth'] = $info['authority'];

$auth = $_SESSION['auth'];
echo "<script> console.log('authLevel', $auth)</script>";

$sql = mysqli_query($conn, "SELECT `contentID` FROM `auth` WHERE authLevel<=$auth");
$authArr = mysqli_fetch_all($sql, MYSQLI_ASSOC);

foreach ($authArr as $authElem) {
    $authElem = $authElem['contentID'];
    echo "<script> elemAuth.push('$authElem'); </script>";
}
