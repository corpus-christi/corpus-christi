<template>
  <v-app-bar dense dark height="60">
    <v-row align="center" class="ml-3">
      <v-col cols="2">
        <v-toolbar-title>
          Tags
        </v-toolbar-title>
      </v-col>
      <v-col cols="2">
        <v-toolbar-title>
          Subtags
        </v-toolbar-title>
      </v-col>
      <v-col cols="2">
        <!-- Cannot set default without losing functionality -->
        <v-select
          :label="'Translate From'"
          :items="allLocales"
          item-text="displayString"
          item-value="code"
          v-model="previewLocale"
          @change="$emit('previewUpdated', previewLocale)"
          class="mt-5"
        />
      </v-col>
      <v-icon>keyboard_arrow_right</v-icon>
      <v-col cols="2">
        <v-select
          :label="'Translate To'"
          :items="allLocales"
          item-text="displayString"
          item-value="code"
          v-model="currentLocale"
          @change="$emit('currentUpdated', currentLocale)"
          class="mt-5"
        />
      </v-col>
      <v-col cols="3" align="center">
        <v-toolbar-title>
          New Translation
        </v-toolbar-title>
      </v-col>
      <v-col cols="0">
        <v-toolbar-title>
          <v-icon>done</v-icon>
        </v-toolbar-title>
      </v-col>
    </v-row>
  </v-app-bar>
</template>

<script>
export default {
  name: "WorkbenchHeader",
  props: {
    allLocales: { type: Array, required: true },
  },
  data() {
    return {
      previewLocale: "",
      currentLocale: "",
    };
  },
};
</script>
