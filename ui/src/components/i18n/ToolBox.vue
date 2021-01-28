<template>
  <v-card>
    <v-card-title>
      {{ $t("translation.toolbox.title") }}
      <v-spacer />
      <v-btn icon @click="$emit('hideToolBox')">
        <v-icon>close</v-icon>
      </v-btn>
    </v-card-title>

    <v-divider horizontal />

    <v-card-text class="pb-0">
      <v-container>
        <v-row justify="space-around">
          <v-col align="center">
            {{
              $t("translation.filters.portion-translated", [
                numTranslated,
                totalEntries,
              ])
            }}
          </v-col>
        </v-row>
        <v-row>
          <v-col align="center">
            {{
              $t("translation.filters.portion-verified", [
                numVerified,
                totalEntries,
              ])
            }}
          </v-col>
        </v-row>

        <v-row>
          <v-col class="pb-0">
            <v-select
              outlined
              multiple
              chips
              :label="$t('translation.filters.label')"
              :items="filterObjs"
              item-text="disp"
              item-value="tag"
              v-model="activeFilters"
              @change="filtersUpdated"
            />
          </v-col>
        </v-row>
      </v-container>
    </v-card-text>

    <v-card-actions>
      <v-spacer />
      <v-btn class="mr-5" @click="$emit('addNewLocale')" color="primary">
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

  computed: {
    filterObjs() {
      return this.filterOptions.map((item) => {
        return {
          tag: item,
          disp: this.$t(item),
        };
      });
    },
  },

  methods: {
    filtersUpdated() {
      this.$emit("sendFilters", this.activeFilters);
    },
  },

  mounted: function () {
    this.filtersUpdated();
  },
};
</script>
