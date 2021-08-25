function download( data, filename ){
    var element = document.createElement("a");
    element.setAttribute( "href", "data:text/csv;charset=utf-8," + encodeURIComponent(data) );
    element.setAttribute( "download", filename );
    element.style.display = "none";
    document.body.appendChild( element );
    element.click();
}

function markEmployeeAttendance() 
{   
    const disp = document.getElementById( "mark_employee_attendance_msg" );
    const uid = document.getElementById( "mark_employee_attendance_uid" );
    const markDatetime = document.getElementById( "mark_employee_attendance_datetime" );

    if ( !uid.value.length ) {
        disp.innerHTML = "provide a valid employee id";
        disp.style.color = "red";
        return;
    }
    else if ( !markDatetime.value.length ) {
        disp.innerHTML = "provide valid date time";
        disp.style.color = "red";
        return;
    }

    var data = JSON.stringify({
        "uid": uid.value,
        "datetime": markDatetime.value+":00"
    });
      
    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;
      
    xhr.addEventListener("readystatechange", function() {
        if(this.readyState === 4) {

            resp = JSON.parse( this.responseText );

            if ( resp["message"] === "authentication required" ) {
                window.location.replace( "/app/page/login_page.html" );
            }

            disp.innerHTML = resp["message"];
            if ( this.status === 200 ) disp.style.color = "green";
            else disp.style.color = "red";
        }
    });

    console.log( data );
      
    xhr.open("POST", "/attendance/mark/one" );
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(data);
}

function getEmployeeAttendance() {

    const disp = document.getElementById( "get_employee_attendance_msg" );
    const uid = document.getElementById( "get_employee_attendance_uid" );
    const startdate = document.getElementById( "get_employee_attendance_startdate" );
    const enddate = document.getElementById( "get_employee_attendance_enddate" );

    if ( !uid.value.length )
    {
        disp.innerHTML = "provide a valid employee ID";
        disp.style.color = "red";
        return;
    }
    else if( !startdate.value.length )
    {
        disp.innerHTML = "provide a valid start date";
        disp.style.color = "red";
        return;
    }
    else if( !enddate.value.length )
    {
        disp.innerHTML = "provide a valid end date";
        disp.style.color = "red";
        return;
    }

    var data = JSON.stringify({
        "uid": uid.value,
        "startdate": startdate.value,
        "enddate" : enddate.value
    });
      
    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;

    xhr.addEventListener( "readystatechange", function() {
        if ( this.readyState === 4 ) {

            if( this.status === 200 ) {               
                download( this.responseText, "attendance.csv" );
            }
            else {
                resp = JSON.parse( this.responseText );

                if( resp["message"] === "authentication required" ) window.location.replace( "/app/page/login_page.html" );

                disp.innerHTML = resp["message"];
                disp.style.color = "red";
            }
        }
    });

    xhr.open( "POST", "/attendance/get/one/between" );
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send( data );
}

function getAllEmployeeAttendance() {

    const disp = document.getElementById( "get_allemployee_attendance_msg" );
    const startdate = document.getElementById( "get_allemployee_attendance_startdate" );
    const enddate = document.getElementById( "get_allemployee_attendance_enddate" );

    if ( !startdate.value.length ){
        disp.innerHTML = "provide a valid start date";
        disp.style.color = "red";
        return;
    }
    else if ( !enddate.value.length ) {
        disp.innerHTML = "provide a valid end data";
        disp.style.color = "red";
        return;
    }

    var data = JSON.stringify( {
        "startdate" : startdate.value,
        "enddate" : enddate.value
    });

    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;

    xhr.addEventListener( "readystatechange", function() {
        if( this.readyState === 4 ) {
            if( this.status === 200 ) {
                download( this.responseText, "attendance.csv" );
            }
            else {
                resp = JSON.parse( this.responseText );
                if( resp["message"] === "authentication required" ) window.location.replace( "/app/page/login_page.html" );

                disp.innerHTML = resp["message"];
                disp.style.color = "red";
            }
        }
    });

    xhr.open( "POST", "/attendance/get/all/between" );
    xhr.setRequestHeader( "Content-Type", "application/json" );
    xhr.send( data );
}

function deleteAttendanceRecord() {
    const disp = document.getElementById( "delete_attendance_record_msg" );
    const date = document.getElementById( "delete_attendance_record_date");

    if ( !date.value.length )
    {
        disp.innerHTML = "provide a valid date";
        disp.style.color = "red";
        return;
    }

    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;

    var data =  JSON.stringify( {
        "date" : date.value
    });

    xhr.addEventListener( "readystatechange", function() {

        if ( this.readyState === 4 ) {
            resp = JSON.parse( this.responseText );

            if ( resp["message"] === "authentication required" ) window.location.replace( "/app/page/login_page.html" );

            disp.innerHTML = resp["message"];
            if ( this.status === 200 ) disp.style.color = "green";
            else disp.style.color = "red";
        }

    });

    xhr.open("DELETE", "/attendance/deleterecord/one");
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send( data );
}

function deleteAllAttendanceRecords() {
    const disp = document.getElementById( "delete_attendance_record_msg" );

    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;

    xhr.addEventListener( "readystatechange", function(){

        if ( this.readyState === 4 ) {
            resp = JSON.parse( this.responseText );

            if ( resp["message"] === "authentication required" ) window.location.replace( "/app/page/login_page.html" );

            disp.innerHTML = resp["message"];
            if( this.status === 200 ) disp.style.color = "green";
            else disp.style.color = "red";
        }

    });

    xhr.open("DELETE", "/attendance/deleterecord/all");
    xhr.send();

}