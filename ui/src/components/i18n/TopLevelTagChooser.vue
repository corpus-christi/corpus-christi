<template>
  <v-card-text>
    <v-list 
      elevation="2"
      rounded
    >
      <v-list-item-group
        color="grey darken-4"
        multiple
      >

      <v-tooltip right
        v-for="(tag, index) in topLevelTags"
        :key="index"
      >
        <template v-slot:activator="{ on }">
          <!-- Workaround from https://github.com/vuetifyjs/vuetify/issues/11345 -->
          <span v-on="on">
            <v-checkbox
              v-model="selectedTags"
              :label="`${tag}
                (${incompleteCounts[tag] ? incompleteCounts[tag].untranslated : 0} | 
                ${incompleteCounts[tag] ? incompleteCounts[tag].unverified : 0})`"
              :value="tag"
              @click="onTagsChanged"
            />
          </span>
        </template>
        <span>
          {{ $t("translation.tags.tooltip",
          [incompleteCounts[tag] ? incompleteCounts[tag].untranslated : 0,
          incompleteCounts[tag] ? incompleteCounts[tag].unverified : 0]) }}
        </span>
      </v-tooltip>

      </v-list-item-group>
    </v-list>
  </v-card-text>
</template>

<script>
export default {
  name: "TopLevelTagChooser",
  props: {
    topLevelTags: { type: Array, required: true, },
    allTranslations: { type: Array, required: false, },
  },
  data() {
    return {
      selectedTags: [],
      incompleteCounts: [],
    };
  },
  watch: {
    allTranslations: function() {
      this.populateIncompleteCounts();
    },
  },
  methods: {
    onTagsChanged() {
      this.$emit("tagsUpdated", this.selectedTags);
    },
    populateIncompleteCounts() {
      this.incompleteCounts = [];

      this.topLevelTags.forEach((topLevelTag) => {
        this.incompleteCounts[topLevelTag] = {
          untranslated: this.numUntranslated(topLevelTag),
          unverified: this.numUnverified(topLevelTag),
        };
      });
    },
    numUntranslated(topLevelTag) {
      return this.allTranslations
        .filter((obj) => obj.top_level_key == topLevelTag)
        .filter((obj) => obj.current_gloss == '')
        .length;
    },
    numUnverified(topLevelTag) {
      return this.allTranslations
        .filter((obj) => obj.top_level_key == topLevelTag)
        .filter((obj) => obj.current_verified == false)
        .length;
    },
  },
};
</script>
