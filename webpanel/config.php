<?php
defined( '_VALID_THINBLUE' ) or die( 'Direct Access to this location is not allowed.' );

$config=$sqlite->get_config();
?>
<h2>Configuración del equipo "<?php echo $_SERVER["SERVER_NAME"]; ?>"</h2>



<form method="post" action="index.php">
<table>
    <tr>
        <td>Debug: </td>
        <td>
            <input type="checkbox" name="debug" id="debug" value=1 <?php if ($config['debug'] > 0) {echo "checked";} ?> >
        </td>
    </tr>
    <tr>
        <td>Timeout búsqueda nuevos: </td>
        <td>
            <input type="text" name="timeout" id="timeout" size='3' value="<?php if ($config['timeout'] > 0) {echo $config['timeout'];} ?>" > (seg), recomendado 8.
        </td>
    </tr>
    
    <tr>
        <td>Conexiones de envío concurrentes: </td>
        <td>
            <input type="text" name="concurrent" id="concurrent" size='3' value="<?php if ($config['concurrent'] > 0) {echo $config['concurrent'];} ?>" > (4 por defecto)
        </td>
    </tr>
    
    <tr>
        <td colspan=2>
            <input type="submit" value="Enviar">
            <input type="hidden" name="op" value="configsave">
        </td>
    </tr>
</table>

</form>
