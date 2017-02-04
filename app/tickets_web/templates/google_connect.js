function signInCallback(authResult) {

    console.log('function signInCallback():');
    console.log(authResult);

    if (authResult['code']) {

        $.ajax({
            type: 'POST',
            url: '{{ url_for('connect', provider_name='google', session_id=SESSION_ID) }}',
            //_csrf_token: '{{csrf_token()}}',
            processData: false,
            data: authResult['code'],
            contentType: 'application/octet-stream; charset=utf-8',
            success: function(result) {

                // Handle or verify the server response if necessary.
                if (result) {
                    console.log(result);
                    window.location.href = "{{ redirect_url }}";
                } 
                else if (authResult['error']) {
                    console.log('There was an error: ' + authResult['error']);
                }
                else {
                    $('#result').html('Failed to make a server-side call. Check your configuration and console.');
                }
            }
        });
    }
}
