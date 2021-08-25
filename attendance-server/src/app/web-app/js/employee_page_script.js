function clearEmployeeDetails() {
    document.getElementById( "employee_firstname").innerHTML = "";
    document.getElementById( "employee_gender").innerHTML = ""
    document.getElementById( "employee_email").innerHTML = "";
    document.getElementById( "employee_dob").innerHTML = "";
    document.getElementById( "employee_doj").innerHTML = ""
    document.getElementById( "employee_department").innerHTML = "";
    document.getElementById( "employee_title").innerHTML = "";
    document.getElementById( "employee_image" ).style.display = "None";
    disp.innerHTML = "";
}

function getEmployeeDetails()
{
    disp = document.getElementById( "get_employee_details_msg" );
    uid = document.getElementById( "get_employee_details_uid" ).value;

    if ( !uid.length ){
        disp.innerHTML = "provide a valid employee id";
        disp.style.color = "red";
        return;
    }

    var data = JSON.stringify({
        "uid": uid
    });
      
    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;

    xhr.addEventListener("readystatechange", function() {
        if(this.readyState === 4 ) 
        {
            resp = JSON.parse( this.responseText );
            
            if ( resp["message"] === "authentication required" ) window.location.replace("/app/page/login_page.html" );

            if ( resp["message"] === "success" )
            {
                document.getElementById( "employee_firstname").innerHTML = resp["details"]["firstname"] + " " + resp["details"]["lastname"];
                document.getElementById( "employee_gender").innerHTML = "Gender - " + resp["details"]["gender"];
                document.getElementById( "employee_email").innerHTML = "Email - " + resp["details"]["email"];
                document.getElementById( "employee_dob").innerHTML = "DOB - " + resp["details"]["DOB"];
                document.getElementById( "employee_doj").innerHTML = "DOJ - " + resp["details"]["DOJ"];
                document.getElementById( "employee_department").innerHTML = "Department - " + resp["details"]["department"];
                document.getElementById( "employee_title").innerHTML = "Title - " + resp["details"]["title"];
                disp.innerHTML = "";
                IMG = document.getElementById( "employee_image");
                IMG.style.display = "inline";
                IMG.src = "/employee/getone/image?uid=" + uid;
            }
            else{
                clearEmployeeDetails();
                disp.innerHTML = resp["message"];
                disp.style.color = "red";
            }
        }
    });

    xhr.open("POST", "/employee/getone/details" );
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send( data );
}



function addEmployee() {

    const uid = document.getElementById( "add_employee_uid" );
    const firstname = document.getElementById( "add_employee_firstname" );
    const lastname = document.getElementById( "add_employee_lastname" );
    const email = document.getElementById( "add_employee_email" );
    const dob = document.getElementById( "add_employee_dob" );
    const doj = document.getElementById( "add_employee_doj" );
    const department = document.getElementById( "add_employee_department" );
    const title = document.getElementById( "add_employee_title" );
    const gender = document.getElementById( "add_employee_gender" );

    const disp = document.getElementById( "add_employee_msg" );

    var imageFile =  document.getElementById("add_employee_image").files[0];

    var text = "";
    if ( !uid.value.length ) {
        text += "Missing Employee ID ";
    }
    else if ( !firstname.value.length || !lastname.value.length ) {
        text += "Missing name ";
    }
    else if ( !gender.value.length ) {
        text += "Missing gender ";
    }
    else if ( !email.value.length ) {
        text += "Missing email ";
    }
    else if ( !dob.value.length ) {
        text += "Missing date of birth ";
    }
    else if ( !doj.value.length ) {
        text += "Missing date of joining ";
    }
    else if ( !department.value.length ) {
        text += "Missing department ";
    }
    else if ( !title.value.length ) {
        text += "Missing title ";
    }
    else if( imageFile === undefined )
    {
        text += "No image"
    }
    
    if( text.length ){
        disp.innerHTML = text;
        disp.style.color = "red";
        return;
    }

    var data = new FormData();
    data.append("image", imageFile, imageFile["name"]);
    data.append("uid", uid.value );
    data.append("firstname", firstname.value );
    data.append("lastname", lastname.value );
    data.append("gender", gender.value );
    data.append("email", email.value );
    data.append("doj", doj.value );
    data.append("dob", dob.value );
    data.append("department", department.value );
    data.append("title", title.value );

    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;

    xhr.addEventListener("readystatechange", function() {
        if( this.readyState === 4) {
            resp = JSON.parse( this.responseText );
            
            if( resp["message"] === "authentication required" ) window.location.replace( "/app/page/login_page.html" );

            disp.innerHTML = resp["message"];
            if(this.status === 201 ) disp.style.color = "green";
            else disp.style.color = "red";
        }
    });
    
    xhr.open( "POST", "/employee/addone" );
    xhr.send( data );
}

function removeEmployee() {

    disp = document.getElementById( "remove_employee_msg" );
    uid = document.getElementById( "remove_employee_uid" ).value;

    if ( !uid.length ){
        disp.innerHTML = "provide a valid employee id";
        disp.style.color = "red";
        return;
    }

    var data = JSON.stringify( {
        "uid" : uid
    });

    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;

    xhr.addEventListener("readystatechange", function() {
        if( this.readyState === 4 ) 
        {
            resp = JSON.parse( this.responseText );

            if( resp["message"] === "authentication required" ) window.location.replace( "/app/page/login_page.html" );

            disp.innerHTML = resp["message"];
            if ( this.status === 200 ) disp.style.color = "green";
            else disp.style.color = "red";
        }
    });

    xhr.open("DELETE", "/employee/removeone");
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send( data );
}

function updateEmployeeDetails() {

    disp = document.getElementById( "update_employee_details_msg" );
    uid = document.getElementById( "update_employee_details_uid" ).value;
    email = document.getElementById( "update_employee_details_email").value;
    title = document.getElementById( "update_employee_details_title" ).value;
    department = document.getElementById( "update_employee_details_department" ).value;

    if( !uid.length )
    {
        disp.innerHTML = "provide a valid employee ID";
        disp.style.color = "red";
        return;
    }

    if( !email.length && !title.length && !department.length){
        disp.innerHTML = "no field provided";
        disp.style.color = "red";
        return;
    }

    var data = { 
        "uid" : uid
    };

    if( email.length ) data["email"] = email;
    if( title.length ) data["title"] = title;
    if( department.length ) data["department"] = department;

    data = JSON.stringify(data);

    var xhr = new XMLHttpRequest();

    xhr.addEventListener("readystatechange", function() {
        if(this.readyState === 4) {
            resp = JSON.parse( this.responseText );

            disp.innerHTML = resp["message"];
            if( this.status === 200 ) disp.style.color = "green";
            else disp.style.color = "red";
        }
    });

    xhr.open( "PATCH", "/employee/updateone/details" );
    xhr.setRequestHeader( "Content-Type", "application/json" );
    xhr.send( data );
}

function updateEmployeeImage() {

    disp = document.getElementById( "update_employee_image_msg" );

    uid = document.getElementById( "update_employee_image_uid" ).value;
    var imageFile =  document.getElementById( "update_employee_image_image" ).files[0];

    if ( !uid.length ) {
        disp.innerHTML = "provide a valid employee ID";
        disp.style.color = "red";
        return;
    }
    else if( imageFile === undefined )
    {
        disp.innerHTML = "provide a valid image";
        disp.style.color = "red";
        return;
    }

    var data = new FormData();
    data.append("image", imageFile, imageFile["name"]);
    data.append("uid", uid );

    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;

    xhr.addEventListener("readystatechange", function() {
        if( this.readyState === 4) {
            resp = JSON.parse( this.responseText );
            
            if( resp["message"] === "authentication required" ) window.location.replace( "/app/page/login_page.html" );

            disp.innerHTML = resp["message"];
            if(this.status === 200 ) disp.style.color = "green";
            else disp.style.color = "red";
        }
    });
    
    xhr.open( "PATCH", "/employee/updateone/image" );
    xhr.send( data );
}