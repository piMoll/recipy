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

    const Ingredient = {
        template: `
<div class="create-ingredient flex-row" v-show="!deleted">
    <div class="ingredient-delete">
        <input type="hidden" :name="fieldname('DELETE')" v-if="deleted" value="True">
        <label @click="deleteThis"></label>
    </div>
    
    <div class="md-text-input flex-40">
        <input type="text" :name="fieldname('quantity')" :value="model.quantity" maxlength="255" @input="e => updateQuantity(e.target.value)">
        <label :for="fieldname('quantity')">Menge</label>
    </div>
    <div class="md-text-input flex-60">
        <input type="text" :name="fieldname('name')" :value="model.name" maxlength="255" @input="e => updateName(e.target.value)">
        <label :for="fieldname('name')">Name</label>
    </div>
    
    <input type="hidden" :name="fieldname('ORDER')" :value="model.order_item - 1">
    
    <input type="hidden" :name="fieldname('group')" :value="model.group.name">

    <input type="hidden" :name="fieldname('order_item')" :value="model.order_item">
    
    <input type="hidden" :name="fieldname('id')" :value="model.id">

    <input type="hidden" :name="fieldname('recipe')" :value="model.recipe">
</div>`,
        props: {
            model: {
                type: Object,
                required: true,
            }
        },
        data() {
            return {deleted: false,};
        },
        computed: {
            fieldname() {
                if (this.isMock) return () => '';
                return field => `ingredient_set-${this.model.form}-${field}`;
            },
            isMock() {
                return typeof this.$root.items[this.model.tid] === 'undefined';
            },
        },
        methods: {
            updateQuantity(value) {
                this.realize();
                this.$root.items[this.model.tid].quantity = value;
            },
            updateName(value) {
                this.realize();
                this.$root.items[this.model.tid].name = value;
            },
            realize() {
                if (this.isMock) {
                    this.$root.create(this.model.tid, this.model.group.tid);
                }
            },
            deleteThis() {
                if (this.model.id)
                    this.deleted = !this.deleted;
                else
                    this.$delete(this.$root.items, this.model.tid);
            },
        }
    };

    const IngredientGroup = {
        template: `
<div class="ingredient-group">
    <div class="md-text-input ingredient-group-name">
        <label for="id">Zwischenschritt</label>
        <input :id="id" class="ingredient-group-input" type="text" :value="group" @input="e => updateGroup(e.target.value)">
    </div>
    
    <div>
        <Ingredient
          v-for="model in mockedList"
          :key="model.tid"
          :model="model"
        ></Ingredient>
    </div>
</div>`,
        components: {
            Ingredient,
        },
        props: {
            tid: null,
            group: null,
            items: null,
        },
        computed: {
            id() {
                return `group-input-${this.tid}`
            },
            mockedList() {
                return this.items.concat(this.mockModel());
            }
        },
        methods: {
            updateGroup(value) {
                if (this.group === '' && value !== '') {
                    this.$root.createGroup('');
                }
                this.$root.groups[this.tid].name = value;
            },
            mockModel() {
                return {
                    name: '',
                    quantity: '',
                    group: {
                        name: this.group,
                        tid: this.tid,
                    },
                    tid: tid(),
                }
            },
        }
    };

    const IngredientFormset = {
        name: 'IngredientFormset',
        template: `
<div class="ingredient-form flex-50">
    <input type="hidden" name="ingredient_set-TOTAL_FORMS" :value="totalForms">

    <IngredientGroup
      v-for="group in groupedItems"
      :items="group.items"
      :group="group.group"
      :tid="group.tid"
      :key="group.tid"
    ></IngredientGroup>
</div>`,
        components: {
            IngredientGroup,
        },
        props: {
            initData: Array,
        },
        data() {
            return {
                items: {},
                groups: {},
                recipe: null,
                initialForms: null,
            }
        },
        computed: {
            groupedItems() {
                const itemGroups = {};
                ownProps(this.items).forEach(item => {
                    const groupTid = item.group;
                    if (!(groupTid in itemGroups)) {
                        itemGroups[groupTid] = [];
                    }
                    itemGroups[groupTid].push({...item, group: this.groups[groupTid],});
                });

                const groupedItems = [];
                ownProps(this.groups).sort((a, b) => a.order - b.order).forEach(group => {
                    const items = itemGroups[group.tid] || [];
                    groupedItems.push({
                        tid: group.tid,
                        group: group.name,
                        items: items.sort((a, b) => a.order_item - b.order_item)
                    });
                });

                return groupedItems;
            },
            totalForms() {
                return Object.keys(this.items).length;
            },
        },
        methods: {
            create(tid, groupTid) {
                this.$set(this.items, tid, {
                    quantity: '',
                    name: '',
                    group: groupTid,
                    recipe: this.recipe,
                    id: '',
                    order_item: 101,
                    form: 101,
                    tid,
                });
                this.reorderItems();
            },
            createGroup(group) {
                const groupTid = tid();
                this.$set(this.groups, groupTid, {
                    group,
                    tid: groupTid,
                    order: Object.keys(this.groups).length,
                })
            },
            initialize(initData) {
                const groupsInverse = {};
                const items = {};
                let recipe = null;
                let order_item = 0;
                let order_group = 0;
                initData.sort((a, b) => Number(a.order_item) - Number(b.order_item)).forEach(item => {
                    const itemTid = tid();

                    if (!(item.group in groupsInverse))
                        groupsInverse[item.group] = {tid: tid(), order: order_group++};

                    if (recipe !== null && item.recipe !== recipe)
                        throw RangeError('Not all ingredients belong to the same recipe');
                    if (recipe === null)
                        recipe = item.recipe;

                    order_item += 1;
                    items[itemTid] = {
                        quantity: item.quantity || '',
                        name: item.name,
                        group: groupsInverse[item.group].tid,
                        recipe,
                        id: item.id,
                        form: order_item - 1, // zero-indexed
                        order_item: order_item , // one-indexed
                        tid: itemTid,
                    };
                });
                if (!('' in groupsInverse))
                    groupsInverse[''] = {tid: tid(), order: order_group++};
                const groups = Object.keys(groupsInverse).reduce((groups, group) => {
                    groups[groupsInverse[group].tid] = {
                        name: group,
                        tid: groupsInverse[group].tid,
                        order: groupsInverse[group].order,
                    };
                    return groups;
                }, {});

                this.groups = groups;
                this.items = items;
                this.recipe = recipe;
                this.initialForms = order_item;
            },
            reorderItems() {
                const itemGroups = {};
                ownProps(this.items).forEach(item => {
                    const groupTid = item.group;
                    if (!(groupTid in itemGroups)) {
                        itemGroups[groupTid] = [];
                    }
                    itemGroups[groupTid].push(item);
                });

                let order = 0;
                ownProps(this.groups).sort((a, b) => a.order - b.order).forEach(group => {
                    const items = itemGroups[group.tid] || [];
                    items.sort(((a, b) => a.order_item - b.order_item)).forEach(item => item.order_item = ++order);
                });
            },
            renumberForms() {
                let forms = 0;
                ownProps(this.items).forEach(item => {
                    if (!item.id) item.form = this.initialForms + forms++;
                });
            },
        },
        watch: {
            totalForms(nu) {
                if (nu > this.initialForms) this.renumberForms();
            },
        },
        created() {
            this.initialize(this.initData);
        },
    };

    const Direction = {
        template: `
<div class="create-direction" v-show="!deleted">
    <div class="direction-delete">
        <input type="hidden" :name="fieldname('DELETE')" v-if="deleted" value="True">
        <label @click="deleteThis"></label>
    </div>

    <div class="md-text-input flex-40">
        <textarea
          :name="fieldname('description')"
          cols="40" rows="10"
          @input="e => updateDescription(e.target.value)"
          ref="textarea"
          :style="{height: height}"
        >{{ model.description }}</textarea>
        <label :for="fieldname('description')">Schritt</label>
    </div>
    
    <input type="hidden" :name="fieldname('ORDER')" :value="model.step - 1">
    
    <input type="hidden" :name="fieldname('step')" :value="model.step">

    <input type="hidden" :name="fieldname('id')" :value="model.id">

    <input type="hidden" :name="fieldname('recipe')" :value="model.recipe">
</div>`,
        props: {
            model: {
                type: Object,
                required: true,
            },
        },
        data() {
            return {deleted: false, height: '0px',};
        },
        computed: {
            fieldname() {
                if (this.isMock) return () => '';
                return field => `direction_set-${this.model.form}-${field}`;
            },
            isMock() {
                return typeof this.$root.items[this.model.tid] === 'undefined';
            },
        },
        methods: {
            updateDescription(value) {
                this.realize();
                this.$root.items[this.model.tid].description = value;
                this.adjustHeight();
            },
            realize() {
                if (this.isMock) {
                    this.$root.create(this.model.tid);
                }
            },
            deleteThis() {
                if (this.model.id)
                    this.deleted = !this.deleted;
                else
                    this.$delete(this.$root.items, this.model.tid);
            },
            adjustHeight() {
                const textarea = this.$refs.textarea;
                this.height = '0px';
                this.$nextTick(() => {
                    const scrollHeight = textarea.scrollHeight - 20;
                    this.height = `calc(${scrollHeight}px + 20px + 2px)`;
                });
            },
        },
        mounted() {
            this.adjustHeight();
        }
    };

    const DirectionFormset = {
        name: 'DirectionFormset',
        template: `
<div class="direction-form flex-50">
    <input type="hidden" name="direction_set-TOTAL_FORMS" :value="totalForms">

    <Direction
      v-for="item in itemList"
      :key="item.tid"
      :model="item"
    ></Direction>
</div>`,
        components: {
            Direction,
        },
        props: {
            initData: Array,
        },
        data() {
            return {
                items: {},
                recipe: null,
                initialForms: null,
            }
        },
        computed: {
            itemList() {
                return ownProps(this.items).sort((a, b) => a.step - b.step).concat(this.mockModel())
            },
            totalForms() {
                return Object.keys(this.items).length;
            },
        },
        methods: {
            create(tid) {
                this.$set(this.items, tid, {
                    description: '',
                    recipe: this.recipe,
                    id: '',
                    form: this.totalForms,
                    step: this.totalForms + 1,
                    tid,
                });
            },
            initialize(initData) {
                const items = {};
                let recipe = null;
                let step = 0;
                initData.sort((a, b) => Number(a.step) - Number(b.step)).forEach(item => {
                    const itemTid = tid();

                    if (recipe !== null && item.recipe !== recipe)
                        throw RangeError('Not all ingredients belong to the same recipe');
                    if (recipe === null)
                        recipe = item.recipe;

                    step += 1;
                    items[itemTid] = {
                        description: item.description,
                        recipe: item.recipe,
                        id: item.id,
                        form: step - 1, // zero-indexed
                        step: step, // one-indexed
                        tid: itemTid,
                    }
                });
                this.items = items;
                this.recipe = recipe;
                this.initialForms = step;
            },
            mockModel() {
                return {
                    description: '',
                    tid: tid(),
                }
            },
            renumberForms() {
                let forms = 0;
                ownProps(this.items).forEach(item => {
                    if (!item.id) item.form = this.initialForms + forms++;
                });
            },
        },
        watch: {
            totalForms(nu) {
                if (nu > this.initialForms) this.renumberForms();
            },
        },
        created() {
            this.initialize(this.initData);
        },
    };

    /**
     * Pictures can have the following states:
     * - Currently existing in DB: picture.id && picture.image
     * - Just added: !picture.id && picture.image
     * - An empty FileInput: !picture.id && !picture.image
     */
    const PictureFormset = {
        name: 'PictureFormset',
        template: `
<div class="image create-image">
    <input type="hidden" name="picture_set-TOTAL_FORMS" :value="totalForms">
    <input type="hidden" name="picture_set-INITIAL_FORMS" :value="initialForms">

    <div class="image">
        <img :src="selection.image" alt="Siehe Beschreibung">
    </div>
    
    <div class="image-list">
        <div class="scroll-wrap">
            <div
              class="button"
              :class="{'add-picture': !picture.image}"
              v-for="picture in itemList"
              :key="picture.tid"
              v-show="!picture.deleted"
            >
                <input type="hidden" :name="fieldname(picture, 'order')" :value="picture.order">
                <input type="hidden" :name="fieldname(picture, 'description')" :value="picture.description">
                <input type="hidden" :name="fieldname(picture, 'id')" :value="picture.id">
                <input type="hidden" :name="fieldname(picture, 'recipe')" :value="picture.recipe">
                <input type="hidden" :name="fieldname(picture, 'ORDER')" :value="picture.order - 1">
                
                <input type="hidden" :name="fieldname(picture, 'DELETE')" value="True" v-if="picture.deleted">
                
                <input
                  type="file"
                  :name="fieldname(picture, 'image')"
                  :id="fieldname(picture, 'image')"
                  v-if="!picture.id"
                  v-show="false"
                  accept="image/*"
                  @change="e => create(picture.tid, e.target)"
                  ref="fileinput"
                  :data-tid="picture.tid"
                >
                <label :for="fieldname(picture, 'image')" v-show="!picture.image"></label>
            
                <img :src="picture.image" @click="() => selection = picture" v-show="picture.image">
                
                <div class="picture-delete" v-show="picture.image">
                    <label @click="() => deletePicture(picture)"></label>
                </div>
            </div>
        </div>
    </div>
</div>`,
        props: {
            initData: Array,
        },
        data() {
            return {
                items: {},
                newItems: {},
                initialForms: null,
                recipe: null,
                selection: {},
            };
        },
        computed: {
            itemList() {
                return ownProps(this.items)
                    .concat(ownProps(this.newItems))
                    .sort((a, b) => a.order - b.order)
                    .concat(this.mockModel())
            },
            totalForms() {
                return Object.keys(this.items).length + Object.keys(this.newItems).length;
            },
            fieldname() {
                return (picture, field) => (typeof picture.form !== 'undefined') ?
                    `picture_set-${picture.form}-${field}` : '';
            },
        },
        methods: {
            log: console.log.bind(console),
            create(tid, input) {
                if (!(input.files && input.files[0])) return;

                const image = URL.createObjectURL(input.files[0]);

                this.$set(this.newItems, tid, {
                    image,
                    description: '',
                    recipe: this.recipe,
                    id: '',
                    form: this.totalForms, // zero-indexed
                    order: this.totalForms + 1, // one-indexed
                    tid,
                    deleted: false,
                });
            },
            deletePicture(picture) {
                if (picture.id) picture.deleted = true;
                else this.$delete(this.newItems, picture.tid);
            },
            initialize(initData) {
                const items = {};
                const newItems = {};
                let recipe = null;
                let order = 0;
                initData.sort((a, b) => Number(a.order) - Number(b.order)).forEach(item => {
                    const itemTid = tid();

                    if (recipe !== null && item.recipe !== recipe)
                        throw RangeError('Not all ingredients belong to the same recipe');
                    if (recipe === null)
                        recipe = item.recipe;

                    order += 1;
                    const model = {
                        image: item.image,
                        description: item.description,
                        recipe: item.recipe,
                        id: item.id,
                        form: order - 1, // zero-indexed
                        order: order, // one-indexed
                        tid: itemTid,
                        deleted: false,
                    };
                    if (!model.id) {
                        const file = new File([b64toBlob(item.image.base64)], item.image.name, {type: item.image.type});
                        const image = URL.createObjectURL(file);
                        model.image = image;
                        newItems[itemTid] = model;
                        this.$nextTick(() => {
                            const input = this.$refs.fileinput.filter(ref => ref.dataset.tid === itemTid)[0];
                            const transfer = new DataTransfer();
                            transfer.items.add(file);
                            input.files = transfer.files;
                        });
                    }

                    (model.id ? items : newItems)[itemTid] = model;
                });
                this.items = items;
                this.newItems = newItems;
                this.recipe = recipe;
                this.initialForms = Object.keys(items).length;
            },
            mockModel() {
                return {
                    description: '',
                    tid: tid(),
                    form: this.totalForms,
                }
            },
            renumberForms() {
                let forms = 0;
                ownProps(this.newItems).forEach(item => {
                    if (!item.id) item.form = this.initialForms + forms++;
                });
            },
        },
        watch: {
            totalForms(nu) {
                if (nu > this.initialForms) this.renumberForms();
            },
        },
        created() {
            this.initialize(this.initData);
            this.selection = this.itemList[0];
        },
    };

    window.recipeCreate = {
        IngredientFormset: Vue.extend(IngredientFormset),
        DirectionFormset: Vue.extend(DirectionFormset),
        PictureFormset: Vue.extend(PictureFormset),
    };
})();
