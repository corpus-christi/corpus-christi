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
      fab
      dark
      fixed
      top
      right
      color="dense"
      @click="toBottom"
    >
      <v-icon>keyboard_arrow_down</v-icon>
    </v-btn>

    <v-btn
      class="mb-7"
      v-scroll="onScroll"
      v-show="fab"
      fab
      dark
      fixed
      bottom
      right
      color="dense"
      @click="toTop"
    >
      <v-icon>keyboard_arrow_up</v-icon>
    </v-btn>

    <v-row>
      <!-- Top Level Tag -->
      <v-col cols="2">
        <v-card-text>
          <v-list 
            elevation="2"
            rounded
          >
            <v-list-item-group
              color="grey darken-4"
              multiple
            >
              <v-list-item
                v-for="(tag, index) in wip.topLevelTags"
                :key="index"
                v-text="tag"
                @change="addSelectedTag(tag)"
              >
              </v-list-item>
            </v-list-item-group>
          </v-list>
        </v-card-text>
      </v-col>

      <v-divider vertical></v-divider>
      
      <!-- Rest of tag and other stuff -->
      <v-col>
        <template>
        <!-- v-for="tag in wip.translationDetails"
            v-if="tag.top_level_key in wip.selectedTags" -->
          <v-card 
            outlined
            class="d-flex align-center ml-3 mt-4 mr-3"
            elevation="2"
            v-for="(detail, i) in wip.cardDetails"
            :key="i"
          >
            <v-card
              min-width=19.7%
              max-width=19.7%
              elevation="0"
              class="ml-1"
            >
              <v-card-text>
                {{ detail.rest_of_key }}
              </v-card-text>
            </v-card>
            
            <v-card
              min-width=20.5%
              max-width=20.5%
              elevation="0"
              outlined
            >
              <v-card-text>
                {{ detail.preview_gloss }}
              </v-card-text>
            </v-card>

            <v-card
              min-width=1%
              elevation="0"
            >
              <v-icon>
                keyboard_arrow_right
              </v-icon>
            </v-card>

            <v-card
              min-width=20.5%
              max-width=20.5%
              elevation="0"
              outlined
            >
              <v-card-text>
                {{ detail.current_gloss }}
              </v-card-text>
            </v-card>

            <!-- SPACER -->
            <v-card
              min-width=7%
            ></v-card>

            <v-card
              min-width=20%
              max-width=20%
              elevation="0"
            >
              <v-card
                min-width=80%
                max-width=80%
                elevation="0"
              >
                <v-text-field>
                </v-text-field>
              </v-card>
            </v-card>

            <!-- SPACER -->
            <v-card
              min-width=3.7%
            ></v-card>

            <v-card
              min-width=1%
              max-width=1%
              elevation="0"
            >
              <v-checkbox
                class=" align-self-center"
                v-model="detail.current_verified"
              >
              </v-checkbox>
            </v-card>
          </v-card>
        </template>
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

    <!-- Edit translation Dialog-->
    <!-- <v-dialog v-model="changeTranslationDialog" persistent max-width="400">
      <v-card>
        <v-col cols="12">
          <v-text-field
            v-model="updateTR"
            :label="dialogInitialText"
            single-line
            outlined
          ></v-text-field>
        </v-col>
        <v-card-actions>
          <v-tooltip bottom>
            <template v-slot:activator="{ on }">
              <v-btn small v-on="on" v-on:click="hideDialog"
                ><v-icon>cancel</v-icon></v-btn
              >
            </template>
            <span>{{ $t("translation.dialog.cancel") }}</span>
          </v-tooltip>
          <v-spacer />
          <v-tooltip bottom>
            <template v-slot:activator="{ on }">
              <v-btn small v-on="on" v-on:click="update()">{{
                $t("translation.dialog.submit")
              }}</v-btn>
            </template>
          </v-tooltip>
        </v-card-actions>
      </v-card>
    </v-dialog> -->
  </v-container>
</template>


<script>
import { mapState } from "vuex";
import { eventBus } from "../plugins/event-bus.js";
const _ = require("lodash");
export default {
  name: "Translation",
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
    // https://vuejs.org/v2/guide/list.html
    // 'wip.selectedTags': {
    //   handler: function(someValue) {
    //     // console.log(`Value: ${someValue}`);
    //     // console.log(this.wip.selectedTags);
    //   },
    //   deep: true
    // }
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
      console.log(selection);
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
    getTranslationDetails() {
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
      //Sorting
      //console.log(this.wip.cardDetails);
      //console.log(this.wip.selectedTags);
    },
    deleteCards(tag){
      console.log(this.wip.cardDetails)
      for(let i = 0 ; i < this.wip.cardDetails.length;i++){
        if (this.wip.cardDetails[i].top_level_key == tag) {
          this.wip.cardDetails.splice(i, 1);
          i--;
        }
      }
      console.log(this.wip.cardDetails);
      console.log(this.wip.selectedTags);
    }
  },
  mounted: function () {
    this.loadTopLevelTags();
    this.getAllLocales();
    this.getTranslationDetails();
    this.fillAllCards();
  },
  beforeRouteLeave(to, from, next) {
    // If there are unsaved changes,
    //  Do not let the user leave without prompting
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
