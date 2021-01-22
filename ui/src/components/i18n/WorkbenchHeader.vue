<template>
  <v-app-bar dense dark height="60">
    <v-card min-width="1%" max-width="1%"></v-card>
    <v-card
      elevation="0"
      color="transparent"
      min-width="4%"
      max-width="4%"
    >
      <v-toolbar-title>
        Tags
      </v-toolbar-title>
    </v-card>
    <v-card min-width="15%" max-width="15%"></v-card>
    <v-card
      elevation="0"
      color="transparent"
      min-width="7%"
      max-width="7%"
    >
      <v-toolbar-title>
        Subtags
      </v-toolbar-title>
    </v-card>
    <v-card min-width="9%" max-width="9%"></v-card>
    <v-card
      elevation="0"
      color="transparent"
      class="mt-5"
      min-width="13%"
      max-width="13%"
    >
      <!-- Cannot set default without losing functionality -->
      <v-select
        :label="'Translate From'"
        :items="allLocales"
        item-text="displayString"
        item-value="code"
        v-model="previewLocale"
        @change="$emit('previewUpdated', previewLocale)"
      />
    </v-card>
    <v-card min-width="1.7%" max-width="1.8%"></v-card>
    <v-icon>keyboard_arrow_right</v-icon>
    <v-card min-width="1.7%" max-width="1.8%"></v-card>
    <v-card
      elevation="0"
      color="transparent"
      class="mt-5"
      min-width="13%"
      max-width="13%"
    >
      <v-select
        :label="'Translate To'"
        :items="allLocales"
        item-text="displayString"
        item-value="code"
        v-model="currentLocale"
        @change="$emit('currentUpdated', currentLocale)"
      />
    </v-card>
    <v-card min-width="1%" max-width="1%"></v-card>
    <v-card
      min-width="4%"
      max-width="4%"
    >
      <v-btn
        @click="$emit('updateTransToFrom')"
        outlined
        :loading="loadingTranslations"
      >
        Go
      </v-btn>
    </v-card>
    <v-card min-width="5.5%" max-width="5.5%"></v-card>
    <v-card 
      elevation="0"
      color="transparent"
      min-width="10%"
      max-width="10%"
    >
      <v-toolbar-title>
        New Translation
      </v-toolbar-title>
    </v-card>
    <v-card min-width="7.5%" max-width="7.5"></v-card>
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
