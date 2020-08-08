document.addEventListener('DOMContentLoaded', function() {
    
    //follow button event
    document.querySelector("#comment-form").onsubmit = () => {

        event.preventDefault();

        var comment = document.getElementById("id_comment_content").value;
        var recipe = document.querySelector("#comment-form").getAttribute("data-recipe");

        fetch("/comment", {
            method: "POST",
            headers: { "X-CSRFToken": getCookie('csrftoken') },
            body: JSON.stringify({
                comment: comment,
                recipe: recipe
            })
          })
            .then(response => response.json())
            .then(result => {
              console.log(result);
              if (result.status == 201) {
                document.getElementById("comments-div").innerHTML += `<p>${comment}</p>
                <p><b>User:</b> ${ result.user }</p>
                <p>${ result.created_at }</p>
                <hr>`
                document.getElementById("id_comment_content").value = '';
              } else {
                  alert(`${result.message}`);
              }
            
            });
    };


});

// The following function are copying from 
// https://docs.djangoproject.com/en/dev/ref/csrf/#ajax
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}