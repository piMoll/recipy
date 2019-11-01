'use strict';

(function () {
    const debounce = window.recipyUtil.debounce;

    const RecipeTag = Vue.extend({
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
    });

    const SearchWidget = Vue.extend({
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
          :key="tag.id"
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
                required: false,
                default: '',
            },
            endpoint: {
                type: String,
                required: true,
            },
            recipes: {
                type: Array,
                required: false,
                default() {return [];},
            },
            doRouting: {
                type: Boolean,
                required: false,
                default: false,
            },
        },
        data() {
            return {
                searchString: this.search_string,
                tags_: this.tags.slice(),
                recipes_: this.recipes,
                fetch: null,
                skipSubmit: false,
                delay: 400,
            }
        },
        created() {
            this.submit = debounce(this.submit, this.delay);

            if (this.doRouting) {
                window.addEventListener('popstate', ({state}) => {
                    this.skipSubmit = true;
                    this.searchString = state.searchString;
                    this.tags_ = state.tags_;
                    this.$emit(this.$options.NEW_RESULT, state.recipes_);
                });

                history.replaceState(...this.getHistoryState());
            }
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
                this.$emit(SearchWidget.options.NEW_RESULT, this.recipes_);

                if (this.doRouting)
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

        NEW_RESULT: 'new-result',
    });

    const Recipe = Vue.extend({
        name: 'Recipe',
        template: `
<div class="recipe-list-gutter">
    <div class="recipe-list-item">
        <a
          :href="model.url"
          :title="model.title"
          class="recipe-list-link"
          @click="$emit('click', $event, model)"
        >
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
                      :key="tag.id"
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
    });

    const RecipeList = Vue.extend({
        name: 'RecipeList',
        template: `
<div class="gutter search-results">
    <div class="recipe-list">
        <div class="recipe-list-overflow">
            <template v-for="recipe in recipes"">
                <slot :recipes="recipes" :recipe="recipe">
                    <Recipe :key="recipe.id" :model="recipe" @click="recipeClicked" :class="recipeClass(recipe)"/>
                </slot>
            </template>
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
                default() {return [];},
            },
        },
        methods: {
            setItems(newItems) {
                this.$props.recipes = newItems;
            },
            consume(searchWidget) {
                searchWidget.$on(SearchWidget.options.NEW_RESULT, this.setItems);
            },
            recipeClicked() {},
            recipeClass(recipe) {},
        },
    });

    window.recipeSearch = {
        SearchWidget,
        RecipeList,
        Recipe,
    };
})();
