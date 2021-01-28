<template>
  <v-card>
    <v-row
      class="subrow"
      align="center"
    >
      <v-col
        cols="7"
        align="center"
        class="text-right"
      >
        <v-btn
          dark
          @click="$emit('addNewLocale')"
        >
          <v-icon left>add_circle_outline</v-icon>
          {{ $t("translation.locale.add") }}
        </v-btn>
      </v-col>
      <v-col
        cols="4"
        align="center"
        class="text-right mr-5"
      >
        <v-btn
          dark
          @click="$emit('hideToolBox')"
        >
          {{ $t("actions.hide") }}
        </v-btn>
      </v-col>
    </v-row>
    <v-row
      class="subrow"
    >
      <v-col
        cols="1"
      >
      </v-col>
      <v-col
        cols="10"
      >
        <v-select
          outlined multiple chips
          prepend-icon="filter_alt"
          :label="$t('translation.filters.label')"
          :items="translatedFilters()"
          v-model="activeFilters"
          @change="filtersUpdated"
        />
      </v-col>
      <v-col
        cols="1"
      >
      </v-col>
    </v-row>
    <v-row
      class="subrow"
    >
      <v-col
        cols="1"
      >
      </v-col>
      <v-col
        cols="10"
      >
        <v-card
          width="100%"
          class="text-center pa-2 my-2 primary--text"
        >
          {{ $t("translation.filters.portion-translated",
            [numTranslated, totalEntries]) }}
        </v-card>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-card
          width="100%"
          class="text-center pa-2 my-2 primary--text"
        >
          {{ $t("translation.filters.portion-verified",
            [numVerified, totalEntries]) }}
        </v-card>
      </v-col>
      <v-col
        cols="1"
      >
      </v-col>
    </v-row>
  </v-card>
</template>

<script>
export default {
  name: "ToolBox",
  props: {
    numTranslated: { type: Number, required: true },
    numVerified:   { type: Number, required: true },
    totalEntries:  { type: Number, required: true },
    filterOptions: { type: Array,  required: true },
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
    translatedFilters() {
      return this.filterOptions.map((item) => this.$t(item));
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
