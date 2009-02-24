<?php
defined( '_VALID_THINBLUE' ) or die( 'Direct Access to this location is not allowed.' );

$config=$sqlite->get_config();

$config['debug']=leer_datos('debug');
if($config['debug'] == '') {
    $config['debug']=0;
}
$config['timeout']=leer_datos('timeout');
$config['concurrent']=leer_datos('concurrent');
if($config['concurrent'] == '' || $config['concurrent'] == '0') {
    $config['concurrent']=4;
}


if ( $sqlite->save_config($config) ) {
    echo "<h2>Configuración guardada.</h2>";
    $host = strlen($_SERVER['HTTP_HOST'])?$_SERVER['HTTP_HOST']:$_SERVER['SERVER_NAME'];
    echo "<script type='text/javascript'>setTimeout(\"document.location.href='http://$host/index.php?op=config'\", 2000);</script>";
}
else {
    echo "<h2>Error guardando configuración.</h2>";
    echo $sqlite->get_error();
}


?>
