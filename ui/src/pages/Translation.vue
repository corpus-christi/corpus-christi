<template>
  <v-container>
    <v-card elevation="0" class="d-flex justify-end">
      <v-btn
        @click="showToolBox = true"
        class="col-md-1"
        outlined
      >
        Reveal ToolBox
      </v-btn>
    </v-card>

    <ToolBox class="ToolBox"
      :numTranslated="numEntriesTranslated"
      :numValidated="numEntriesValidated"
      :totalEntries="numEntriesTotal"
      :shouldBeShown="showToolBox"
      @goToTop="$vuetify.goTo(0)"
      @goToBot="$vuetify.goTo(bodyScrollHeight())"
      @hideToolBox="showToolBox = false"
      @sendFilters="useFilter"
    />

    <WorkbenchHeader
      :allLocales="allLocaleObjs"
      :loadingTranslations="loadingTranslations"
      @previewUpdated="onPreviewLocaleChanged"
      @currentUpdated="onCurrentLocaleChanged"
      @updateTransToFrom="fetchNewTranslations"
    />

    <v-row>
      <v-col cols="2">
        <TopLevelTagChooser
          :topLevelTags="topLevelTags"
          @tagsUpdated="onTopLevelTagsUpdated"
        />
      </v-col>

      <v-divider vertical />

      <v-col>
        <TranslationCard
          v-for="(card, index) in translationObjs"
          :key="index"
          :myIndex="index"
          :topLevelTag="card.top_level_key"
          :restOfTag="card.rest_of_key"
          :previewGloss="card.preview_gloss"
          :currentGloss="card.current_gloss"
          :currentVerified="card.current_verified"
          :filters="filters"
          :selectedTags="selectedTags"
          :currentCode="currentCode"
          @appendToList="appendTranslation"
          @clearFromList="clearGivenTranslation"
          @validationChanged="logValidation"
          @submitAChange="sendUpdatedTranslation"
        />
      </v-col>
    </v-row>

    <v-dialog
      v-model="dialog"
      width="67%"
    >
      <v-card>
        <v-card-title class="headline black lighten-2 white--text">
          You are about to submit {{Object.keys(newTranslationList).length}} changes!
        </v-card-title>
        <v-list-item
          v-for="(item, index) in newTranslationList"
          :key="index"
          outlined
        >
          <v-list-item-title class="text-right AutoWidth">{{index}}</v-list-item-title>
          <v-divider vertical class="mx-3" />
          <v-list-item-subtitle class="text-right AutoWidth">{{item.oldTrans}}</v-list-item-subtitle>
          <v-list-item-icon><v-icon>keyboard_arrow_right</v-icon></v-list-item-icon>
          <v-list-item-subtitle class="text-left AutoWidth">{{item.newTrans}}</v-list-item-subtitle>
        </v-list-item>
        <v-card-actions class="headline black lighten-2 white--text">
          <v-btn color="red lighten-2" @click="dialog=false" outlined class="white">
            Sumbit
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- <v-row fixed bottom>
      <v-app-bar color="white" elevation="2">
        <v-card min-width="60%" />
        <v-card min-width="2%" />

        <v-btn min-width="9%">
          Activate
        </v-btn>
      </v-app-bar>
    </v-row> -->
  </v-container>
</template>

<script>
import { mapState } from "vuex";
// import { eventBus } from "../plugins/event-bus.js";
import { LocaleModel } from "../models/Locale.js";
import TranslationCard from "../components/i18n/TranslationCard.vue";
import TopLevelTagChooser from "../components/i18n/TopLevelTagChooser.vue";
import WorkbenchHeader from "../components/i18n/WorkbenchHeader.vue";
import ToolBox from "../components/i18n/ToolBox.vue";
const _ = require("lodash");
export default {
  name: "Translation",
  components: {
    WorkbenchHeader,
    TopLevelTagChooser,
    TranslationCard,
    ToolBox,
  },
  data() {
    return {
      dialog: false,
      fabToTop: false,
      fabToBot: true,
      canUserLeaveFreely: true,
      showToolBox: true,

      topLevelTags: [],
      selectedTags: [],
      allLocaleObjs: [],
      translationObjs: [],
      previewCode: "",
      currentCode: "",
      loadingTranslations: false,
      newTranslationList: {},
      filters: {},
    };
  },
  computed: {
    ...mapState(["currentAccount"]),
    ...mapState(["currentLocale"]),
    numEntriesTranslated() {
      return this.translationObjs.filter(obj => obj.current_gloss != '').length;
    },
    numEntriesValidated() {
      return this.translationObjs.filter(obj => obj.current_verified).length;
    },
    numEntriesTotal() {
      return this.translationObjs.length;
    },
  },
  methods: {
    onScroll(e) {
      if (typeof window === "undefined") return;
      const top = window.pageYOffset || e.target.scrollTop || 0;
      this.fabToTop = top > 20;
      this.fabToBot = top < this.scrollHeight - 20;
    },
    loadTopLevelTags() {
      return this.$http
        .get(`api/v1/i18n/keys`)
        .then((resp) => {
          resp.data.forEach((obj) => {
            this.topLevelTags.push(obj.id.split(".")[0]);
          });
          this.topLevelTags = _.uniq(this.topLevelTags).sort();
        })
        .catch((err) => console.log(err));
    },
    getAllLocales() {
      return this.$http
        .get(`api/v1/i18n/locales`)
        .then((resp) => {
          this.allLocaleObjs = resp.data.map((obj) => {
            let tempLocaleModel = new LocaleModel(obj);
            return {
              displayString: tempLocaleModel.flagAndDescription,
              code: tempLocaleModel.languageAndCountry,
            };
          });
        })
        .catch((err) => console.log(err));
    },
    fetchNewTranslations() {
      this.loadingTranslations = true;
      return this.$http
        .get(`api/v1/i18n/values/translations/${this.previewCode}/${this.currentCode}`)
        .then((resp) => {
          this.translationObjs = resp.data;
        })
        .catch((err) => console.log(err))
        .finally(() => this.loadingTranslations = false);
    },
    onPreviewLocaleChanged(code) {
      this.previewCode = code;
    },
    onCurrentLocaleChanged(code) {
      this.currentCode = code;
    },
    onTopLevelTagsUpdated(tagList) {
      this.selectedTags = tagList;
    },
    submitChanges() {
      console.log(this.newTranslationList);
    },
    appendTranslation(key, newTrans, oldTrans) {
      if (key in this.newTranslationList) {
        this.newTranslationList[key].newTrans = newTrans;
        this.newTranslationList[key].oldTrans = oldTrans;
      }
      else {
        this.newTranslationList[key] = {
          key: key,
          newTrans: newTrans,
          oldTrans: oldTrans,
          newValid: null,
          oldValid: null,
        };
      }
    },
    clearGivenTranslation(key) {
      delete this.newTranslationList[key];
    },
    logValidation(key, newValid, oldValid) {
      if (key in this.newTranslationList) {
        this.newTranslationList[key].newValid = newValid;
        this.newTranslationList[key].oldValid = oldValid;
      }
      else {
        this.newTranslationList[key] = {
          key: key,
          newTrans: null,
          oldTrans: null,
          newValid: newValid,
          oldValid: oldValid,
        };
      }
    },
    thereIsUnsavedWork() {
      return Object.keys(this.newTranslationList).length > 0;
    },
    bodyScrollHeight() {
      return document.body.scrollHeight;
    },
    useFilter(filters) {
      this.filters = filters;
    },
    sendUpdatedTranslation(index, newTrans, newValid) {
      this.translationObjs[index].current_gloss = newTrans;
      this.translationObjs[index].current_verified = newValid;
    }
  },
  mounted: function () {
    this.loadTopLevelTags();
    this.getAllLocales();
  },
  beforeRouteLeave(to, from, next) {
    if (this.thereIsUnsavedWork()) {
      const userAnswer = window.confirm(this.$t("actions.unsaved-changes-lost"));
      next(userAnswer);
    }
    else {
      next();
    }
  },
};
</script>

<style scoped>
.ToolBox {
  position: fixed;
  width: 300px;
  height: 300px;
  right: 0;
  z-index: 2;
}
</style>
