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
      v-bind:value="value"
      v-on:input="setSelected"
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
      searchInput: "",
      isLoading: false
    };
  },
  watch: {
    value(entity) {
      this.initializeSelected(entity)
    },
  },
  computed: {
    items() {
      var descriptionLimit = 60;
      return this.entities.map(entity => {
        var entityDescriptor;
        if (this.location) {
          entityDescriptor = entity.description + ", " + entity.address.address + ", " + entity.address.city
        }
        else if (this.person) {
          entityDescriptor = entity.firstName + " " + entity.lastName;
        }
        const Description =
          entityDescriptor.length > this.descriptionLimit
            ? entityDescriptor.slice(0, this.descriptionLimit) + "..."
            : entityDescriptor;
        return Object.assign({}, entity, { Description });
      });
    },
  },
  methods: {
    setSelected(entity) {
      this.$emit("input", entity);
    },

    initializeSelected(entity) {
      if (!entity) return
      this.selected = entity
      var entityDescriptor;
      if (this.location) {
        entityDescriptor = entity.description + ", " + entity.address.address + ", " + entity.address.city
      }
      else if (this.person) {
        entityDescriptor = entity.firstName + " " + entity.lastName;
      }
      const Description =
      entityDescriptor.length > this.descriptionLimit
        ? entityDescriptor.slice(0, this.descriptionLimit) + "..."
        : entityDescriptor;
      this.selected['Description'] = Description
    }
  },

  mounted() {
    this.isLoading = true;
    var endpoint = (this.location) ? '/api/v1/places/locations' : '/api/v1/people/persons'
    this.$http
    .get(endpoint)
    .then(resp => {
      this.entities = resp.data;
      this.isLoading = false;
    })
    .catch(error => {
      console.log(error);
      this.isLoading = false;
    });
  }
};
</script>
