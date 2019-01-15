<template>
  <div>
    <v-autocomplete
      data-cy="entity-search-field"
      v-bind:label="
        location ? $t('events.event-location') : $t('actions.search-people')
      "
      prepend-icon="search"
      :items="entities"
      :loading="isLoading"
      v-bind:value="value"
      v-on:input="setSelected"
      :search-input.sync="searchInput"
      v-validate="'required'"
      v-bind:error-messages="errors.collect('location')"
      return-object
      :filter="customFilter"
      color="secondary"
    >
      <template slot="selection" slot-scope="data">
        {{ getEntityDescription(data.item, 100) }}
      </template>
      <template slot="item" slot-scope="data">
        {{ getEntityDescription(data.item) }}
      </template>
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
      descriptionLimit: 50,
      entities: [],
      searchInput: "",
      isLoading: false
    };
  },
  methods: {
    setSelected(entity) {
      this.$emit("input", entity);
    },

    getEntityDescription(entity, letterLimit=this.descriptionLimit) {
      if (!entity) return;
      let entityDescriptor = "";
      if (this.location) {
        entityDescriptor =
          entity.description +
          ", " +
          entity.address.address +
          ", " +
          entity.address.city;
      } else if (this.person) {
        entityDescriptor = entity.firstName + " " + entity.lastName;
      }

      if (entityDescriptor.length > letterLimit) {
        entityDescriptor = entityDescriptor.substring(0, letterLimit) + "...";
      }
      return entityDescriptor;
    },

    customFilter(item, queryText) {
      const itemDesc = this.getEntityDescription(item).toLowerCase();
      const searchText = queryText.toLowerCase();
      return itemDesc.indexOf(searchText) > -1;
    }
  },

  mounted() {
    //TODO use search-input.sync to avoid making a huge request here
    this.isLoading = true;
    var endpoint = this.location
      ? "/api/v1/places/locations"
      : "/api/v1/people/persons";
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
