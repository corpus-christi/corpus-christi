<template>
  <v-container>
    <v-btn
      title="Show Toolbox"
      fab
      outlined
      right
      fixed
      depressed
      class="showToolBox"
      style="top: 80px; z-index: 2"
      @click="showToolBox = !showToolBox"
    >
      <v-icon>construction</v-icon>
    </v-btn>

    <ToolBox
      class="ToolBox mr-2 mt-1"
      elevation="2"
      v-show="showToolBox"
      :numTranslated="numEntriesTranslated"
      :numVerified="numEntriesVerified"
      :totalEntries="numEntriesTotal"
      :shouldBeShown="showToolBox"
      :filterOptions="[
        'translation.filters.untranslated',
        'translation.filters.unverified',
      ]"
      @hideToolBox="showToolBox = false"
      @sendFilters="useFilter"
      @addNewLocale="newLocaleDialog = true"
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
          ref="topLevelTagChooser"
          :topLevelTags="topLevelTags"
          :allTranslations="translationObjs"
          @tagsUpdated="onTopLevelTagsUpdated"
        />
      </v-col>

      <v-col>
        <v-card class="mb-1">
          <v-card-title>
            <v-row>
              <v-col>{{ $t("translation.tags.sub") }}</v-col>
              <v-col>{{ $t("translation.translate-from") }}</v-col>
              <v-col cols="1"></v-col>
              <v-col>{{ $t("translation.translate-to") }}</v-col>
              <v-col cols="3">{{ $t("translation.new-translation") }}</v-col>
              <v-col cols="1"><v-icon>check</v-icon></v-col>
            </v-row>
          </v-card-title>
        </v-card>
        <v-card
          class="overflow-y-auto"
          :height="calculateScreenHeight"
        >
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
        </v-card>
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
import { LocaleModel } from "@/models/Locale";
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
      showToolBox: false,
      loadingTranslations: false,
    };
  },
  computed: {
    ...mapState(["currentAccount"]),
    ...mapState(["currentLocale"]),
    numEntriesTranslated() {
      return this.translationObjs.filter((obj) => obj.current_gloss != "")
        .length;
    },
    numEntriesVerified() {
      return this.translationObjs.filter((obj) => obj.current_verified).length;
    },
    numEntriesTotal() {
      return this.translationObjs.length;
    },
    calculateScreenHeight() {
      console.log(this.screenHeight);
      return .7 * screen.height;
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
        .get(
          `api/v1/i18n/values/translations/${this.previewCode}/${this.currentCode}`
        )
        .then((resp) => {
          this.translationObjs = resp.data;
        })
        .catch((err) => console.log(err))
        .finally(() => (this.loadingTranslations = false));
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
      dance: for (
        let objNum = 0;
        objNum < this.translationObjs.length;
        objNum++
      ) {
        for (let tagNum = 0; tagNum < this.selectedTags.length; tagNum++) {
          if (
            this.selectedTags[tagNum] ==
            this.translationObjs[objNum].top_level_key
          ) {
            //focus on the v-text-field element
            this.focusOnFirstTag(this.translationObjs[objNum]);
            break dance;
          }
        }
      }
    },
    // eslint-disable-next-line
    focusOnFirstTag(cardObj) {},
    bodyScrollHeight() {
      return document.body.scrollHeight;
    },
    useFilter(filters) {
      this.filters = filters;
    },
    sendUpdatedTranslation(index, newTrans, newVerify) {
      this.translationObjs[index].current_gloss = newTrans;
      this.translationObjs[index].current_verified = newVerify;
      this.$refs.topLevelTagChooser.populateIncompleteCounts();
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
  width: 350px;
  height: 25%;
  right: 0;
  z-index: 2;
}
.dialog {
  overflow: hidden;
}
</style>
