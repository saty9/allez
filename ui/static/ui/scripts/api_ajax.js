function api_post(target, data, success) {
    return api_post(target,data,success, null, null)
}

function api_post(target, data, success, failure) {
    return api_post(target,data,success, failure, null)
}

function api_post(target, data, success, failure, error){
    let csrftoken = $("[name=csrfmiddlewaretoken]").val();
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }});
    $.ajax({
        type:'POST',
        url: target,
        data: data,
        dataType: 'json',
        success: function (data) {
            if (data['success']) {
                success(data);
            } else {
                console.log(data);
                $('#alerts').innerText = "";

                if (failure){
                    failure(data)
                } else {
                    $('#alerts').append('<div class="alert alert-danger">' + data['verbose_reason'] + '</div>')
                }
            }},
        error: function (data) {
            console.log(data);
            if (error){
                error(data);
            } else {
                if (data.status == 403){
                    $('#alerts').innerText = "";
                    $('#alerts').append(
                        '<div class="alert alert-failure">You don\'t have permission to do that please check you are"+ ' +
                        'logged in and can perform this action</div>'
                    )
                }
            }
        }
    });
}