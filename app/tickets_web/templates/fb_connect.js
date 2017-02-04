
window.fbAsyncInit = function() {
    FB.init({
        appId      : '{{fb_app_id}}',
        cookie     : true,  // allow server to access the session
        xfbml      : true,  // parse social plugins on this page
        version    : 'v2.5' // use graph api version 2.5
    });
};

// Load the SDK asynchronously
function load_SDK_Async(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) {
        return;
    }
    js = d.createElement(s);
    js.id = id;
    js.src = "//connect.facebook.net/en_US/sdk.js";
    fjs.parentNode.insertBefore(js, fjs);
}
load_SDK_Async(document, 'script', 'facebook-jssdk');

// Here we run a very simple test of the Graph API after login is
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
            url: '{{ url_for('connect', provider_name='facebook', session_id=SESSION_ID) }}',
            //_csrf_token: '{{csrf_token()}}',
            processData: false,
            data: access_token,
            contentType: 'application/octet-stream; charset=utf-8',
            success: function(result) {
                // Handle or verify the server response if necessary.
                if (result) {
                    window.location.href = "{{redirect_url}}";
                    //$('#result').html('Login Successful!</br>'+ result + '</br>Redirecting...')
                    //setTimeout(function() {
                    //   window.location.href = "{{redirect_url}}";
                    //}, 4000);
                    
                } else {
                    $('#result').html('Failed to make a server-side call. Check your configuration and console.');
                }
            }
            
        });
    });
}

