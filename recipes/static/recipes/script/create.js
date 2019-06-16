(function () {
    'use strict';

    const $ = document.querySelectorAll.bind(document);

    let spentIds = 0; // todo: ...

    function nextId() {
        spentIds += 1;
        return spentIds;
    }






    const ingredientTotalForms = $('[name="ingredient_set-TOTAL_FORMS"]')[0];
    let currentMaxIngredient = Number($('[name="ingredient_set-INITIAL_FORMS"]')[0].value);

    function nextIngredientId() {
        const id = Number(ingredientTotalForms.value);
        return id;
        currentMaxIngredient += 1;
        ingredientTotalForms.value = currentMaxIngredient;
        return currentMaxIngredient;
    }

    function updateGroupFields(event) {
        const group = this;
        const name = event.target.value;

        group.querySelectorAll('[name$="-group"]:not([data-pristine])').forEach(input => {
            input.value = name;
        })
    }

    function installIngredientFunctions(ingredientGroup) {
        const input = ingredientGroup.querySelector('.ingredient-group-input');
        // todo: this has been temporarily deactivated
        // input.addEventListener('input', updateGroupFields.bind(ingredientGroup));
    }

    $('.ingredient-group').forEach(installIngredientFunctions);

    const ingredientGroupTemplate = $('#template-ingredient-group')[0].innerText;

    function newIngredientGroup(ingredientCounter) {
        const div = document.createElement('div');

        const template = ingredientGroupTemplate.replace(/__(GROUPKEY|prefix)__/g, placeholder => ({
            GROUPKEY: nextId,
            prefix: () => ingredientCounter,
        }[placeholder])());

        div.innerHTML = template; // lots of html parsing

        let group = div.querySelector('.ingredient-group');
        group = group.parentElement.removeChild(group);
        installIngredientFunctions(group);
        return group;
    }

    function newIngredient(ingredientCounter) {
        const group = newIngredientGroup(ingredientCounter);
        group.querySelector('[name$="-group"]').setAttribute('data-pristine', '');
        group.removeChild(group.querySelector('.ingredient-group-name'));
        const children = Array.from(group.children).map(element => group.removeChild(element));

        return children;
    }

    function autoAddIngredient() {
        const ingredient = this;



        const counter = nextIngredientId();
    }









    function growTextareaHeight(event) {
        const textarea = this;

        textarea.style.height = '0px';
        const scrollHeight = textarea.scrollHeight - 20;
        // textarea.style.height = `calc(${scrollHeight}px + 20px + 2px)`;
        textarea.style.height = `calc(${scrollHeight}px + 20px + 2px)`;
    }

    function installDirectionFunctions(directionForm) {
        const textarea = directionForm.querySelector('textarea');
        growTextareaHeight.bind(textarea)();
        textarea.addEventListener('input', growTextareaHeight.bind(textarea));
    }

    $('.create-direction').forEach(installDirectionFunctions);









    // animate input labels
    const inputs = $('.md-text-input input, .md-text-input textarea');
    for (let i = 0; i < inputs.length; ++i) {
        const input = inputs[i];
        if (!input.value)
            input.classList.add('blank');

        input.addEventListener('blur', () => {
            if (!input.value)
                input.classList.add('blank');
            else
                input.classList.remove('blank');
        });
    }

    // add at least one ingredient per group

})();
