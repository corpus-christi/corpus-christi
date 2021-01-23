<template>
  <v-card
    class="mr-2"
    outlined
    elevation="2"
  >
    <v-row
      class="subrow"
      align="center"
      no-gutters
    >
      <v-col
        align="center"
      >
        <v-btn
          class="ml-3"
          dark
          @click="$emit('addNewLocale')"
        >
          <v-icon left>add_circle_outline</v-icon>
          Add New Locale
        </v-btn>
      </v-col>
      <v-col
        align="center"
      >
        <v-btn
          dark
          @click="$emit('goToBot')"
        >
          <v-icon>keyboard_arrow_down</v-icon>
        </v-btn>
      </v-col>
    </v-row>
    <v-row
      class="subrow"
      no-gutters
    >
      <v-col>
        <v-select
          outlined multiple chips
          prepend-icon="filter_alt"
          label="Filters"
          :items="filterOptions"
          v-model="activeFilters"
          @change="filtersUpdated"
        />
      </v-col>
    </v-row>
    <v-row
      class="subrow"
      no-gutters
    >
      <v-col>
        <v-card
          width="100%"
          class="text-center pa-2 my-2"
        >
          {{numTranslated}} / {{totalEntries}} Translated
        </v-card>
        <v-card
          width="100%"
          class="text-center pa-2 my-2"
        >
          {{numValidated}} / {{totalEntries}} Verified
        </v-card>
      </v-col>
    </v-row>
    <v-row
      class="subrow ml-3"
      no-gutters
    >
      <v-col cols="4">
      </v-col>
      <v-col 
        cols="4"
        right
        align="center"
      >
        <v-btn
          dark
          @click="$emit('hideToolBox')"
        >
          Hide
        </v-btn>
      </v-col>
      <v-col 
        cols="4"
        align="center"
      >
        <v-btn
          dark
          @click="$emit('goToTop')"
        >
          <v-icon>keyboard_arrow_up</v-icon>
        </v-btn>
      </v-col>
    </v-row>
  </v-card>
</template>

<script>
export default {
  name: "ToolBox",
  props: {
    numTranslated: { type: Number, required: true },
    numValidated: { type: Number, required: true },
    totalEntries: { type: Number, required: true },
    filterOptions: { type: Array, required: true },
  },
  data() {
    return {
      activeFilters: [],
    };
  },
  methods: {
    filtersUpdated() {
      this.$emit('sendFilters', this.activeFilters);
    },
  },
  mounted: function() {
    this.filtersUpdated();
  },
};
</script>

<style scoped>
.subrow {
  height: 25%;
  align-content: center;
}
</style>
