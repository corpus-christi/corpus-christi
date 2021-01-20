<template>
  <v-container>
    
    <ToolBox class="ToolBox"
      
    />
    <WorkbenchHeader
      :allLocales="allLocaleObjs"
      :loadingTranslations="loadingTranslations"
      @previewUpdated="onPreviewLocaleChanged"
      @currentUpdated="onCurrentLocaleChanged"
      @updateTransToFrom="fetchNewTranslations"
    />

    <!-- <v-btn
      class="mt-13"
      v-scroll="onScroll"
      v-show="fabToBot"
      fab dark fixed top right
      color="dense"
      @click="$vuetify.goTo(bodyScrollHeight)"
    >
      <v-icon>keyboard_arrow_down</v-icon>
    </v-btn>

    <v-btn
      class="mb-7"
      v-scroll="onScroll"
      v-show="fabToTop"
      fab dark fixed bottom right
      color="dense"
      @click="$vuetify.goTo(0)"
    >
      <v-icon>keyboard_arrow_up</v-icon>
    </v-btn> -->

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
          :topLevelTag="card.top_level_key"
          :restOfTag="card.rest_of_key"
          :previewGloss="card.preview_gloss"
          :currentGloss="card.current_gloss"
          :currentVerified="card.current_verified"
          :selectedTags="selectedTags"
          @TranslationChanged="getNewTranslation"
          @AppendToList="appendTranslation"
        />
      </v-col>
    </v-row>

    <v-row fixed bottom>
      <v-app-bar color="white" elevation="2">
        <v-card min-width="60%" />
        <!-- For testing "changes must be saved" feature -->
        <v-btn min-width="15%"
          @click="canUserLeaveFreely = !canUserLeaveFreely"
        >
          {{freelyLeaveButtonText}}
        </v-btn>

        <v-card min-width="2%" />

        <v-dialog
          v-model="dialog"
          scrollable
          width="500"
        >
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              min-width="9%"
              color="red lighten-2"
              dark
              v-bind="attrs"
              v-on="on"
            >
              Submit
            </v-btn>
          </template>

          <v-card>
            <v-card-title class="headline black lighten-2 white--text">
              You are about to submit {{Object.keys(newTranslationList).length}} changes!
            </v-card-title>
            <v-card-text>
              <v-radio-group
                v-for="(items, index) in newTranslationList"
                :key="index"
                v-text="index + ' ' + items.oldTrans + '   >   ' + items.newTrans"
                column
              >
              </v-radio-group>
                
            </v-card-text>

            <v-divider></v-divider>

            <v-spacer></v-spacer>
            <v-card-actions>
              
              <v-btn
                color="red lighten-2"
                text
                @click="dialog=false"
              >
                Submit
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

        

        <v-card min-width="2%" />

        <v-btn min-width="9%">
          Activate
        </v-btn>
      </v-app-bar>
    </v-row>

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

      topLevelTags: [],
      selectedTags: [],
      allLocaleObjs: [],
      translationObjs: [],
      previewCode: "",
      currentCode: "",
      newTranslation: "",
      changedKey: "",
      loadingTranslations: false,
      newTranslationList: {},
    };
  },
  computed: {
    ...mapState(["currentAccount"]),
    ...mapState(["currentLocale"]),
    // "Changes must be saved before leaving" feature-to-be
    freelyLeaveButtonText() {
      return this.canUserLeaveFreely ? "Leave without issue" : "Prompt b/f leaving";
    },
    bodyScrollHeight() {
      return document.body.scrollHeight;
    },
  },
  methods: {
    onScroll(e) {
      if (typeof window === "undefined") return;
      const top = window.pageYOffset || e.target.scrollTop || 0;
      this.fabToTop = top > 20;
      this.fabToBot = top < this.bodyScrollHeight - window.innerHeight - 20;
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
    getNewTranslation(key, newTrans, oldTrans) {
      this.changedKey = key;
      this.newTranslation = newTrans;
      this.oldTranslation = oldTrans;
    },
    appendTranslation() {
      let tempKey = this.changedKey;
      if (tempKey in this.newTranslationList) {
        this.newTranslationList[tempKey].newTrans = this.newTranslation;
      }
      else {
        let tempDict = {};
        tempDict.key = tempKey;
        tempDict.newTrans = this.newTranslation;
        tempDict.oldTrans = this.oldTranslation;
        this.newTranslationList[tempKey] = tempDict;
      }
    },
  },
  mounted: function () {
    this.loadTopLevelTags();
    this.getAllLocales();
  },
  beforeRouteLeave(to, from, next) {
    if (!this.canUserLeaveFreely) {
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
    width:300px;
    height: 20%;
    right: 0;
    z-index: 2
  }
</style>
