var device_card = `<br>
<div class="device_card" id="device_card_{%device_id%}" style="background-color: {%color%}">
    <h4 class = "device_card_label">{%device_id%}</h4>
    <hr class = "device_card_line">
    <p>Key : {%device_key%}</p>
    <p id="device_status_{%device_id%}" class="device_card_status">Status : {%device_status%}</p>
    <p id="device_location_{%device_id%}" class="device_card_location">Location : {%device_location%}</p>
    <button id="device_button_{%device_id%}" class="device_card_button" onclick="{%auth_deauth_function%}">{%auth_deauth%}</button>
    <button class="device_card_button" onclick="updateLocation('{%device_id%}')">Update Location</button>
    <button class="device_card_button" onclick="deleteDevice('{%device_id%}')">Delete</button>
</div><br>`;

function delay(delayInms) {
    return new Promise(resolve => {
      setTimeout(() => {
        resolve();
      }, delayInms);
    });
}

function populate( deviceList ) {

    var device_card_html = "";

    deviceList.forEach( ( element, index, array ) => {

        var temp = device_card.replaceAll( "{%device_id%}", element["device_id"] ).replace("{%device_key%}", element["api key"]).replace( "{%device_location%}", element["location"]);
        
        if ( element["registered"] ) {
            temp = temp.replace( "{%color%}", "rgb(206, 241, 134);").replace( "{%auth_deauth_function%}", ("deauthorizeDevice('" + element["device_id"] + "')" ) ).replace( "{%auth_deauth%}", "Deauthorize" ).replace( "{%device_status%}", "Authorized");
        }
        else {
            temp = temp.replace( "{%color%}", "rgb(255, 162, 125)").replace( "{%auth_deauth_function%}", ("authorizeDevice('" + element["device_id"] + "')" ) ).replace( "{%auth_deauth%}", "Authorize" ).replace( "{%device_status%}", "Unauthorized");
        }

        device_card_html += temp;
    });

    document.getElementById( "content" ).innerHTML += device_card_html;
}

function getDevices(){
    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;

    xhr.addEventListener( "readystatechange", function() {
        if ( this.readyState === 4 ) {
            const resp = JSON.parse( this.responseText );

            if( resp["message"] === "done" ) {
                populate( resp["devices"] );
            }
        }
    });

    xhr.open( "GET", "/devices/aicam/getall" );
    xhr.send();
}

function updateLocation( deviceID ) {

    const location = prompt( "Location where the device is deployed" );

    if( !location.length ){
        alert( "Invalid location" );
        return;
    }

    var data = JSON.stringify( {
        "device_id" : deviceID,
        "location" : location
    });

    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;

    xhr.addEventListener( "readystatechange", function() {
        if( this.readyState === 4 ){
            const resp = JSON.parse( this.responseText );

            if ( resp["message"] === "authentication requried" ){
                window.location.replace( "/app/page/login_page.html");
                return;
            }

            alert( resp["message"] );

            if( this.status === 200 ){
                document.getElementById( "device_location_"+deviceID ).innerHTML = "Location : "+location;
            }
        }
    });

    xhr.open("PATCH", "/devices/aicam/updateone/location");
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send( data );
}

function authorizeDevice( deviceID ) {

    if( document.getElementById("device_status_"+deviceID).innerHTML === "Status : Authorized" )
    {
        alert( "Already authorized" );
        return;
    }

    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;

    xhr.addEventListener( "readystatechange", function() {
        if( this.readyState === 4 ){
            const resp = JSON.parse( this.responseText );

            if ( resp["message"] === "authentication required" ){
                window.location.replace( "/app/page/login_page.html");
                return;
            }

            alert( resp["message"] );

            if ( this.status === 200 ){
                /*document.getElementById( "device_card_"+deviceID ).style.backgroundColor = "rgb(206, 241, 134)";
                document.getElementById( "device_status_"+deviceID ).innerHTML = "Status : "+"Authorized";
                const btn = document.getElementById( "device_button_"+deviceID );
                btn.onclick = deauthorizeDevice( deviceID );
                btn.innerHTML = "Deauthorize";*/
                window.location.reload();
            }
        }
    });

    xhr.open( "PATCH", "/devices/aicam/authorize?device_id="+deviceID );
    xhr.send();
}

function deauthorizeDevice( deviceID ) {

    if( document.getElementById("device_status_"+deviceID).innerHTML === "Status : Unauthorized" )
    {
        alert( "Already un-authorized" );
        return;
    }

    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;

    xhr.addEventListener( "readystatechange", function() {
        if( this.readyState === 4 ){
            const resp = JSON.parse( this.responseText );

            if ( resp["message"] === "authentication required" ){
                window.location.replace( "/app/page/login_page.html");
                return;
            }

            alert( resp["message"] );

            if ( this.status === 200 ){
                /*
                document.getElementById( "device_card_"+deviceID ).style.backgroundColor = "rgb(255, 162, 125)";
                document.getElementById( "device_status_"+deviceID ).innerHTML = "Status : "+"Unauthorized";
                const btn = document.getElementById( "device_button_"+deviceID );
                btn.onclick = authorizeDevice(deviceID);
                btn.innerHTML = "Authorize";*/
                window.location.reload();
            }
        }
    });

    xhr.open( "PATCH", "/devices/aicam/deauthorize?device_id="+deviceID );
    xhr.send();
}

function deleteDevice( deviceID ) {
    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;

    xhr.addEventListener("readystatechange", function() {
        if(this.readyState === 4) {
            const resp = JSON.parse( this.responseText );

            if( resp["message"] === "authentication required" ) window.location.replace( "/app/page/login_page.html" );

            alert( resp["message"] );

            if( this.status === 200 ) {
                const elem = document.getElementById( "device_card_"+deviceID );
                elem.parentNode.removeChild( elem );
            }
        }
      });
      
      xhr.open("DELETE", "/devices/aicam/removeone?device_id="+deviceID);
      xhr.send();
}

async function generateEncodingFile() {
    
    const disp = document.getElementById( "generate_encoding_file_msg" );
    const btn = document.getElementById( "generate_encoding_file_button" );
    const loader = document.getElementById( "generate_encoding_file_loader" );

    btn.style.display = "none";
    loader.style.display = "block";

    var requestOptions = {
        method: 'PUT',
        redirect: 'follow'
    };
      
    var resp = await fetch("/encodingfile/generate", requestOptions ).then( response => response.json() ).catch( error => { return {"message":"failed"} } );

    if( resp["messsage"] === "failed" )
    {
        btn.style.display = "inline";
        loader.style.display = "none";
        disp.innerHTML = "failed";
        disp.style.color = "red";
    }
    else{

        while ( true ) {

            await delay( 5000 );

            var requestOptions = {
                method: 'GET',
                redirect: 'follow'
            }
              
            resp = await fetch("/encodingfile/status", requestOptions).then( response => response.json() ).catch( error => { return { "message" : "failed" } } );

            if ( resp["message"] != "running" ){
                
                btn.style.display = "inline";
                loader.style.display = "none";
                
                
                if( resp["message"] === "stopped" )
                {
                    disp.innerHTML = "generated";
                    disp.style.color = "green";
                }
                else
                {
                    disp.innerHTML = resp["message"]; 
                    disp.style.color = "red";
                }

                break;
            }
        }

    }

}