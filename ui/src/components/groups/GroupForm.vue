<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ name }}</span>
    </v-card-title>
    <v-card-text>
      <form>
        <v-text-field
          v-model="group.name"
          v-bind:label="$t('groups.name')"
          name="title"
          v-validate="'required'"
          v-bind:error-messages="errors.first('')"
          data-cy="title"
        ></v-text-field>
        <v-textarea
          rows="3"
          v-model="group.description"
          v-bind:label="$t('groups.group-description')"
          name="description"
          data-cy="description"
        ></v-textarea>
        <entity-search
          manager
          v-model="group.manager"
          name="address"
          v-bind:error-messages="errors.first('address')"
        />
      </form>
    </v-card-text>
    <v-card-actions>
      <v-btn
        color="secondary"
        flat
        v-on:click="cancel"
        :disabled="formDisabled"
        data-cy="form-cancel"
        >{{ $t("actions.cancel") }}</v-btn
      >
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        outline
        v-on:click="addAnother"
        v-if="editMode === false"
        :loading="addMoreLoading"
        :disabled="formDisabled"
        data-cy="form-addanother"
        >{{ $t("actions.add-another") }}</v-btn
      >
      <v-btn
        color="primary"
        raised
        v-on:click="save"
        :loading="saveLoading"
        :disabled="formDisabled"
        data-cy="form-save"
        >{{ $t("actions.save") }}</v-btn
      >
    </v-card-actions>

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <v-btn flat @click="snackbar.show = false" data-cy>
        {{ $t("actions.close") }}
      </v-btn>
    </v-snackbar>
  </v-card>
</template>

<script>
import { isEmpty } from "lodash";
import { mapGetters } from "vuex";
import EntitySearch from "../EntitySearch";
export default {
  components: { "entity-search": EntitySearch },
  name: "GroupForm",
  watch: {
    initialData(groupProp) {
      if (isEmpty(groupProp)) {
        this.clear();
      } else {
        this.group = groupProp;
        this.group.manager = groupProp.managerInfo;
      }
    }
  },
  computed: {
    groupKeys() {
      return Object.keys(this.group);
    },

    name() {
      return this.editMode
        ? this.$t("groups.edit-group")
        : this.$t("groups.create-group");
    },

    formDisabled() {
      return this.saveLoading || this.addMoreLoading;
    },

    ...mapGetters(["currentLanguageCode"])
  },

  methods: {
    validateGroup(group, operation) {
      if(group.name == undefined || group.description == undefined || group.manager == undefined) {
        this.showSnackbar(this.$t("groups.messages.required-fields"));
      }
      else {
        this.$http.get(`/api/v1/groups/find_group/${group.name}/${group.manager.id}`).then((response) => {
          if(response.data == 0){
            this.$validator.validateAll().then(() => {
              operation();
            });
          }
          else {
            this.showSnackbar(this.$t("groups.messages.already-exists"));
          }
        });
      }
      
    },

    showSnackbar(message) {
      this.snackbar.text = message;
      this.snackbar.show = true;
    },

    cancel() {
      this.clear();
      this.$emit("cancel");
    },

    clear() {
      for (let key of this.groupKeys) {
        this.group[key] = "";
      }
      delete this.group.address;
      this.$validator.reset();
    },

    save() {
      this.validateGroup(this.group, () => {
        this.group.active = true;
          this.group.active = true;
          this.$emit("save", this.group);
      });
    },

    addAnother() {
      this.validateGroup(this.group, () => {
        this.group.active = true;
          this.$emit("add-another", this.group);
          this.group = {};
      });
    }
  },
  props: {
    editMode: {
      type: Boolean,
      required: true
    },
    initialData: {
      type: Object,
      required: true
    },
    saveLoading: {
      type: Boolean
    },
    addMoreLoading: {
      type: Boolean
    }
  },
  data: function() {
    return {
      group: {},
      snackbar: {
        show: false,
        text: ""
      },
    };
  }
};
</script>
