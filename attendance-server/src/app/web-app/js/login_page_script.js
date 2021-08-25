function login_func()
{
    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    msg = document.getElementById("msg");

    if( !username.length || !password.length  )
    {
        console.log("missing username or password");
        msg.innerHTML = "missing username or password";
        msg.style.color = "red";
        return;
    }

    xhr.addEventListener("readystatechange", function() {
        if( this.readyState === 4 ) 
        {
            resp = JSON.parse( this.responseText );
            
            if ( resp["message"] === "success" ) window.location.replace( "/app/auth/page/home_page.html" );

            msg.innerHTML = resp["message"];
            msg.style.color = "red";
        }
    });

    xhr.open("POST", "/auth/login?username="+username+"&password="+password );
    xhr.send();
}