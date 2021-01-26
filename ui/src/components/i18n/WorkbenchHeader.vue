<template>
  <v-card class="mb-2">
    <v-container>
      <v-row align="center">
        <v-col class="headline">{{ $t("translation.tags.top") }}</v-col>
        
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
