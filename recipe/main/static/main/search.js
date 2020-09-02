document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('#recipe-btn').addEventListener('click', recipe_view);
    document.querySelector('#users-btn').addEventListener('click', user_view);

    //default
    recipe_view()
})

function recipe_view() {
    document.querySelector("#recipe-results").style.display = 'block';
    document.querySelector("#user-results").style.display = 'none';
}

function user_view() {
    document.querySelector("#recipe-results").style.display = 'none';
    document.querySelector("#user-results").style.display = 'block';
}