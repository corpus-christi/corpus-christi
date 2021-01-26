<template>
  <v-app-bar dense dark height="60">
    <v-card elevation="0" color="transparent" width="15%">
      <v-toolbar-title>
        {{ $t("translation.tags.top") }}
      </v-toolbar-title>
    </v-card>
    <v-card width="3%" />
    <v-card elevation="0" color="transparent" width="15%">
      <v-toolbar-title>
        {{ $t("translation.tags.sub") }}
      </v-toolbar-title>
    </v-card>
    <v-card width="2.8%" />
    <v-card
      elevation="0"
      color="transparent"
      class="mt-5"
      width="13%"
    >
      <v-select
        :label="$t('translation.translate-from')"
        :items="fromLocaleList"
        item-text="displayString"
        item-value="code"
        v-model="previewLocale"
        @change="changeLocaleList('fromLocaleList', previewLocale)"
      />
    </v-card>
    <v-card width="2%" />
    <v-icon>keyboard_arrow_right</v-icon>
    <v-card width="2%" />
    <v-card
      elevation="0"
      color="transparent"
      class="mt-5"
      width="13%"
    >
      <v-select
        :label="$t('translation.translate-to')"
        :items="toLocaleList"
        item-text="displayString"
        item-value="code"
        v-model="currentLocale"
        @change="changeLocaleList('toLocaleList', currentLocale)"
      />
    </v-card>
    <v-card width="1%" />
    <v-card width="3%">
      <v-btn
        :disabled="previewLocale == '' || currentLocale == ''"
        @click="$emit('updateTransToFrom')"
        small
        outlined
        depressed
        color="primary"
        height="50px"
        :loading="loadingTranslations"
      >
        {{ $t("translation.fetch") }}
      </v-btn>
    </v-card>
    <v-card
      elevation="0"
      color="transparent"
      width="21%"
      align="center"
    >
      <v-toolbar-title>
        {{ $t("translation.new-translation") }}
      </v-toolbar-title>
    </v-card>
    <v-card width="3%" />
    <v-card elevation="0" color="transparent" width="1%">
      <v-icon>done</v-icon>
    </v-card>
  </v-app-bar>
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
      fromLocaleList: [],
      toLocaleList: [],
    };
  },
  watch: {
    allLocales: function() {
      this.initializeToAndFromLocaleLists();
    },
  },
  methods: {
    changeLocaleList(theListName, thePopObject) {
      if (theListName=="toLocaleList") {
        //doSomething to the fromLocaleList
        this.fromLocaleList = [];
        this.fromLocaleList.push(...this.allLocales);
        this.fromLocaleList.splice(this.findIndex(this.fromLocaleList, thePopObject), 1);
        this.$emit("currentUpdated", thePopObject);
      } else if (theListName=="fromLocaleList") {
        //doSomething to the toLocaleList
        this.toLocaleList = [];
        this.toLocaleList.push(...this.allLocales);
        this.toLocaleList.splice(this.findIndex(this.toLocaleList, thePopObject), 1);
        this.$emit('previewUpdated', thePopObject);
      } else{
        console.log("\n\n\n\nSOMETHING REALLY WEIRD HAPPENED\n\n\n\n");
      }
    },
    initializeToAndFromLocaleLists() {
      this.fromLocaleList = this.allLocales;
      this.toLocaleList = this.allLocales;
    },
    findIndex(theList, theObject){
      for(let i=0;i<theList.length;i++){
        if(theList[i].code==theObject){
          return i;
        }
      }
      return -1;
    },
  },
};
</script>
