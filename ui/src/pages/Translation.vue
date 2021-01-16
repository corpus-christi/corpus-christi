<template>
  <v-container>
    <v-app-bar dense dark height="60">
      <!--{{ titleLocale }}-->
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
          <v-select
            :items="wip.localesConcat"
            v-bind:label="wip.preview.desc"
            v-model="wip.defaultPreview"
            class="mt-5"
          ></v-select>
        </v-col>
        <v-icon>keyboard_arrow_right</v-icon>
        <v-col cols="2">
          <v-select
            :items="wip.localesConcat"
            v-bind:label="wip.current.desc"
            class="mt-5"
          ></v-select>
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

    <v-btn
      class="mt-13"
      v-scroll="onScroll"
      v-show="baf"
      fab dark fixed top right
      color="dense"
      @click="toBottom"
    >
      <v-icon>keyboard_arrow_down</v-icon>
    </v-btn>

    <v-btn
      class="mb-7"
      v-scroll="onScroll"
      v-show="fab"
      fab dark fixed bottom right
      color="dense"
      @click="toTop"
    >
      <v-icon>keyboard_arrow_up</v-icon>
    </v-btn>

    <v-row>
      <!-- Top Level Tag -->
      <v-col cols="2">
        <TopLevelTagChooser 
          :topLevelTags="wip.topLevelTags"
          @tagsUpdated="onTopLevelTagsUpdated"
        />
      </v-col>

      <v-divider vertical></v-divider>
      
      <!-- Rest of tag and other stuff -->
      <v-col>
        <TranslationCard
          v-for="(card, index) in wip.translationDetails"
          :key="index"
          :topLevelTag="card.top_level_key"
          :restOfTag="card.rest_of_key"
          :previewGloss="card.preview_gloss"
          :currentGloss="card.current_gloss"
          :currentVerified="card.current_verified"
          :selectedTags="wip.selectedTags"
        />
      </v-col>
    </v-row>

    <v-row
      fixed
      bottom
    >
      <v-app-bar   
        color="white"
        elevation="2"     
      >
        <v-card
          min-width="60%"
        > 
        </v-card>
        <!-- For testing 'changes must be saved' feature -->
        <v-btn
          min-width="15%"
          @click="canUserLeaveFreely = !canUserLeaveFreely" 
        >
          {{freelyLeaveButtonText}}
        </v-btn>
        <v-card
          min-width="2%"
        > 
        </v-card>
        <v-btn
          min-width="9%"
        >
          Submit
        </v-btn>
        <v-card
          min-width="2%"
        > 
        </v-card>
        <v-btn
          min-width="9%"
        >
          Activate
        </v-btn>
      </v-app-bar>
    </v-row>
  </v-container>
</template>


<script>
import { mapState } from "vuex";
import { eventBus } from "../plugins/event-bus.js";
import TranslationCard from "../components/i18n/TranslationCard.vue";
import TopLevelTagChooser from "../components/i18n/TopLevelTagChooser.vue";
const _ = require("lodash");
export default {
  name: "Translation",
  components: {
    TranslationCard,
    TopLevelTagChooser,
  },
  data() {
    return {
      translation: null,
      counter: 1,
      items: [],
      storedLocale: null,
      open: true,
      tree: [],
      changeTranslationDialog: false,
      dialogInitialText: null,
      updateTR: null,
      selected_key_id: null,
      search: null,
      fab: false,
      baf: true,
      isActive: false,
      canUserLeaveFreely: false,
      wip: {
        translationDetails: [],
        selectedTags: [],
        cardDetails: [],
        tags: [],
        topLevelTags: [],
        localeObjs: [],
        localesConcat: [],
        defaultPreview: null,
        preview: {"code": "n/a", "desc": "Translate From"},
        current: {"code": "n/a", "desc": "Translate To"},
      },
    };
  },
  computed: {
    ...mapState(["currentAccount"]),
    ...mapState(["currentLocale"]),
    titleLocale() {
      return (
        this.currentLocale.languageCode + "-" + this.currentLocale.countryCode
      );
    },
    // For testing 'changes must be saved' feature
    freelyLeaveButtonText() {
      return this.canUserLeaveFreely ? "Leave without issue" : "Prompt b/f leaving";
    }
  },
  watch: {
    titleLocale() {
      if (
        this.currentLocale.languageCode +
          "-" +
          this.currentLocale.countryCode !=
        this.storedLocale
      ) {
        console.log(
          "New Locale",
          this.currentLocale.languageCode + "-" + this.currentLocale.countryCode
        );
      }
    },
  },
  methods: {
    onScroll(e) {
      if (typeof window === "undefined") return;
      const top = window.pageYOffset || e.target.scrollTop || 0;
      this.fab = top > 20;
      this.baf = top < document.body.scrollHeight - window.innerHeight - 20;
    },
    toTop() {
      this.$vuetify.goTo(0);
    },
    toBottom() {
      this.$vuetify.goTo(document.body.scrollHeight)
    },
    change(selection) {
      this.dialogInitialText = selection.name;
      this.changeTranslationDialog = true;
      this.selected_key_id = selection.key_id;
      // console.log(selection);
    },
    hideDialog() {
      this.changeTranslationDialog = false;
    },
    update() {
      this.changeTranslationDialog = false;
      let payload = {
        key_id: this.selected_key_id,
        locale_code: this.storedLocale,
        gloss: this.updateTR,
      };
      return this.$http
        .patch(`api/v1/i18n/values/update`, payload)
        .then((resp) => {
          eventBus.$emit("message", {
            content: "translation.updated",
          });
          console.log(resp.data);
        })
        .catch((err) => {
          console.log(err);
          eventBus.$emit("error", {
            content: "translation.error",
          });
        });
    },
    loadTopLevelTags() {
      return this.$http
        .get(`api/v1/i18n/keys`)
        .then((resp) => {
          resp.data.forEach((obj) => {
            // this.wip.tags.map(obj);
            obj.active = false;
            this.wip.topLevelTags.push(obj.id.split('.')[0]);
          });
          this.wip.topLevelTags = _.uniq(this.wip.topLevelTags).sort();
        })
        .catch((err) => console.log(err));
    },
    getAllLocales() {
      return this.$http
        .get(`api/v1/i18n/locales`)
        .then((resp) => {
          this.wip.localeObjs = resp.data;
          this.wip.localesConcat = resp.data.map((obj) => obj.flag + " " + obj.desc);
          this.wip.defaultPreview = this.wip.localesConcat[0];
        });
    },
    fetchAllTranslations() {
      let previewLocale = 'en-US'; //Eventually come from this.wip.preview.code
      let currentLocale = 'es-EC'; //Eventually come from this.wip.current.code

      return this.$http
        .get(`api/v1/i18n/values/translations/${previewLocale}/${currentLocale}`)
        .then((resp) => {
          this.wip.translationDetails = resp.data;
          console.log(resp.data[0]);
        })
        .catch((err) => console.log(err));
    },
    addSelectedTag(tag) {
      if (this.wip.selectedTags.indexOf(tag) == -1) {
        this.wip.selectedTags.push(tag);
        this.fillAllCards();
      }
      else {
        this.wip.selectedTags.splice(
          this.wip.selectedTags.indexOf(tag), 1
        );
        this.deleteCards(tag);
      }
    },
    fillAllCards(){
      this.wip.cardDetails = [];
      this.wip.translationDetails.forEach((details) => {
        if (this.wip.selectedTags.includes(details.top_level_key)) {
          this.wip.cardDetails.push(details);
        }
      });
    },
    deleteCards(tag){
      for(let i = 0 ; i < this.wip.cardDetails.length;i++){
        if (this.wip.cardDetails[i].top_level_key == tag) {
          this.wip.cardDetails.splice(i, 1);
          i--;
        }
      }
    },
    onTopLevelTagsUpdated(tagList) {
      this.wip.selectedTags = tagList;
    },
  },
  mounted: function () {
    this.loadTopLevelTags();
    // this.getAllLocales();
    this.fetchAllTranslations();
    // this.fillAllCards();
  },
  beforeRouteLeave(to, from, next) {
    // If there are unsaved changes, do not let the user leave without prompting
    if (!this.canUserLeaveFreely) {
      const userAnswer = window.confirm(this.$t("actions.unsaved-changes-lost"));
      next(userAnswer);
    }
    else {
      next();
    }
  }
};
</script>

<style scoped></style>
