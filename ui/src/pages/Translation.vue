<template>
  <v-container>
    <v-btn
      outlined right fixed depressed
      class="showToolBox"
      style="top: 180px; z-index: 2; transform: rotate(90deg);"
      min-width="10%" min-height="5%"
      @click="showToolBox = !showToolBox"
    >
      {{ $t("translation.toolbox.show") }}
    </v-btn>

    <transition name="fade">
      <ToolBox class="ToolBox mr-2 mt-1"
        elevation="2"
        v-show="showToolBox"
        :numTranslated="numEntriesTranslated"
        :numValidated="numEntriesValidated"
        :totalEntries="numEntriesTotal"
        :shouldBeShown="showToolBox"
        :filterOptions="[
          'translation.filters.untranslated',
          'translation.filters.unverified']"
        @goToTop="$vuetify.goTo(0)"
        @goToBot="$vuetify.goTo(bodyScrollHeight())"
        @hideToolBox="showToolBox = false"
        @sendFilters="useFilter"
        @addNewLocale="newLocaleDialog=true"
      />
    </transition>

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
          @submitAChange="sendUpdatedTranslation"
        />
      </v-col>
    </v-row>

    <NewLocaleDialog
      :showDialog="newLocaleDialog"
      @submitComplete="newLocaleSuccessfullyAdded"
      @closeDialog="newLocaleDialog = false"
    />
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
import NewLocaleDialog from "../components/i18n/NewLocaleDialog.vue";
const _ = require("lodash");

export default {
  name: "Translation",
  components: {
    WorkbenchHeader,
    TopLevelTagChooser,
    TranslationCard,
    ToolBox,
    NewLocaleDialog,
  },
  data() {
    return {
      topLevelTags: [],
      selectedTags: [],
      allLocaleObjs: [],
      translationObjs: [],

      previewCode: "",
      currentCode: "",
      
      newLocaleDialog: false,
      filters: [],
      showToolBox: true,
      loadingTranslations: false,
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
      this.findFirstTag();
    },
    findFirstTag() {
      //find the first tag
      dance:
      for(let objNum = 0; objNum < this.translationObjs.length; objNum++){
        for(let tagNum = 0; tagNum < this.selectedTags.length; tagNum++){
          if(this.selectedTags[tagNum] == this.translationObjs[objNum].top_level_key){
            //focus on the v-text-field element
            this.focusOnFirstTag(this.translationObjs[objNum]);
            break dance;
          }
        }
      }
    },
    // eslint-disable-next-line
    focusOnFirstTag(cardObj) {
      
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
    },
    newLocaleSuccessfullyAdded(newLocaleObj) {
      let newLocale = new LocaleModel(newLocaleObj);
      this.allLocaleObjs.push({
        code: newLocale.languageAndCountry,
        displayString: newLocale.flagAndDescription,
      });
      this.newLocaleDialog = false;
    },
  },
  mounted: function () {
    this.loadTopLevelTags();
    this.getAllLocales();
  },
};
</script>

<style scoped>
.ToolBox {
  position: fixed;
  width: 300px;
  height: 30%;
  right: 0;
  z-index: 2;
}
.dialog {
  overflow: hidden;
}
/* From https://vuejs.org/v2/guide/transitions.html */
.fade-enter-active, .fade-leave-active {
  transition: opacity .5s;
}
.fade-enter, .fade-leave-to /* .fade-leave-active below version 2.1.8 */ {
  opacity: 0;
}
</style>
