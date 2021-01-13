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
      left
      color="dense"
      @click="toBottom"
    >
      <v-icon>keyboard_arrow_down</v-icon>
    </v-btn>

    <v-btn
      v-scroll="onScroll"
      v-show="fab"
      fab
      dark
      fixed
      bottom
      left
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
                :class="{ 'active': index === 0 }"
              >
              </v-list-item>
            </v-list-item-group>
          </v-list>
        </v-card-text>
      </v-col>

      <v-divider vertical></v-divider>
      
      <!-- Rest of tag and other stuff -->
      <v-col>
        <!--  v-for="(obj,index) in wip.tags"
          :key="index"
          v-text="obj" -->
          
        <v-card 
          outlined
          class="d-flex align-center ml-3 mt-4 mr-3"
          elevation="2"
        >
          <v-card
            min-width=19.7%
            max-width=19.7%
            elevation="0"
            class="ml-1"
          >
            <v-card-text>
              Joe Mama
            </v-card-text>
          </v-card>
          
          <v-card
            min-width=20.5%
            max-width=2-.5%
            elevation="0"
            outlined
          >
            <v-card-text>
              Joe Mama
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
              Joe Mama
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
            >
            </v-checkbox>
          </v-card>
        </v-card>
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
          min-width="80%"
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
      wip: {
        translationDetails: [],
        tags: [],
        topLevelTags: [],
        localeObjs: [],
        localesConcat: [],
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
        this.loadAllTranslations();
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
    getTreeLeaves() {
      for (let L1 of Object.keys(this.translation)) {
        this.items.push({
          id: this.counter,
          name: L1,
          children: [],
        });
        this.counter += 1;
        this.getExtensions(
          L1,
          this.translation[L1],
          this.items[this.items.length - 1].children,
          L1 + "."
        );
      }
    },
    getExtensions(name, subtree, container, key_id) {
      for (let leaf of Object.keys(subtree)) {
        if (container === undefined) {
          console.log("reach end");
        } else if (typeof subtree[leaf] === "object") {
          container.push({
            id: this.counter,
            name: leaf,
            children: [],
          });
          this.counter += 1;
          this.getExtensions(
            leaf,
            subtree[leaf],
            container[container.length - 1].children,
            key_id + leaf + "."
          );
        } else if (typeof subtree[leaf] === "string") {
          container.push({
            id: this.counter,
            name: leaf,
            children: [],
          });
          this.counter += 1;
          container[container.length - 1].children.push({
            id: this.counter,
            name: subtree[leaf],
            key_id: key_id + leaf,
          });
          this.counter += 1;
        }
      }
    },
    loadAllTranslations() {
      let locale =
        this.currentLocale.languageCode + "-" + this.currentLocale.countryCode;
      this.storedLocale =
        this.currentLocale.languageCode + "-" + this.currentLocale.countryCode;
      return this.$http
        .get(`api/v1/i18n/values/${locale}?format=tree`)
        .then((resp) => {
          this.translation = resp.data;
        })
        .then(() => this.getTreeLeaves());
    },
    loadTopLevelTags() {
      return this.$http
        .get(`api/v1/i18n/keys`)
        .then((resp) => {
          resp.data.forEach((obj) => {
            // this.wip.tags.map(obj);
            this.wip.topLevelTags.push(obj.id.split('.')[0]);
          });
          this.wip.topLevelTags = _.uniq(this.wip.topLevelTags).sort();
        })
        .then(()=>{
          this.getAllLowLevelKeyObjects();
        });
    },
    getAllLowLevelKeyObjects(){
      return this.$http
        .get(`api/v1/i18n/values`)
        .then((response)=>{
          this.wip.tags = response.data.map((obj) => {
            return {
              top_level_id:   obj.key_id.split('.')[0],
              full_id:        obj.key_id,
              locale_code:    obj.locale_code,
              gloss:          obj.gloss,
              verified:       obj.verified,
            }
          });
        });
    },
    getAllLocales() {
      return this.$http
        .get(`api/v1/i18n/locales`)
        .then((resp) => {
          this.wip.localeObjs = resp.data;
          this.wip.localesConcat = resp.data.map((obj) => obj.code + " " + obj.desc);
        });
    },
    getTranslationDetails() {
      let previewLocale = 'en-US'; //Probably set to this.wip.preview.code
      let currentLocale = 'es-EC'; //Probably set to this.wip.current.code

      return this.$http
        .get(`api/v1/i18n/values/translations/${previewLocale}/${currentLocale}`)
        .then((resp) => {
          this.wip.translationDetails = resp.data;
          console.log(resp.data[0]);
        })
        .catch((err) => console.log(err));
    },
  },
  mounted: function () {
    // this.loadAllTranslations();
    this.loadTopLevelTags();
    this.getAllLocales();
    this.getTranslationDetails();
  },
};
</script>

<style scoped></style>
