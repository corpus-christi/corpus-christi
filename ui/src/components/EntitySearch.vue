<template>
  <div>
    <v-autocomplete
      data-cy="entity-search-field"
      v-bind:label="getLabel"
      prepend-icon="search"
      :items="searchableEntities"
      :loading="isLoading"
      :value="value"
      v-on:input="setSelected"
      :search-input.sync="searchInput"
      v-bind:error-messages="errorMessages"
      return-object
      :filter="customFilter"
      :multiple="multiple"
      :value-comparator="compare"
      color="secondary"
      :disabled="disabled"
    >
      <template v-if="!multiple" slot="selection" slot-scope="data">
        {{ getEntityDescription(data.item, 100) }}
      </template>
      <template slot="item" slot-scope="data">
        <span v-if="multiple && selectionContains(data.item)">
          <v-icon>clear</v-icon>
        </span>
        {{ getEntityDescription(data.item) }}
      </template>
    </v-autocomplete>
    <template v-if="multiple">
      <div v-for="entity in value" v-bind:key="entity[idField]">
        <v-chip
          :close="!disabled"
          @input="remove(entity)"
          :data-cy="'chip-' + entity[idField]"
        >
          {{ getEntityDescription(entity) }}
        </v-chip>
      </div>
    </template>
  </div>
</template>

<script>
export default {
  name: "EntitySearch",
  props: {
    location: Boolean,
    person: Boolean,
    course: Boolean,
    team: Boolean,
    address: Boolean,
    asset: Boolean,
    group: Boolean,
    meeting: Boolean,
    groupType: Boolean,
    managerType: Boolean,
    multiple: { type: Boolean, default: false },
    existingEntities: Array,
    value: null,
    searchEndpoint: String,
    errorMessages: String,
    label: String,
    disabled: Boolean
  },
  data() {
    return {
      descriptionLimit: 50,
      entities: [],
      searchInput: "",
      isLoading: false
    };
  },

  watch: {
    value(val) {
      this.setSelected(val);
    }
  },

  computed: {
    getLabel() {
      if (this.label) return this.label;
      else if (this.location) return this.$t("events.event-location");
      else if (this.person) return this.$t("actions.search-people");
      else if (this.course) return this.$t("actions.search-courses");
      else if (this.team) return this.$t("teams.title");
      else if (this.address) return this.$t("actions.search-addresses");
      else if (this.asset) return this.$t("assets.title");
      else if (this.group) return this.$t("groups.title");
      else if (this.meeting) return this.$t("groups.meetings.title");
      else if (this.groupType) return this.$t("actions.search-group-types");
      else if (this.managerType) return this.$t("actions.search-manager-types");
      else return "";
    },
    idField() {
      return "id";
    },
    searchableEntities() {
      if (this.existingEntities) {
        return this.entities.filter(ent => {
          for (let otherEnt of this.existingEntities) {
            if (ent[this.idField] === otherEnt[this.idField]) {
              return false;
            }
          }
          return true;
        });
      }
      return this.entities;
    }
  },

  methods: {
    selectionContains(entity) {
      if (!this.value || !this.value.length) return;
      var idx = this.value.findIndex(
        en => en[this.idField] === entity[this.idField]
      );
      return idx > -1;
    },
    setSelected(entity) {
      this.$emit("input", entity);
    },
    getEntityDescription(entity, letterLimit = this.descriptionLimit) {
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
      } else if (this.course) {
        entityDescriptor = entity.name;
      } else if (this.team) {
        entityDescriptor = entity.description;
      } else if (this.address) {
        entityDescriptor = entity.name + ", " + entity.address;
      } else if (this.asset) {
        entityDescriptor = entity.description;
      } else if (this.group) {
        entityDescriptor = entity.name + ": " + entity.description;
      } else if (this.meeting) {
        entityDescriptor = entity.description;
      } else if (this.groupType) {
        entityDescriptor = entity.name;
      } else if (this.managerType) {
        entityDescriptor = entity.name;
      }
      if (entityDescriptor.length > letterLimit) {
        //TODO don't do this here, it limits search functionality
        entityDescriptor = entityDescriptor.substring(0, letterLimit) + "...";
      }
      return entityDescriptor;
    },
    customFilter(item, queryText) {
      const itemDesc = this.getEntityDescription(item).toLowerCase();
      const searchText = queryText.toLowerCase();
      return itemDesc.indexOf(searchText) > -1;
    },
    remove(entity) {
      if (!this.multiple) return;
      var idx = this.value.findIndex(
        en => en[this.idField] === entity[this.idField]
      );
      if (idx > -1) {
        this.value.splice(idx, 1);
      }
    },
    compare(a, b) {
      if (!a || !b) return false;
      return a[this.idField] === b[this.idField];
    }
  },
  mounted() {
    //TODO use search-input.sync to avoid making a huge request here
    this.isLoading = true;
    var endpoint = "";
    if (this.location) endpoint = "/api/v1/places/locations";
    else if (this.person) endpoint = "/api/v1/people/persons";
    else if (this.course) endpoint = "/api/v1/courses/courses";
    else if (this.team) endpoint = "/api/v1/teams/";
    else if (this.asset) endpoint = "/api/v1/assets/";
    else if (this.address) endpoint = "/api/v1/places/addresses";
    else if (this.group) endpoint = "/api/v1/groups/groups";
    else if (this.meeting) endpoint = "/api/v1/groups/meetings";
    else if (this.groupType) endpoint = "/api/v1/groups/group-types";
    else if (this.managerType) endpoint = "/api/v1/groups/manager-types";
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
