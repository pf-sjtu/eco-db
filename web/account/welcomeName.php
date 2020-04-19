<?php
function wName($username)
{
    if ($username == 'visitor') {
        return '访客';
    } elseif ($username == 'admin') {
        return '管理员';
    } else return $username;
}
