<?php
defined( '_VALID_THINBLUE' ) or die( 'Direct Access to this location is not allowed.' );

$refresh=leer_datos("refresh");
if ($refresh == "") {
    $refresh=0;
}

if (leer_datos("action") == "") {

$phones=$sqlite->get_all_phones();

?>
<h2>Accesos del equipo "<?php echo $_SERVER["SERVER_NAME"]; ?>"</h2>


<table class='data'>
<?php
echo "<tr style='color:#FFF; background-color:#486591'>";
    echo "<td>MAC</td>";
    echo "<td>Estado</td>";
    echo "<td>Fecha encontrado</td>";
    echo "<td>Fecha enviado</td>";
echo "</tr>";

for ($i=0; $i<sizeof($phones); $i++) {
    echo "<tr style='background-color:#C9C9C9; color:#000;'>";
        echo "<td>".$phones[$i]['address']."</td>";
        echo "<td>".$phones[$i]['status']."</td>";
        echo "<td>".$phones[$i]['date_search']."</td>";
        echo "<td>".$phones[$i]['date_send']."</td>";
    echo "</tr>";
}
?>
</table>
<br/><br/>

<div class='white center'>
<br/>
<a class='white' href="index.php?op=phones&action=clean&refresh=<? echo $refresh;?>">Borrar todos (se vuelve a buscar/enviar)</a>  | 
<a class='white' href="index.php?op=phones&action=pending&refresh=<? echo $refresh;?>">Reenviar a todos (pone a seen1)</a> |
<?php
if ( $refresh == 0 ) {
    echo "<a class='white' href='index.php?op=phones&refresh=3'>Recargar cada 3 seg</a>";
    }
else {
    echo "<a class='white' href='index.php?op=phones&refresh=0'>Parar autorecarga</a>";
}
?>
<br/><br/>
</div>

<?
    if ($refresh > 0 ) {
        $refresh_time=$refresh * 1000;
        $host = strlen($_SERVER['HTTP_HOST'])?$_SERVER['HTTP_HOST']:$_SERVER['SERVER_NAME'];
        echo "<script type='text/javascript'>setTimeout(\"document.location.href='http://$host/index.php?op=phones&refresh=$refresh'\", $refresh_time);</script>";
    }
} /*fin de leer_datos("action") */



elseif ( leer_datos("action") == "clean") {
    $sqlite->clean();
    echo "<h3>Limpiando...</h3>";
    $host = strlen($_SERVER['HTTP_HOST'])?$_SERVER['HTTP_HOST']:$_SERVER['SERVER_NAME'];
    echo "<script type='text/javascript'>document.location.href='http://$host/index.php?op=phones&refresh=$refresh';</script>";
}



elseif ( leer_datos("action") == "pending") {
    $sqlite->set_pending();
    echo "<h3>Configurando todos como pendientes...</h3>";
    $host = strlen($_SERVER['HTTP_HOST'])?$_SERVER['HTTP_HOST']:$_SERVER['SERVER_NAME'];
    echo "<script type='text/javascript'>document.location.href='http://$host/index.php?op=phones&refresh=$refresh';</script>";
}

?>
