'use strict';

(function () {
    function ownProps(object) {
        return Object.keys(object).map(key => object[key]);
    }

    const MAX_32_BIT = Math.pow(2, 32);
    function tid() {
        const num = Math.floor(Math.random() * MAX_32_BIT);
        return ('00000000' + num.toString(16)).substr(-8);
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
                // this is somewhat incorrect, because this allows you to cancel beyond the specified delay
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

    const RecipeTag = {
        name: 'RecipeTag',
        template: `<span @click="click" class="tag" :style="{color: tag.font, 'background-color': tag.color}">{{tag.name}}</span>`,
        props: {
            tag: {
                type: Object,
                required: true,
            },
        },
        methods: {
            click() {
                this.$emit('click', this.tag);
            },
        },
    };

    const SearchWidget = {
        name: 'SearchWidget',
        template: `
<div class="recipe-search">
    <input
      class="search-string"
      type="text"
      placeholder="Nach Rezept, Zutat, etc. suchen"
      v-model="searchString"
    >

    <div class="search-tags">
        <RecipeTag
          v-for="tag in tags_"
          :tag="tag"
          :class="{'include-tag': tag.state === true, 'exclude-tag': tag.state === false}"
          @click="() => cycleTag(tag)"
        />
    </div>
</div>
`,
        components: {
            RecipeTag,
        },
        props: {
            tags: {
                type: Array,
                required: true,
            },
            search_string: {
                type: String,
                required: true,
            },
            endpoint: {
                type: String,
                required: true,
            },
            recipes: {
                type: Array,
                required: true,
            }
        },
        data() {
            return {
                searchString: this.search_string,
                tags_: this.tags.slice(),
                recipes_: this.recipes,
                fetch: null,
                skipSubmit: false,
            }
        },
        created() {
            this.submit = debounce(this.submit, 350);

            window.addEventListener('popstate', ({state}) => {
                this.skipSubmit = true;
                this.searchString = state.searchString;
                this.tags_ = state.tags_;
                this.$emit(this.$options.NEW_RESULT, state.recipes_);
            });

            history.replaceState(...this.getHistoryState());
        },
        methods: {
            cycleTag(tag) {
                const nextState = {
                    null: true,
                    true: false,
                    false: null,
                }[tag.state];
                tag.state = nextState;
            },
            indirectSubmit() {
                this.submit();
            },
            async submit() {
                if (this.skipSubmit) {
                    this.skipSubmit = false;
                    return;
                }

                const qs = this.querystring();
                if (!qs) return;

                const request = fetch(this.endpoint + '?' + qs);
                this.fetch = request;

                const response = await this.fetch;
                if (this.fetch !== request) return;

                const json = await response.json();
                this.recipes_ = json.recipes;
                this.$emit(this.$options.NEW_RESULT, this.recipes_);

                history.pushState(...this.getHistoryState());
            },
            querystring() {
                let tags = this.tags_
                    .filter(tag => tag.state !== null)
                    .map(tag => encodeURIComponent(`tag.${tag.name}`) + '=' + encodeURIComponent(tag.state));
                if (this.searchString) tags.push('search_string=' + encodeURIComponent(this.searchString));
                return tags.join('&');
            },
            getHistoryState() {
                return [
                    {
                        searchString: this.searchString,
                        tags_: this.tags_,
                        recipes_: this.recipes_,
                    },
                    'Rezeptsuche' + this.searchString ? `: ${this.searchString}` : '',
                    '?' + this.querystring(),
                ]
            },
        },
        watch: {
            tags_: {
                deep: true,
                handler: 'indirectSubmit',
            },
            searchString: 'indirectSubmit',
        },

        NEW_RESULT: 'NEW_RESULT',
    };

    const Recipe = {
        name: 'Recipe',
        template: `
<div class="recipe-list-gutter">
    <div class="recipe-list-item">
        <a :href="model.url"
           :title="model.title"
           class="recipe-list-link">
            <div class="recipe-list-image">
                    <img :src="model.thumbnail" :alt="model.title">
            </div>
            <div class="recipe-list-desc">
                <span class="recipe-list-name">
                    {{ model.title }}
                </span>
                <div class="recipe-list-tags">
                    <RecipeTag
                      v-for="tag in model.tags"
                      :tag="tag"
                      :style="{color: tag.font, 'background-color': tag.color}"
                    />
                </div>
            </div>
        </a>
   </div>
</div>
`,
        components: {
            RecipeTag,
        },
        props: {
            model: {
                type: Object,
                required: true,
            }
        }
    };

    const RecipeList = {
        name: 'RecipeList',
        template: `
<div class="gutter search-results">
    <div class="recipe-list">
        <div class="recipe-list-overflow">
            <Recipe
              v-for="recipe in recipes"
              :model="recipe"
            />
        </div>
    </div>
    <h3 v-show="this.recipes.length === 0">Keine Rezepte gefunden :(</h3>
</div>
`,
        components: {
            Recipe,
        },
        props: {
            recipes: {
                type: Array,
                required: false,
            },
        },
        methods: {
            setItems(newItems) {
                this.$props.recipes = newItems;
            },
        }
    };

    window.recipeSearch = {
        SearchWidget: Vue.extend(SearchWidget),
        RecipeList: Vue.extend(RecipeList),
    };
})();
