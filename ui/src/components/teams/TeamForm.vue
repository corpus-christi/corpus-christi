<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ title }}</span>
    </v-card-title>
    <v-card-text>
      <form>
        <v-textarea
          rows="3"
          v-model="team.description"
          v-bind:label="$t('teams.description')"
          name="team-description"
          v-validate="'required'"
          v-bind:error-messages="errors.collect('team-description')"
          data-cy="description"
        ></v-textarea>
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
        v-if="!editMode"
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
  </v-card>
</template>

<script>
import { isEmpty } from "lodash";
// import { mapGetters } from "vuex";
export default {
  name: "TeamForm",
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
      team: {},
      addMore: false
    };
  },

  watch: {
    // Make sure data stays in sync with any changes to `initialData` from parent.
    initialData(teamProp) {
      if (isEmpty(teamProp)) {
        this.clear();
      } else {
        this.team = teamProp;
      }
    }
  },
  computed: {
    // List the keys in an Team record.
    teamKeys() {
      return Object.keys(this.team);
    },
    title() {
      return this.editMode
        ? this.$t("teams.edit-team")
        : this.$t("teams.create-team");
    },

    formDisabled() {
      return this.saveLoading || this.addMoreLoading;
    }

    // ...mapGetters(["currentLanguageCode"])
  },

  methods: {
    cancel() {
      this.$emit("cancel");
    },

    // Clear the form and the validators.
    clear() {
      for (let key of this.teamKeys) {
        this.team[key] = "";
      }

      this.$validator.reset();
    },

    addAnother() {
      this.addMore = true;
      this.save();
    },

    save() {
      this.$validator.validateAll().then(() => {
        if (!this.errors.any()) {
          this.team.active = true;
          if (this.addMore) this.$emit("addAnother", this.team);
          else this.$emit("save", this.team);
        }
        this.addMore = false;
      });
    }
  }
};
</script>
