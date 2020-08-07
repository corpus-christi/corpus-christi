<template>
  <v-container>
    <v-app-bar
      dense
      dark>
    <v-toolbar-title>
      {{ $t("translation.toolbar-title") }} {{ titleLocale }}
    </v-toolbar-title>
    </v-app-bar>
    <v-row>
      <v-col>
        <v-card-text>
          <v-treeview
            activatable
            :items="items"
            v-model="tree"
            selected-color="indigo"
            :open-on-click="open"
            selectable
            return-object
          ></v-treeview>
        </v-card-text>
      </v-col>
      <v-divider vertical></v-divider>
      <v-col
        cols="12"
        md="6"
      >
        <v-card-text>
          <v-scroll-x-transition
            group
            hide-on-leave
          >
            <v-chip
              v-for="(selection, i) in tree"
              :key="i"
              color="grey"
              dark
              small
              class="ma-1"
              v-on:click="change(selection)"
            >
              <v-icon left small>mdi-beer</v-icon>
              {{ selection.name }}
            </v-chip>
          </v-scroll-x-transition>
        </v-card-text>
      </v-col>
    </v-row>

    <!-- Edit translation Dialog-->
    <v-dialog v-model="changeTranslationDialog" persistent max-width="400">
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
              <v-btn
                small
                v-on="on"
                v-on:click="hideDialog"
              ><v-icon>cancel</v-icon></v-btn
              >
            </template>
            <span>{{ $t("translation.dialog.cancel") }}</span>
          </v-tooltip>
          <v-spacer />
          <v-tooltip bottom>
            <template v-slot:activator="{ on }">
              <v-btn
                small
                v-on="on"
                v-on:click="update()"
              >{{ $t("translation.dialog.submit") }}</v-btn
              >
            </template>
          </v-tooltip>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
  import { mapState } from "vuex";
    export default {
      name: "Translation",
      data() {
        return {
          translation: null,
          counter: 1,
          items: [],
          storedLocale: null,
          open: true,
          tree:[],
          changeTranslationDialog: false,
          dialogInitialText: null,
          updateTR: null,
          selected_key_id: null
        };
      },
      computed:{
        ...mapState(["currentAccount"]),
        ...mapState(["currentLocale"]),
        titleLocale(){
          return this.currentLocale.languageCode + "-" + this.currentLocale.countryCode;
        },
      },
      watch:{
        titleLocale(){
          if (this.currentLocale.languageCode + "-" + this.currentLocale.countryCode != this.storedLocale){
            console.log("New Locale",this.currentLocale.languageCode + "-" + this.currentLocale.countryCode);
            this.loadAllTranslation();
          }
        }
      },
      methods:{
        change(selection){
          this.dialogInitialText = selection.name
          this.changeTranslationDialog = true;
          this.selected_key_id=selection.key_id;
          console.log(selection)
        },
        hideDialog(){
          this.changeTranslationDialog = false;
        },
        update(){
          console.log(this.updateTR);
          this.changeTranslationDialog = false;
          let payload = {key_id: this.selected_key_id, locale_code: this.storedLocale, gloss: this.updateTR}
          //send the request here
          return this.$http.patch(`api/v1/i18n/values/update`, payload).then((resp) => {
            console.log(resp.data)
          });
        },
        getTreeLeaves(){
          for (let L1 of Object.keys(this.translation)){
            this.items.push({
              id: this.counter,
              name: L1,
              children:[]
            })
            this.counter+=1;
            this.getExtensions(L1, this.translation[L1], this.items[this.items.length-1].children, L1 +'.')
          }
        },
        getExtensions(name, subtree, container, key_id){
          for (let leaf of Object.keys(subtree)){
            if (container === undefined){
              console.log("reach end");
            }
            else if ((typeof subtree[leaf]) === "object"){
              container.push({
                id: this.counter,
                name: leaf,
                children:[]
              })
              this.counter+=1;
              this.getExtensions(leaf, subtree[leaf], container[container.length-1].children, key_id+leaf)
            }
            else if ((typeof subtree[leaf]) === "string"){
              container.push({
                id: this.counter,
                name: leaf,
                children:[]
              })
              this.counter+=1;
              container[container.length-1].children.push({
                id: this.counter,
                name: subtree[leaf],
                key_id: key_id+'.'+leaf
              })
              this.counter+=1;
            }
          }
          },
        loadAllTranslation(){
          let locale = this.currentLocale.languageCode + "-" + this.currentLocale.countryCode;
          this.storedLocale = this.currentLocale.languageCode + "-" + this.currentLocale.countryCode;
          return this.$http.get(`api/v1/i18n/values/${locale}?format=tree`).then((resp) => {
            this.translation =resp.data;
          }).then(() => this.getTreeLeaves());
        }
      },
      mounted: function () {
        this.loadAllTranslation();
      },
    }
</script>

<style scoped>

</style>
