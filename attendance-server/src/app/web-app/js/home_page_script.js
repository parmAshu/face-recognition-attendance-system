function updateCredentials() 
{
    var xhr = new XMLHttpRequest()

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    console.log( username );
    console.log( password );

    msg = document.getElementById("msg");

    if( !username.length || !password.length  )
    {
        console.log("missing username or password");
        msg.innerHTML = "missing username or password";
        msg.style.color = "red";
        return;
    }

    var data = JSON.stringify({
        "username": username,
        "password": password
    });

    xhr.addEventListener("readystatechange", function()
    {
        if( this.readyState === 4 ) 
        {
            resp = JSON.parse( this.responseText );

            if( resp["message"] === "authentication required" ) window.location.replace( "/app/page/login_page.html" );

            msg.innerHTML = resp["message"];

            if( this.status === 200 ) msg.style.color = "green";
            else msg.style.color = "red";
        }
    });

    xhr.open("POST", "/auth/update/admin/credentials" );
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(data);
}