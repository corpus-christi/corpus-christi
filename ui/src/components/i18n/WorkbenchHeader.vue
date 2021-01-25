<template>
  <v-app-bar dense dark height="60">
    <v-card elevation="0" color="transparent" min-width="15%" max-width="15%">
      <v-toolbar-title>
        {{ $t("translation.tags.top") }}
      </v-toolbar-title>
    </v-card>
    <v-card min-width="3%" max-width="3%" />
    <v-card elevation="0" color="transparent" min-width="15%" max-width="15%">
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
        :items="fromLocaleList"
        item-text="displayString"
        item-value="code"
        v-model="previewLocale"
        @change="changeLocaleList('fromLocaleList', previewLocale)"
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
        :items="toLocaleList"
        item-text="displayString"
        item-value="code"
        v-model="currentLocale"
        @change="changeLocaleList('toLocaleList', currentLocale)"
      />
    </v-card>
    <v-card min-width="1%" max-width="1%" />
    <v-card min-width="5%" max-width="5%">
      <v-btn
        :disabled="previewLocale == '' || currentLocale == ''"
        @click="$emit('updateTransToFrom')"
        small
        outlined
        depressed
        color="primary"
        height="50px"
        width="75px"
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
    <v-card elevation="0" color="transparent" min-width="1%" max-width="1%">
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
      console.log("the watch allLocales function was called.");
      console.log("allLocales:     ".concat(JSON.stringify(this.allLocales)));
      this.initializeToAndFromLocaleLists();
      console.log("BEFOREUPDATE() toLocaleList:   ".concat(JSON.stringify(this.toLocaleList)));
      console.log("BEFOREUPDATE() fromLocaleList: ".concat(JSON.stringify(this.fromLocaleList)));
    },
  },
  methods: {
    changeLocaleList(theListName, thePopObject) {
      console.log("the fromLocalList was changed.");
      console.log("The index of thePopObject is: ", this.fromLocaleList.indexOf(thePopObject));
      console.log(this.fromLocaleList);
      console.log(thePopObject);
      if (theListName=="toLocaleList") {
        console.log("if");
        //doSomething to the fromLocaleList
        this.fromLocaleList = [];
        this.fromLocaleList.push(...this.allLocales);
        this.fromLocaleList.splice(this.findIndex(this.fromLocaleList, thePopObject), 1);
        this.$emit("currentUpdated", thePopObject);
      } else if (theListName=="fromLocaleList") {
        console.log("else if");
        //doSomething to the toLocaleList
        this.toLocaleList = [];
        this.toLocaleList.push(...this.allLocales);
        this.toLocaleList.splice(this.findIndex(this.toLocaleList, thePopObject), 1);
        this.$emit('previewUpdated', thePopObject);
      } else{
        console.log("\n\n\n\nSOMETHING REALLY WEIRD HAPPENED!\n\n\n\n");
      }
      console.log("toLocaleList:   ".concat(JSON.stringify(this.toLocaleList)));
      console.log("fromLocaleList: ".concat(JSON.stringify(this.fromLocaleList)));
    },
    initializeToAndFromLocaleLists() {
      console.log("The initializeToAndFromLocaleLists function was called.");
      // console.log("BEFORE:");
      // console.log("toLocaleList:   ".concat(JSON.stringify(this.toLocaleList)));
      // console.log("fromLocaleList: ".concat(JSON.stringify(this.fromLocaleList)));
      // console.log("allLocales:     ".concat(JSON.stringify(this.allLocales)));
      this.fromLocaleList = this.allLocales;
      this.toLocaleList = this.allLocales;
      // console.log("AFTER:");
      console.log("toLocaleList:   ".concat(JSON.stringify(this.toLocaleList)));
      console.log("fromLocaleList: ".concat(JSON.stringify(this.fromLocaleList)));
      // console.log("allLocales:     ".concat(JSON.stringify(this.allLocales)));
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
