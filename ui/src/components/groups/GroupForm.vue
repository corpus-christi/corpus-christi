//add grooup button content
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
          v-bind:error-messages="errors.first('title')"
          data-cy="title"
        />
        <v-textarea
          rows="3"
          v-model="group.description"
          v-bind:label="$t('groups.group-description')"
          name="description"
          v-validate="'required'"
          v-bind:error-messages="errors.collect('description')"
          data-cy="description"
        />
        <entity-search
          manager
          :value="manager"
          @input="updateSelection"
          name="manager"
          v-bind:error-messages="errors.first('manager')"
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
        >{{ $t("actions.cancel") }}ttt</v-btn
      >
      <v-spacer />
      <v-btn
        color="primary"
        outline
        v-on:click="addAnother"
        v-if="!editMode"
        :loading="addMoreLoading"
        :disabled="formDisabled"
        data-cy="form-addanother"
        >{{ $t("actions.add-another") }}qqqqq
      </v-btn>
      <v-btn
        color="primary"
        raised
        v-on:click="save"
        :loading="saveLoading"
        :disabled="formDisabled"
        data-cy="form-save"
        >{{ $t("actions.save") }}hhhh <!-- save botton - Add group -->
      </v-btn>
    </v-card-actions>

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <v-btn flat @click="snackbar.show = false" data-cy>
        {{ $t("actions.close") }}wwww
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
        this.manager = this.parseGroup(this.group);
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
    getManagerName(managerInfo) {
      var man = managerInfo.person;
      return (
        man.firstName +
        " " +
        man.lastName +
        " " +
        (man.secondLastName ? man.secondLastName : "")
      );
    },

    parseGroup(obj) {
      return {
        id: obj.managerId
      };
    },

    updateSelection(obj) {
      if (obj.person) {
        this.group.managerId = obj.id;
        if (!this.group.manager) this.group.manager = {};
        this.group.manager.person = obj.person;
        if (!this.group.managerInfo) this.group.managerInfo = {};
        this.group.managerInfo.person = obj.person;
      }
      //console.log("updateSelection");
      //console.log(this.group);
    },

    validateGroup(group, operation) {
      //console.log(group);
      //console.log(group.manager.person);
      this.$validator.validateAll().then(isValid => {
        if (isValid) {
          this.$http
            .get(`/api/v1/groups/find_group/${group.name}/${group.manager.person.id}`)
            .then(response => {
              if (response.data == 0) {
                operation();
                console.log("reachinng ---");
              } else {
                this.showSnackbar(this.$t("groups.messages.already-exists"));
              }
            });
        }
      });
    },

    showSnackbar(message) {
      this.snackbar.text = message;
      this.snackbar.show = true;
    },

    cancel() {
      this.clear();
      this.$validator.reset();
      this.$emit("cancel");
      this.manager = {};
    },

    clear() {
      for (let key of this.groupKeys) {
        this.group[key] = "";
      }
      delete this.group.address;
      this.$validator.reset();
    },

    save() { //save add group
      //console.log(this.group);
      //console.log(this.group);
      this.validateGroup(this.group, () => {
        this.group.active = true;
        //this.group.active = true;
        this.$emit("save", this.group);//where is this sending to?
      });
      this.manager = {};
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
      manager: {},
      snackbar: {
        show: false,
        text: ""
      }
    };
  }
};
</script>
