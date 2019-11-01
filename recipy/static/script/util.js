(function () {
    function ownProps(object) {
        return Object.keys(object).map(key => object[key]);
    }

    const MAX_32_BIT = Math.pow(2, 32);
    function tid() {
        const num = Math.floor(Math.random() * MAX_32_BIT);
        return ('00000000' + num.toString(16)).substr(-8);
    }

    function b64toBlob(b64Data, contentType='', sliceSize=512) {
        const byteCharacters = atob(b64Data);
        const byteArrays = [];

        for (let offset = 0; offset < byteCharacters.length; offset += sliceSize) {
            const slice = byteCharacters.slice(offset, offset + sliceSize);

            const byteNumbers = new Array(slice.length);
            for (let i = 0; i < slice.length; i++) {
            byteNumbers[i] = slice.charCodeAt(i);
        }

        const byteArray = new Uint8Array(byteNumbers);
            byteArrays.push(byteArray);
        }

        const blob = new Blob(byteArrays, {type: contentType});
        return blob;
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie != '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.startsWith(name + '=')) {
                    return  decodeURIComponent(cookie.substring(name.length + 1));
                }
            }
        }
        return cookieValue;
    }

    function rest(url, options) {
        return fetch(url, {
            credentials: 'same-origin',
            ...options,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                Accept: 'application/json',
                ...options.headers,
            },
        })
    }

    function post(url, body, options) {
        return rest(url, {
            body,
            method: 'post',
            ...options,
        })
    }

    function postJSON(url, body, options = {}) {
        return post(url, JSON.stringify(body), {
            headers: {
                'Content-Type': 'application/json;charset=UTF-8',
                ...options.headers,
            },
            ...options
        });
    }

    function debounce(fn, delay, awaitPrevious = false) {
        let activeTimeout;
        let resolve;
        let reject;
        let promise;

        let running;
        let _promise;

        function reset() {
            promise = new Promise((solve, ject) => {
                resolve = solve;
                reject = ject;
            })
        }

        async function invoke(args) {
            activeTimeout = null;

            const _resolve = resolve;
            const _reject = reject;
            _promise = promise;
            reset();

            try {
                running = true;
                const result = await fn.apply(this, args);
                running = false;

                _resolve(result);

            } catch (e) {
                running = false;

                _reject(e)
            }
        }

        function delayedInvoke(args) {
            _promise.finally(() => {
                // abort if cancelled between delayedInvoke() and finally().
                // this is somewhat incorrect, as it allows you to cancel beyond the specified delay
                // under certain circumstances.
                if (!activeTimeout) return;
                invoke(args);
            })
        }

        function debouncedFn(...args) {
            const invocation = awaitPrevious && running ? delayedInvoke : invoke;

            if (activeTimeout) window.clearTimeout(activeTimeout);
            activeTimeout = window.setTimeout(invocation, delay, args);

            return promise;
        }

        debouncedFn.cancel = function (error = null) {
            if (activeTimeout) window.clearTimeout(activeTimeout);
            activeTimeout = null;
            reject(error || new Error('Cancelled'));
            reset();
        };

        reset();
        return debouncedFn;
    }

    const Vue = {
        extend: component => {
            if (window.Vue) return window.Vue.extend(component);
            return function Vue() {
                throw new Error(`Trying to insantiate ${component.name || 'Vue'}, but Vue isn't loaded.`);
            }
        }
    };

    const TemplateDataPropsMixin = {
        beforeCreate() {
            const el = document.querySelector(this.$options.el);
            this.$options.propsData = {
                ...el.dataset,
                ...this.$options.propsData,
            }
        }
    };

    const FormSubmit = Vue.extend({
        name: 'FormSubmit',
        mixins: [TemplateDataPropsMixin],
        template: `
<button
  class="icon"
  @click="onClick"
></button>`,
        props: ['form',],
        methods: {
            async onClick() {
                const form = typeof this.form === 'string' ? document.getElementById(this.form) : this.form;
                const formData = new FormData(form);
                const action = form.action;
                const method = form.method;
                const options = {
                    method: method,
                    body: formData,
                    headers: {
                        Accept: 'application/json'
                    },
                };
                const request = rest(action, options);
                const response = await request.then(r => r.json());
                if (response.success)
                    window.location = response.location;
                else
                    Object.keys(response.errors).forEach(error => this.$emit(error, response.errors[error]));
            }
        }
    });

    window.recipyUtil = {
        ownProps,
        tid,
        b64toBlob,
        rest,
        post,
        postJSON,
        getCookie,
        debounce,
        TemplateDataPropsMixin,
        FormSubmit,
    }
})();
