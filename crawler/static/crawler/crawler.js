(function () {
    function post(url = '', data = {}) {
        // Default options are marked with *
        // from: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
        return fetch(url, {
            method: 'POST', // *GET, POST, PUT, DELETE, etc.
            mode: 'cors', // no-cors, cors, *same-origin
            cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
            credentials: 'same-origin', // include, *same-origin, omit
            headers: {
                'Content-Type': 'application/json',
                // 'Content-Type': 'application/x-www-form-urlencoded',
            },
            redirect: 'follow', // manual, *follow, error
            referrer: 'no-referrer', // no-referrer, *client
            body: JSON.stringify(data), // body data type must match "Content-Type" header
        }).then(response => response.json()); // parses JSON response into native Javascript objects
    }

    let input = document.querySelector('#recipy-crawler-flavour');
    let textarea = document.querySelector('#recipy-crawler-text');
    let resparea = document.querySelector('#recipy-crawler-response');
    document.querySelector('#recipy-crawler-submit').addEventListener('click', async function() {
        let flavour = input.value;
        let titles = textarea.value;
        let postData = {
            titles,
            flavour,
        };

        let resp;
        try {
            resp = await post('batch', postData);
        } catch (e) {
            resp = {error: e.message}
        }
        resparea.textContent = JSON.stringify(resp, null, 4);
    }, false)
})();
