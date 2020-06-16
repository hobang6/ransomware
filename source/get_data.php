<?php
  $uid = $_GET['uid'];
  $key = $_GET['key'];
  $user_data = fopen("./db/db.txt", "a");  
  fwrite($user_data, $uid."/".$key."@"."\r\n");  
  fclose($user_data);
?>