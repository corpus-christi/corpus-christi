<template>
    <div>
        <v-autocomplete 
        data-cy="entity-search-field"
        v-bind:label="$t('events.event-location')"
        prepend-icon="search"
        :items="items" 
        :loading="isLoading"
        v-model="selected" 
        :search-input.sync="searchInput"
        v-validate="'required'"
        v-bind:error-messages="errors.collect('location')"
        return-object
        item-text="Description">
        </v-autocomplete>
    </div>
</template>

<script>
export default {
    name: "EntitySearch",
    props: {
        location: Boolean,
        people: Boolean,
        searchEndpoint: String
    },
    data() {
        return {
            entities: [],
            selected: "",
            searchInput: "",
            isLoading: false,
        };
    },

    watch: {
        searchInput(val) {
            this.isLoading = true
            this.$http.get(this.searchEndpoint).then(resp => {
                this.entities = resp.data;
                this.isLoading = false
            })
            .catch(error => {
                console.log(error)
                this.isLoading = false
            }) 
        },
        selected(entity) {
            this.setSelected(entity)
        }
    },

    computed: { 
        items() {
            if(this.location) {
                var descriptionLimit = 60
                return this.entities.map(entity => {
                    var fullAddress = entity.name + ', ' + entity.address + ', ' + entity.city
                    const Description = fullAddress.length > this.descriptionLimit
                        ? fullAddress.slice(0, this.descriptionLimit) + '...'
                        : fullAddress
                    return Object.assign({}, entity, { Description })
                })
            }
        }
    },

    methods: {
        setSelected(entity) {
            this.$emit("setLocation", entity.id);
        },

    }
}
</script>
