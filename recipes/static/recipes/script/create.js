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

    const {ContainerMixin, ElementMixin, SlickList, HandleDirective} = window.VueSlicksort;

    const shouldCancelStart = ContainerMixin.props.shouldCancelStart.default;
    function isTouch(event) {
        return (event.type === 'touchstart') || shouldCancelStart(event);
    }
    ContainerMixin.props.shouldCancelStart.default = isTouch;

    const TemplateDataPropsMixin = {
        beforeCreate() {
            const el = document.querySelector(this.$options.el);
            this.$options.propsData = {
                ...el.dataset,
                ...this.$options.propsData,
            }
        }
    };

    const ErrorPopup = {
        template: `
<div class="error-popup" v-if="hasError" @click="remove">
    {{message}}
</div>
`,
        props: {
            errors: {
                default: () => ({})
            },
            field: null,
        },
        computed: {
            hasError() {
                return this.field in this.errors;
            },
            message() {
                return this.hasError ? this.errors[this.field].join(' ') : '';
            }
        },
        methods: {
            remove() {
                this.$delete(this.errors, this.field);
            }
        }
    };
    Vue.component('ErrorPopup', ErrorPopup);

    const Ingredient = {
        mixins: [ElementMixin],
        directives: {handle: HandleDirective},
        template: `
<div class="create-ingredient flex-row" v-show="!deleted">
    <div class="ingredient-delete flex-special flex-item">
        <input type="hidden" :name="fieldname('DELETE')" v-if="deleted" value="True">
        <label v-handle @click="deleteThis"></label>
    </div>
    
    <div class="md-text-input flex-40 flex-item">
        <input type="text" :name="fieldname('quantity')" :value="model.quantity" maxlength="255" @input="e => updateQuantity(e.target.value)">
        <label :for="fieldname('quantity')">Menge</label>
        <ErrorPopup :errors="model.errors" field="quantity" />
    </div>
    <div class="md-text-input flex-60 flex-item">
        <input type="text" :name="fieldname('name')" :value="model.name" maxlength="255" @input="e => updateName(e.target.value)">
        <label :for="fieldname('name')">Name</label>
        <ErrorPopup :errors="model.errors" field="name" />
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
            },
        },
        data() {
            return {deleted: false,};
        },
        computed: {
            fieldname() {
                if (this.model.isMock) return () => '';
                return field => `ingredient_set-${this.model.form}-${field}`;
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
                if (this.model.isMock) {
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
        mixins: [ElementMixin],
        template: `
<div class="ingredient-group">
    <div class="flex-row">
        <div class="ingredient-handle flex-special flex-item">
            <label></label>
        </div>
        
        <div class="md-text-input ingredient-group-name flex-100">
            <label for="id">Zwischenschritt</label>
            <input :id="id" class="ingredient-group-input" type="text" :value="group" @input="e => updateGroup(e.target.value)">
        </div>
    </div>
    
    <SlickList
      :value="items"
      axis="y"
      :distance="10"
      lockAxis="y"
      lockToContainerEdges
      lockOffset="0%"
      @input="changeIngredientOrder"
      :useDragHandle="true"
    >
        <Ingredient
          v-for="(model, index) in mockedList"
          :key="model.tid"
          :index="index"
          :collection="group.tid"
          :model="model"
          :disabled="model.isMock"
        ></Ingredient>
    </SlickList>
</div>`,
        components: {Ingredient, SlickList},
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
                    this.$root.createGroup(''); // create a new, empty group, because this one isn't the unnamed one anymore
                }
                this.$root.groups[this.tid].name = value.toLocaleUpperCase();
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
                    isMock: true,
                }
            },
            changeIngredientOrder(newOrder) {
                const items = this.$root.items;
                let orderItem = 0;
                newOrder.forEach(itemOrder => {
                    const item = items[itemOrder.tid];
                    if (!item) return;
                    item.order_item = ++orderItem;
                });
                this.$root.reorderItems();
            },
        }
    };

    const IngredientFormset = {
        name: 'IngredientFormset',
        template: `
<div class="ingredient-form flex-50 flex-item">
    <input type="hidden" name="ingredient_set-TOTAL_FORMS" :value="totalForms">

    <SlickList
      :value="groupedItems"
      axis="y"
      :distance="10"
      lockAxis="y"
      lockToContainerEdges
      lockOffset="0%"
      @input="changeGroupOrder"
    >
        <IngredientGroup
          v-for="(group, index) in groupedItems"
          :key="group.tid"
          :index="index"
          collection="groups"
          :group="group.group"
          :tid="group.tid"
          :items="group.items"
        ></IngredientGroup>
    </SlickList>
</div>`,
        components: {
            IngredientGroup,
            Ingredient,
            SlickList,
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
                console: window.console,
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
                    errors: {},
                });
                this.reorderItems();
            },
            createGroup(name) {
                const groupTid = tid();
                this.$set(this.groups, groupTid, {
                    name,
                    tid: groupTid,
                    order: Object.keys(this.groups).length,
                    isMock: true,
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
                        errors: {},
                    };
                });
                if (!('' in groupsInverse))
                    groupsInverse[''] = {tid: tid(), order: order_group++};
                const groups = Object.keys(groupsInverse).reduce((groups, group) => {
                    groups[groupsInverse[group].tid] = {
                        name: group,
                        tid: groupsInverse[group].tid,
                        order: groupsInverse[group].order,
                        isMock: true,
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
            changeGroupOrder(newOrder) {
                let order = 0;
                newOrder.forEach(groupOrder => {
                    const group = this.groups[groupOrder.tid];
                    if (!group) return;
                    group.order = order++;
                });
                this.reorderItems();
            },
            renumberForms() {
                let forms = 0;
                ownProps(this.items).forEach(item => {
                    if (!item.id) item.form = this.initialForms + forms++;
                });
            },
            isIngredientComponent(target) {
                console.log(target);
                return false;
            },
            showErrors(errors) {
                const items = {};
                ownProps({...this.items})
                    .forEach(item => {
                        items[item.form] = item;
                    });
                errors.forEach((formData, form) => {
                    const item = items[form];
                    item.errors = formData;
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
        mixins: [ElementMixin],
        template: `
<div class="create-direction flex-row" v-show="!deleted">
    <div class="direction-delete flex-special">
        <input type="hidden" :name="fieldname('DELETE')" v-if="deleted" value="True">
        <label @click="deleteThis"></label>
    </div>

    <div class="md-text-input flex-40 flex-item">
        <textarea
          :name="fieldname('description')"
          cols="40" rows="10"
          @input="e => updateDescription(e.target.value)"
          ref="textarea"
          :style="{height: height}"
        >{{ model.description }}</textarea>
        <label :for="fieldname('description')">Schritt</label>
        <ErrorPopup :errors="model.errors" field="description" />
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
                if (this.model.isMock) return () => '';
                return field => `direction_set-${this.model.form}-${field}`;
            },
        },
        methods: {
            updateDescription(value) {
                this.realize();
                this.$root.items[this.model.tid].description = value;
                this.adjustHeight();
            },
            realize() {
                if (this.model.isMock) {
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
                const border = 2;

                const textarea = this.$refs.textarea;
                this.$nextTick(() => {
                    const scrollHeight = textarea.scrollHeight;
                    this.height = `${scrollHeight + border}px`;
                });
                this.height = '0px';
            },
        },
        mounted() {
            this.adjustHeight();
        }
    };

    const DirectionFormset = {
        name: 'DirectionFormset',
        template: `
<div class="direction-form flex-50 flex-item">
    <input type="hidden" name="direction_set-TOTAL_FORMS" :value="totalForms">

    <SlickList
      :value="itemList"
      axis="y"
      :distance="10"
      lockAxis="y"
      lockToContainerEdges
      lockOffset="0%"
      @input="changeOrder"
    >
        <Direction
          v-for="(item, index) in itemList"
          :key="item.tid"
          :index="index"
          :disabled="item.isMock"
          :model="item"
        ></Direction>
    </SlickList>
</div>`,
        components: {
            Direction,
            SlickList,
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
                    errors: {},
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
                        errors: {},
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
                    isMock: true,
                }
            },
            renumberForms() {
                let forms = 0;
                ownProps(this.items).forEach(item => {
                    if (!item.id) item.form = this.initialForms + forms++;
                });
            },
            changeOrder(newOrder) {
                let step = 0;
                newOrder.forEach(orderItem => {
                    const item = this.items[orderItem.tid];
                    if (!item) return;
                    item.step = ++step;
                });
            },
            showErrors(errors) {
                const items = {};
                ownProps({...this.items})
                    .forEach(item => {
                        items[item.form] = item;
                    });
                errors.forEach((formData, form) => {
                    const item = items[form];
                    item.errors = formData;
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

    const Picture = {
        template: `
<div
  class="create-image-button"
  :class="{'add-picture': !picture.image}"
  v-show="!picture.deleted"
  @click="selectThis"
>
    <input type="hidden" :name="fieldname('order')" :value="picture.order">
    <input type="hidden" :name="fieldname('description')" :value="picture.description">
    <input type="hidden" :name="fieldname('id')" :value="picture.id">
    <input type="hidden" :name="fieldname('recipe')" :value="picture.recipe">
    <input type="hidden" :name="fieldname('ORDER')" :value="picture.order - 1">
    
    <input type="hidden" :name="fieldname('DELETE')" value="True" v-if="picture.deleted">
    
    <input
      type="file"
      :name="fieldname('image')"
      :id="fieldname('image')"
      v-if="!picture.id"
      v-show="false"
      accept="image/*"
      @change="realize"
      ref="fileinput"
      :data-tid="picture.tid"
    >
    <label :for="fieldname('image')" v-show="!picture.image"></label>

    <img :src="picture.image" v-show="picture.image">
    
    <div class="picture-delete" v-show="picture.image">
        <label @click="deleteThis"></label>
    </div>
</div>`,
        mixins: [ElementMixin],
        props: {
            picture: Object,
        },
        computed: {
            fieldname() {
                return (field) => (typeof this.picture.form !== 'undefined') ?
                    `picture_set-${this.picture.form}-${field}` : '';
            }
        },
        methods: {
            selectThis() {
                if (this.picture.image)
                    this.$root.selection = this.picture;
            },
            deleteThis() {
                if (this.picture.id) this.picture.deleted = true;
                else this.$delete(this.$root.newItems, this.picture.tid);
            },
            realize(e) {
                if (e.target.files && e.target.files[0])
                    this.$root.create(this.picture.tid, e.target.files[0]);
            }
        },
        mounted() {
            if (this.picture.file) {
                const input = this.$refs.fileinput;
                const transfer = new DataTransfer();
                transfer.items.add(this.picture.file);
                input.files = transfer.files;
                this.$delete(this.picture, 'file');
            }
        },
    };

    const PictureList = {
        template: `
<div class="scroll-wrap">
    <slot />
</div>`,
        mixins: [ContainerMixin],
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

    <div class="image" v-show="selection.image">
        <img :src="selection.image" alt="Siehe Beschreibung">
    </div>
    
    <div class="image-list">
        <PictureList
          :value="itemList"
          axis="x"
          :distance="10"
          lockAxis="x"
          lockToContainerEdges
          lockOffset="0%"
          @input="changeOrder"
        >
            <Picture
              v-for="(picture, index) in itemList"
              :picture="picture"
              :key="picture.tid"
              :index="index"
              :disabled="!picture.image"
            ></Picture>
        </PictureList>
    </div>
</div>`,
        components: {
            Picture, PictureList,
        },
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
        },
        methods: {
            create(tid, file) {
                const image = URL.createObjectURL(file);

                this.$set(this.newItems, tid, {
                    image,
                    description: '',
                    recipe: this.recipe,
                    id: '',
                    form: this.totalForms, // zero-indexed
                    order: this.totalForms + 1, // one-indexed
                    tid,
                    deleted: false,
                    errors: {},
                });
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
                        errors: {},
                    };

                    if (!model.id) {
                        const file = new File([b64toBlob(item.image.base64)], item.image.name, {type: item.image.type});
                        const image = URL.createObjectURL(file);
                        model.image = image;
                        model.file = file;
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
            changeOrder(newOrders) {
                let order = 0;
                newOrders.forEach(itemOrder => {
                    const item = this.items[itemOrder.tid] || this.newItems[itemOrder.tid];
                    if (!item) return;
                    item.order = ++order;
                })
            },
            showErrors(errors) {
                const items = {};
                ownProps({...this.items, ...this.newItems})
                    .forEach(item => {
                        items[item.form] = item;
                    });
                errors.forEach((formData, form) => {
                    const item = items[form];
                    item.errors = formData;
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

    const FormSubmit = {
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
                const form = document.getElementById(this.form);
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
                const request = fetch(action, options);
                const response = await request.then(r => r.json());
                if (response.success)
                    window.location = response.location;
                else
                    Object.keys(response.errors).forEach(error => this.$emit(error, response.errors[error]));
            }
        }
    };

    window.recipeCreate = {
        IngredientFormset: Vue.extend(IngredientFormset),
        DirectionFormset: Vue.extend(DirectionFormset),
        PictureFormset: Vue.extend(PictureFormset),
        FormSubmit: Vue.extend(FormSubmit),
    };
})();
