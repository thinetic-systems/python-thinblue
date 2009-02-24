<?php
defined( '_VALID_THINBLUE' ) or die( 'Direct Access to this location is not allowed.' );
?>

<div align="center"><h1>Autenticaci&oacute;n</h1></div>
	<form action="index.php" method="POST">
		<table align="center" width="225" cellspacing="2" cellpadding="2" border="0">
			<tr>
				<td colspan="2" align="center" bgcolor=#cccccc>Introduce la clave
				</td>
			</tr>
			<tr>
				<td align="right">Usuario:</td>
				<td><input type="Text" name="usuario" size="8" maxlength="50"></td>
			</tr>
			<tr>
				<td align="right">Contrase&ntilde;a:</td>
				<td><input type="password" name="contrasena" size="8" maxlength="50"></td>
			</tr>
			<tr>
				<td colspan="2" align="center"><input type="Submit" value="ENTRAR"></td>
			</tr>
		</table>
	</form>

<script language="javascript">

                document.forms[0].usuario.focus();

</script>
