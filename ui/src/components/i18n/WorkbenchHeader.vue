<template>
  <v-card class="mb-2">
    <v-container>
      <v-row align="center">
        <v-col class="headline">{{ $t("translation.tags.top") }}</v-col>

        <v-s />

        <v-col>
          <v-select
            :label="$t('translation.translate-from')"
            :items="fromLocaleList"
            item-text="displayString"
            item-value="code"
            v-model="previewLocale"
            @change="changeLocaleList('fromLocaleList', previewLocale)"
        /></v-col>

        <v-col>
          <v-select
            :label="$t('translation.translate-to')"
            :items="toLocaleList"
            item-text="displayString"
            item-value="code"
            v-model="currentLocale"
            @change="changeLocaleList('toLocaleList', currentLocale)"
          />
        </v-col>
        <v-col>
          <v-btn
            :disabled="previewLocale === '' || currentLocale === ''"
            @click="$emit('updateTransToFrom')"
            color="primary"
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
      fromLocaleList: [],
      toLocaleList: [],
    };
  },
  watch: {
    allLocales: function () {
      console.log("the watch allLocales function was called.");
      console.log("allLocales:     ".concat(JSON.stringify(this.allLocales)));
      this.initializeToAndFromLocaleLists();
      console.log(
        "BEFOREUPDATE() toLocaleList:   ".concat(
          JSON.stringify(this.toLocaleList)
        )
      );
      console.log(
        "BEFOREUPDATE() fromLocaleList: ".concat(
          JSON.stringify(this.fromLocaleList)
        )
      );
    },
  },
  methods: {
    changeLocaleList(theListName, thePopObject) {
      console.log("the fromLocalList was changed.");
      console.log(
        "The index of thePopObject is: ",
        this.fromLocaleList.indexOf(thePopObject)
      );
      console.log(this.fromLocaleList);
      console.log(thePopObject);
      if (theListName === "toLocaleList") {
        console.log("if");
        //doSomething to the fromLocaleList
        this.fromLocaleList = [];
        this.fromLocaleList.push(...this.allLocales);
        this.fromLocaleList.splice(
          this.findIndex(this.fromLocaleList, thePopObject),
          1
        );
        this.$emit("currentUpdated", thePopObject);
      } else if (theListName === "fromLocaleList") {
        console.log("else if");
        //doSomething to the toLocaleList
        this.toLocaleList = [];
        this.toLocaleList.push(...this.allLocales);
        this.toLocaleList.splice(
          this.findIndex(this.toLocaleList, thePopObject),
          1
        );
        this.$emit("previewUpdated", thePopObject);
      } else {
        console.log("\n\n\n\nSOMETHING REALLY WEIRD HAPPENED!\n\n\n\n");
      }
      console.log("toLocaleList:   ".concat(JSON.stringify(this.toLocaleList)));
      console.log(
        "fromLocaleList: ".concat(JSON.stringify(this.fromLocaleList))
      );
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
      console.log(
        "fromLocaleList: ".concat(JSON.stringify(this.fromLocaleList))
      );
      // console.log("allLocales:     ".concat(JSON.stringify(this.allLocales)));
    },
    findIndex(theList, theObject) {
      for (let i = 0; i < theList.length; i++) {
        if (theList[i].code === theObject) {
          return i;
        }
      }
      return -1;
    },
  },
};
</script>
