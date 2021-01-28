<template>
  <v-card class="mb-2">
    <v-container>
      <v-row align="center">
        <v-col class="headline">{{ $t("translation.tags.top") }}</v-col>

        <v-col>
          <v-select
            :label="$t('translation.translate-from')"
            :items="allLocales"
            item-text="displayString"
            item-value="code"
            v-model="previewLocale"
          />
        </v-col>

        <v-icon
          @mouseover="hoveringOverCenterIcon = true"
          @mouseleave="hoveringOverCenterIcon = false"
          @click="swapSelectedLocales"
        >
          {{ hoveringOverCenterIcon ? "swap_horiz" : "keyboard_arrow_right" }}
        </v-icon>

        <v-col>
          <v-select
            :label="$t('translation.translate-to')"
            :items="allLocales"
            item-text="displayString"
            item-value="code"
            v-model="currentLocale"
            :error="previewLocale == currentLocale && currentLocale !== ''"
          />
        </v-col>
        <v-col>
          <v-btn
            :disabled="previewLocale === '' || currentLocale === ''"
            @click="$emit('updateTransToFrom')"
            :color="areLocalesEqual ? 'primary' : 'warning'"
            :loading="loadingTranslations"
          >
            {{ $t("translation.fetch") }}
          </v-btn>
        </v-col>
      </v-row>
    </v-container>
  </v-card>
</template>

<script>
/* eslint-disable */
export default {
  name: "WorkbenchHeader",
  props: {
    allLocales: { type: Array, required: true },
    loadingTranslations: { type: Boolean, required: true },
  },
  data() {
    return {
      previewLocale: "",
      currentLocale: "",
      prevLocaleOnLoad: "",
      currLocaleOnLoad: "",
      hoveringOverCenterIcon: false,
    };
  },
  watch: {
    previewLocale: function() {
      this.$emit('previewUpdated', this.previewLocale);
    },
    currentLocale: function() {
      this.$emit('currentUpdated', this.currentLocale);
    },
  },
  computed: {
    areLocalesEqual: function() {
      return (this.currentLocale == this.currLocaleOnLoad) && (this.previewLocale == this.prevLocaleOnLoad);
    },
  },
  methods: {
    swapSelectedLocales() {
      let temp = this.previewLocale;
      this.previewLocale = this.currentLocale;
      this.currentLocale = temp;
    },
  },
};
</script>
