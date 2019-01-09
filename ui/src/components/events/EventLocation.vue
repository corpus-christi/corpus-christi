<template>
    <div>
        <v-autocomplete 
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
    name: "EventLocation",
    data() {
        return {
            locations: [],
            selected: "one",
            searchInput: "",
            isLoading: false,
        };
    },

    watch: {
        searchInput(val) {
            // console.log('Searching for ' + val + ' in locations')
            this.isLoading = true
            this.$http.get("http://localhost:3000/locations").then(resp => {
                this.locations = resp.data;
                this.isLoading = false
            })
            .catch(error => {
                console.log(error)
                this.isLoading = false
            })
        },
        selected(location) {
            this.setLocation(location)
        }
    },

    computed: { 
        items() {
            var descriptionLimit = 60
            return this.locations.map(loc => {
                const Description = loc.address.length > this.descriptionLimit
                    ? loc.address.slice(0, this.descriptionLimit) + '...'
                    : loc.address
                return Object.assign({}, loc, { Description })
            })
        }
    },

    methods: {
        setLocation(location) {
            this.$emit("setLocation", location.id);
        },

    }
}
</script>
