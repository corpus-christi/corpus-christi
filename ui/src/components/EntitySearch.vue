<template>
  <div>
    <v-autocomplete
      data-cy="entity-search-field"
      v-bind:label="
        location ? $t('events.event-location') : $t('actions.search-people')
      "
      prepend-icon="search"
      :items="items"
      :loading="isLoading"
      v-model="selected"
      :search-input.sync="searchInput"
      v-validate="'required'"
      v-bind:error-messages="errors.collect('location')"
      return-object
      item-text="Description"
    >
    </v-autocomplete>
  </div>
</template>

<script>
export default {
  name: "EntitySearch",
  props: {
    location: Boolean,
    person: Boolean,
    value: Object,
    searchEndpoint: String
  },
  data() {
    return {
      entities: [],
      selected: "",
      searchInput: "",
      isLoading: false
    };
  },
  watch: {
    searchInput(val) {
      this.isLoading = true;
      this.$http
        .get(this.searchEndpoint + "?q=" + val)
        .then(resp => {
          this.entities = resp.data;
          this.isLoading = false;
        })
        .catch(error => {
          console.log(error);
          this.isLoading = false;
        });
    },
    selected(entity) {
      this.setSelected(entity);
    },

    value(entity) {
      this.selected = entity;
      this.setSelected(entity);
    }
  },
  computed: {
    items() {
      var descriptionLimit = 60;
      return this.entities.map(entity => {
        var entityDescriptor;
        if (this.location)
          entityDescriptor =
            entity.name + ", " + entity.address + ", " + entity.city;
        else if (this.person)
          entityDescriptor = entity.first_name + " " + entity.last_name;
        const Description =
          entityDescriptor.length > this.descriptionLimit
            ? entityDescriptor.slice(0, this.descriptionLimit) + "..."
            : entityDescriptor;
        return Object.assign({}, entity, { Description });
      });
    }
  },
  methods: {
    setSelected(entity) {
      this.$emit("input", entity);
    }
  }
};
</script>
