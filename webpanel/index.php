<?php
session_start();
define("_VALID_THINBLUE", '1');
require_once("db.php");



if (leer_datos("usuario")==user && md5(leer_datos("contrasena")) ==pass){
        $_SESSION["autenticado"] = "SI";
		$conectar="si";
}
elseif (leer_datos("usuario")!="" && (leer_datos("usuario")!= user || md5(leer_datos("contrasena")) != pass)){
        $conectar="error";
}
else{
	$conectar="";
}


if($_SESSION["autenticado"] == "SI"){
    $sqlite=new DB(DBFILE);



    if (leer_datos("op") == "get_image") {
        download_image();
        die();
    }

}


?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
	<title>ThinBlue Admin</title>
	<link href="style.css" rel="stylesheet" type="text/css">
	<meta http-equiv="Content-Type" content="text/html;charset=utf-8">
</head>
<body class="thebody">

<p align="center">
<center>
<br>
<table class="sec">
		<tr class="secheader">
			<td class="secheader">
			<center>
			    <img src="thinblue.jpg" alt="Thinetic Systems">
			</center>
			</td>
		</tr>
</table>
<br><br>
<table class="sec">
	<tr class="secheader">

		<td class="secheader"><h2>Administraci&oacute;n de la configuración y estadísticas</h2></td>
	</tr>
		<tr class="secbody">
			<td class="secbody"><br>
<?php
if($_SESSION["autenticado"] == "SI"){
?>
	<center><a href='index.php'>INICIO</a> | 
	<a href='index.php?op=config'>Ver Configuración</a> | 
	<a href='index.php?op=file'>Archivo de envío</a> | 
	<a href='index.php?op=phones'>Ver Accesos</a> | 
	<a href='index.php?op=logout'>SALIR</a></center>
<?php
}
?>
			
			<br>
			<div class="organize">

<?php



//mostramos mensaje
if ($conectar=="si"){
	echo "<pre><center><font color=red><h2>Usuario y contrase&ntilde;a correctos.</h2></font></center></pre>";
	}
elseif ($conectar=="error"){
	echo "<pre><center><font color=red><h2>Error en usuario o contrase&ntilde;a.</h2></font></center></pre>";
	}


if($_SESSION["autenticado"] == "SI"){
        if (leer_datos('op') == "config" ){
		    require('config.php');
		}
		elseif (leer_datos('op') == "configsave" ){
		    require('configsave.php');
		}
		elseif (leer_datos('op') == "phones" ){
		    require('phones.php');
		}
		elseif (leer_datos('op') == "file" ){
		    require('file.php');
		}
		elseif (leer_datos('op') == "filesave" ){
		    require('filesave.php');
		}
		
		elseif(leer_datos('op')  == "logout"){
			$_SESSION["autenticado"] = "NO";
			session_unset();
			session_destroy();
			echo "<h3><center>Deconectando...</center></h3>";
			echo "<meta http-equiv=\"refresh\" content=\"1; URL=index.php\">";
			}
		else{
		require('todos.php');
		}
}
else{
	//poner el panel de login y pass
	require('registro.php');
	}
?>			

			</div><br>
			<h4>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &lt;=== &nbsp;&nbsp;<a href='javascript:history.go(-1)'>Volver</a></h4>
			</td>

	</tr>
</table>


<p align="center">

<i><a href="http://www.thinetic.es">http://www.thinetic.es</a></i><br>
<i>thinetic at thinetic.es</i>

</body>
</html>



<?php
@$sqlite->close();
?>
