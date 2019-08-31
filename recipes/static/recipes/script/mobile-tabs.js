(function () {
    "use strict";

    var ingredientsTitle = document.getElementById('ingredients-title');
    var directionsTitle = document.getElementById('directions-title');
    var ingredients = document.getElementById('ingredients-content');
    var directions = document.getElementById('directions-content');

    ingredientsTitle.onclick = function() {
        if (!ingredientsActive) {
            ingredientsTitle.classList.add('active');
            ingredients.classList.remove('inactive');
            directionsTitle.classList.remove('active');
            directions.classList.add('inactive');
            ingredientsActive = true;
        }
    };

    directionsTitle.onclick = function() {
        if (ingredientsActive) {
            ingredientsTitle.classList.remove('active');
            ingredients.classList.add('inactive');
            directionsTitle.classList.add('active');
            directions.classList.remove('inactive');
            ingredientsActive = false;
        }
    };

    // initial state
    var ingredientsActive = true;
    ingredientsTitle.classList.add('active');
    directions.classList.add('inactive');


})();