
window.fbAsyncInit = function() {
    FB.init({
        appId      : '907786629329598',
        cookie     : true,  // allow server to access the session
        xfbml      : true,  // parse social plugins on this page
        version    : 'v2.5' // use graph api version 2.5
    });
};

// Load the SDK asynchronously
//
(function(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) return;
    js = d.createElement(s); js.id = id;
    js.src = "//connect.facebook.net/en_US/sdk.js";
    fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));

// sendTokenToServer()
// successful.  See statusChangeCallback() for when this call is made.
//
function sendTokenToServer() {

    var access_token = FB.getAuthResponse()['accessToken'];

    console.log(access_token)
    console.log('Welcome!  Fetching your information.... ');

    FB.api('/me', function(response) {

        console.log('Successful login for: ' + response.name);

        $.ajax({
            type: 'POST',
            url: '/fbconnect?state={{STATE}}',
            processData: false,
            data: access_token,
            contentType: 'application/octet-stream; charset=utf-8',
            success: function(result) {
                // Handle or verify the server response if necessary.
                if (result) {
                    $('#result').html('Login Successful!</br>'+ result + '</br>Redirecting...')
                    setTimeout(function() {
                        window.location.href = "/restaurant";
                    }, 4000);
                    
                } else {
                    $('#result').html('Failed to make a server-side call. Check your configuration and console.');
                }
            }
            
        });
    });
}
