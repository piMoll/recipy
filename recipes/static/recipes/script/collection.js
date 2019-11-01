(function () {
    const {ownProps} = window.recipyUtil;

    const TextInput = Vue.extend({
        name: 'TextInput',
        template: `<input :placeholder="placeholder" :id="id" :class="klass" :type="type" :value="value" @input="$emit('input', $event.target.value)">`,
        props: {
            type: {
                default: 'text',
                type: String,
            },
            value: null,
            id: null,
            klass: null,
            placeholder: null,
        },
    });

    const CollectionForm = Vue.extend({
        name: 'CollectionForm',
        template: `
<form method="post" :action="action">
    <input type="hidden" name="id" :value="collection.id" v-if="collection.id">
    <input type="hidden" name="name" :value="collection.name">

    <input
      v-for="item in itemList"
      type="hidden"
      name="recipes"
      :value="item.id"
    >
</form>
`,
        props: {
            collection: {
                type: Object,
                required: false,
                default() {
                    return {
                        name: '',
                        recipes: [],
                    };
                },
            },
            action: {
                type: String,
                required: false,
            }
        },
        data() {
            return {
                items: {},
            };
        },
        computed: {
            itemList() {
                return ownProps(this.collection.recipes).sort((l, r) => l.id - r.id);
            },
        },
        methods: {
            setName(value) {
                this.collection.name = value;
            },
            toggle(model) {
                if (model.id in this.collection.recipes) this.$delete(this.collection.recipes, model.id);
                else this.$set(this.collection.recipes, model.id, model);
            },
            form() {
                return this.$el;
            },
            hasRecipe(model) {
                return model.id in this.collection.recipes;
            }
        },
    });

    window.collectionForm = {
        TextInput,
        CollectionForm,
    };
})();