

$(document).ready(function() {
   if ( $("input#username") ){
     if ( $("input#username").text() != "")
        $("input#password").focus();
    
     else
        $("input#username").focus();
   }
});


