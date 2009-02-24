<?php
defined( '_VALID_THINBLUE' ) or die( 'Direct Access to this location is not allowed.' );

$config=$sqlite->get_config();
/*
echo "<pre>FILES=".print_r($_FILES, true)."</pre>";
echo "<pre>REQUEST=".print_r($_REQUEST, true)."</pre>";
echo "<pre>HTTP_POST_FILES=".print_r($HTTP_POST_FILES, true)."</pre>";
*/



if ( ! move_uploaded_file($_FILES['userfile']['tmp_name'], $config['file_path']."/".$_FILES['userfile']['name']) ) {
        echo "Error subiendo archivo: ".$_FILES['userfile']['name'];
}
else {
    echo "<h3>Archivo guardado correctamente: ".$_FILES['userfile']['name'] . "</h3>";
    $config=$sqlite->get_config();
    $config['sendfile']=$_FILES['userfile']['name'];
    $sqlite->save_sendfile($config);
    if (leer_datos("sendagain") == "1") {
        echo "<h4>Marcando todos los teléfonos para reenviar...</h4>";
        $sqlite->set_pending();
    }
}

?>
