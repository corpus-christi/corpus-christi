<template>
  <v-app-bar dense dark height="60" >
    <v-card
      elevation="0"
      color="transparent"
      min-width="15%"
      max-width="15%"
    >
      <v-toolbar-title>
        {{ $t("translation.tags.top") }}
      </v-toolbar-title>
    </v-card>
    <v-card min-width="3%" max-width="3%" />
    <v-card
      elevation="0"
      color="transparent"
      min-width="15%"
      max-width="15%"
    >
      <v-toolbar-title>
        {{ $t("translation.tags.sub") }}
      </v-toolbar-title>
    </v-card>
    <v-card min-width="3%" max-width="3%" />
    <v-card
      elevation="0"
      color="transparent"
      class="mt-5"
      min-width="13%"
      max-width="13%"
    >
      <v-select
        :label="$t('translation.translate-from')"
        :items="allLocales"
        item-text="displayString"
        item-value="code"
        v-model="previewLocale"
        @change="$emit('previewUpdated', previewLocale)"
      />
    </v-card>
    <v-card min-width="1.8%" max-width="1.8%" />
    <v-icon>keyboard_arrow_right</v-icon>
    <v-card min-width="1.7%" max-width="1.8%" />
    <v-card
      elevation="0"
      color="transparent"
      class="mt-5"
      min-width="13%"
      max-width="13%"
    >
      <v-select
        :label="$t('translation.translate-to')"
        :items="allLocales"
        item-text="displayString"
        item-value="code"
        v-model="currentLocale"
        @change="$emit('currentUpdated', currentLocale)"
      />
    </v-card>
    <v-card min-width="1%" max-width="1%" />
    <v-card
      min-width="5%"
      max-width="5%"
    >
      <v-btn
        @click="$emit('updateTransToFrom')"
        small color="primary" height="50px" width="75px"
        :loading="loadingTranslations"
      >
        {{ $t("translation.fetch") }}
      </v-btn>
    </v-card>
    <v-card min-width="4.5%" max-width="4.5%" />
    <v-card 
      elevation="0"
      color="transparent"
      min-width="16.3%"
      max-width="16.3%"
    >
      <v-toolbar-title>
        {{ $t("translation.new-translation") }}
      </v-toolbar-title>
    </v-card>
    <v-card min-width="1%" max-width="1%" />
    <v-card
      elevation="0"
      color="transparent"
      min-width="1%"
      max-width="1%"
    >
      <v-icon>done</v-icon>
    </v-card>
  </v-app-bar>
</template>

<script>
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
    };
  },
};
</script>
