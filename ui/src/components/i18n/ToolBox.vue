<template>
  <v-card>
    <v-card-title>
      {{ $t("translation.toolbox.title") }}
      <v-spacer />
      <v-btn icon @click="$emit('hideToolBox')">
        <v-icon>close</v-icon>
      </v-btn>
    </v-card-title>

    <v-card-text>
      <v-container>
        <v-row justify="space-around">
          <v-col>
            {{
              $t("translation.filters.portion-translated", [
                numTranslated,
                totalEntries,
              ])
            }}
          </v-col>
          <v-col>
            {{
              $t("translation.filters.portion-verified", [
                numVerified,
                totalEntries,
              ])
            }}
          </v-col>
        </v-row>

        <v-row>
          <v-col>
            <v-select
              outlined
              multiple
              chips
              prepend-icon="filter_alt"
              :label="$t('translation.filters.label')"
              :items="translatedFilters()"
              v-model="activeFilters"
              @change="filtersUpdated"
            />
          </v-col>
        </v-row>
      </v-container>
    </v-card-text>

    <v-card-actions>
      <v-spacer />
      <v-btn @click="$emit('addNewLocale')">
        <v-icon left>add_circle_outline</v-icon>
        {{ $t("translation.locale.add") }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
export default {
  name: "ToolBox",
  props: {
    numTranslated: { type: Number, required: true },
    numVerified: { type: Number, required: true },
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
      this.$emit("sendFilters", this.activeFilters);
    },
    translatedFilters() {
      return this.filterOptions.map((item) => this.$t(item));
    },
  },
  mounted: function () {
    this.filtersUpdated();
  },
};
</script>
