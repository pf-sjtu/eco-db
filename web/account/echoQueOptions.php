<?php
require_once('conn.php');
$sql = mysqli_query($conn, "SELECT `question` FROM `question`");
$questions = mysqli_fetch_all($sql);
$que_html = "";
$opt_val = 0;
foreach ($questions as $question) {
    $opt_val++;
    $que_html .= "<option value='$opt_val'>" . $question[0] . "</option>";
}
$que_html = "<select class='tBox' name='question' id='question' value=''>$que_html</select>";
echo $que_html;
