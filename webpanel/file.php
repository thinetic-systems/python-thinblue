<?php
defined( '_VALID_THINBLUE' ) or die( 'Direct Access to this location is not allowed.' );

$config=$sqlite->get_config();
?>
<h2>Configuración del equipo "<?php echo $_SERVER["SERVER_NAME"]; ?>"</h2>


<style type="text/css">
div.organize {
    background-color:#AAAAAA;
    margin-left:auto;
    margin-right:auto;
    text-align:center;
    width:50%;
}
</style>

Archivo actual:
<pre><?php echo $config['sendfile']; ?></pre>
<?php
    $img_path=$config['file_path'] . $config['sendfile'];
    echo "<a href='http://".$_SERVER["SERVER_NAME"]."/index.php?op=get_image&force=download&rand=".rand()."'>Descargar (".$config['sendfile'].")</a>";
    echo "<br/>";
    if (is_image($img_path) ) {
        echo "<img src='http://".$_SERVER["SERVER_NAME"]."/index.php?op=get_image&rand=".rand()."'>";
    }
?>
<br/><br/>

<center>
    <form enctype="multipart/form-data" action="index.php" method="post">
        <input type="hidden" name="MAX_FILE_SIZE" value="1000000">
        <input type="hidden" name="op" value="filesave">
        Archivo: <input name="userfile" type="file">
        <input type="submit" value="Cambiar">
        <br/>
        <input type="checkbox" name="sendagain" id="sendagain" value=1> Enviar a todos los teléfonos de nuevo
    </form>
</center>

