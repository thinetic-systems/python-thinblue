<?php

defined( '_VALID_THINBLUE' ) or die( 'Direct Access to this location is not allowed.' );

define("user", 'root');
define("pass", '21b3851fac0cb394d5fb42e20b25841a');

if (file_exists("/.dirs/dev/thinblue/database.db")) {
    define("DBFILE", "/.dirs/dev/thinblue/database.db");
} else {
    define("DBFILE", "/var/lib/thinblue/database.db");
}



class DB
{
    function DB ($dbfile)
    {
        $this->sqliteError="";
        if ( ! $this->dbHandle = sqlite_open($dbfile, 0666, $this->sqliteError) ) {
          echo ($sqliteError);
          $this->connected=false;
          return;
        }
        $this->connected=True;
    }
    

    function get_all_phones() {
        if (! $this->connected) return False;
        $sql="SELECT * from phones;";
        $result = sqlite_query($this->dbHandle, $sql);
        $phones = sqlite_fetch_all($result);
        return $phones;
    }

    function get_config() {
        if (! $this->connected) return False;
        $sql="SELECT * from config;";
        $result = sqlite_query($this->dbHandle, $sql);
        $config = sqlite_fetch_array($result);
        return $config;
    }

    function save_config($config) {
        //echo "<pre>" . print_r($config, true) ."</pre>";
        // stop=2 reload config
        $sql="UPDATE config SET debug='".$config['debug']."', timeout='".$config['timeout']."', concurrent='".$config['concurrent']."', stop='2';";
        $res=sqlite_exec($this->dbHandle, $sql);
        if (!$res) {
            return False;
        } else {
            return True;
        }
    }

    function save_sendfile($config) {
        //echo "<pre>" . print_r($config, true) ."</pre>";
        // stop=2 reload config
        $sql="UPDATE config SET sendfile='".$config['sendfile']."', stop='2' ;";
        $res=sqlite_exec($this->dbHandle, $sql);
        if (!$res) {
            return False;
        } else {
            return True;
        }
    }

    function clean() {
        $sql="DELETE from phones;";
        $res=@sqlite_exec($this->dbHandle, $sql);
        if (!$res) {
            return False;
        } else {
            return True;
        }
    }
    
    function set_pending() {
        $sql="UPDATE phones set status='seen1';";
        $res=@sqlite_exec($this->dbHandle, $sql);
        if (!$res) {
            return False;
        } else {
            return True;
        }
    }

    function get_error(){
        return $this->sqliteError;
    }

    function close() {
        @sqlite_close($this->dbHandle);
    }
}

function leer_datos($nombre){
	if ($_GET[$nombre] != "" ){
			return addslashes ($_GET[$nombre]);
		}
	elseif ($_POST[$nombre] != "" ){
			return addslashes ($_POST[$nombre]);
		}
	else
		return "";
}

function is_image($_file) {
    $tmp=explode(".", $_file);
    $ext=$tmp[count($tmp)-1];
    $image=False;
    switch ($ext) {
           
           case "gif":
           case "png":
           case "jpe":
           case "jpeg":
           case "jpg": $image=True; break;
           
           default: $image=False;
    }
    return $image;
}

function get_filetype($_file) {
    $tmp=explode(".", $_file);
    $ext=$tmp[count($tmp)-1];
    switch ($ext) {
           case "pdf": $ctype="application/pdf"; break;
           case "jar": $ctype="application/java-archive"; break;
           case "exe": $ctype="application/octet-stream"; break;
           case "zip": $ctype="application/zip"; break;
           case "doc": $ctype="application/msword"; break;
           case "xls": $ctype="application/vnd.ms-excel"; break;
           case "ppt": $ctype="application/vnd.ms-powerpoint"; break;
           case "gif": $ctype="image/gif"; break;
           case "png": $ctype="image/png"; break;
           case "gz":  $ctype="application/x-gzip"; break;
           case "txt": $ctype="application/plain-text"; break;
           case "jpe":
           case "jpeg":
           case "jpg": $ctype="image/jpg"; break;
           case "php":
           case "htm":
           case "html":
           /*case "txt": */ die("<b>Extensi&oacute;n ". $extension ." no permitida!</b>"); break;
           default: $ctype="application/force-download";
    }
    return $ctype;
}


function download_image() {
    $sql=new DB(DBFILE);
    $_config=$sql->get_config();
    $img_path=$_config['file_path'] . $_config['sendfile'];
    if ( is_file($img_path) ) {
        $ctype=get_filetype($img_path);
        if ( leer_datos("force") != "download" && is_image($img_path) ) {
            $len = filesize($img_path);
            header("Content-Type: $ctype");
            header("Content-Length: $len");
            header("Content-Disposition: inline; filename=\"".$_config['sendfile']."\"");
            readfile($img_path);
        }
        else {
            header("Pragma: public");
            header("Expires: 0");
            header("Cache-Control: must-revalidate, post-check=0, pre-check=0");
            header("Cache-Control: private",false);
            header("Content-Type: $ctype");
            header("Content-Disposition: attachment; filename=\"".$_config['sendfile']."\";");
            header("Content-Transfer-Encoding: binary");
            header("Content-Length: $len");
            set_time_limit(0);
            readfile($img_path);
        }
    }
}
?>
