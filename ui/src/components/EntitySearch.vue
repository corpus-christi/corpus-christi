<template>
  <div>
    <v-autocomplete
      data-cy="entity-search-field"
      v-bind:label="
        location ? $t('events.event-location') : $t('actions.search-people')
      "
      prepend-icon="search"
<<<<<<< HEAD
      :items="entities"
=======
      :items="items"
>>>>>>> feature/courses-36_create-a-course-offering
      :loading="isLoading"
      v-bind:value="value"
      v-on:input="setSelected"
      :search-input.sync="searchInput"
      v-validate="'required'"
      v-bind:error-messages="errors.collect('location')"
      return-object
<<<<<<< HEAD
      :filter="customFilter"
      color="secondary"
    >
      <template slot="selection" slot-scope="data">
        {{ getEntityDescription(data.item, 100) }}
      </template>
      <template slot="item" slot-scope="data">
        {{ getEntityDescription(data.item) }}
      </template>
=======
      item-text="Description"
    >
>>>>>>> feature/courses-36_create-a-course-offering
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
<<<<<<< HEAD
      descriptionLimit: 50,
=======
      descriptionLimit: 60,
>>>>>>> feature/courses-36_create-a-course-offering
      entities: [],
      searchInput: "",
      isLoading: false
    };
  },
<<<<<<< HEAD

=======
  watch: {
    value(entity) {
      this.initializeSelected(entity);
    }
  },
  computed: {
    items() {
      return this.entities.map(entity => {
        var entityDescriptor;
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
        const Description =
          entityDescriptor.length > this.descriptionLimit
            ? entityDescriptor.slice(0, this.descriptionLimit) + "..."
            : entityDescriptor;
        return Object.assign({}, entity, { Description });
      });
    }
  },
>>>>>>> feature/courses-36_create-a-course-offering
  methods: {
    setSelected(entity) {
      this.$emit("input", entity);
    },

<<<<<<< HEAD
    getEntityDescription(entity, letterLimit=this.descriptionLimit) {
      if (!entity) return;
      let entityDescriptor = "";
=======
    initializeSelected(entity) {
      if (!entity) return;
      this.selected = entity;
      var entityDescriptor;
>>>>>>> feature/courses-36_create-a-course-offering
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
<<<<<<< HEAD

      if (entityDescriptor.length > letterLimit) {
        entityDescriptor = entityDescriptor.substring(0, letterLimit) + "...";
      }
      return entityDescriptor;
    },

    customFilter(item, queryText) {
      const itemDesc = this.getEntityDescription(item).toLowerCase();
      const searchText = queryText.toLowerCase();
      return itemDesc.indexOf(searchText) > -1;
=======
      const Description =
        entityDescriptor.length > this.descriptionLimit
          ? entityDescriptor.slice(0, this.descriptionLimit) + "..."
          : entityDescriptor;
      this.selected["Description"] = Description;
>>>>>>> feature/courses-36_create-a-course-offering
    }
  },

  mounted() {
<<<<<<< HEAD
    //TODO use search-input.sync to avoid making a huge request here
=======
>>>>>>> feature/courses-36_create-a-course-offering
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
