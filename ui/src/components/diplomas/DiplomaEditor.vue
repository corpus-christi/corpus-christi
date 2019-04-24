<template>
  <!-- https://codesandbox.io/s/mjy97x85py?from-embed -->
  <v-card>
    <v-card-title>
      <span class="headline">{{ title }}</span>
    </v-card-title>
    <v-card-text>
      <form>
        <v-text-field
          v-model="diploma.name"
          v-bind:label="$t('diplomas.title')"
          name="title"
          v-validate="'required'"
          v-bind:error-messages="errors.collect('title')"
          data-cy="diplomas-form-name"
        ></v-text-field>
        <v-textarea
          v-model="diploma.description"
          v-bind:label="$t('diplomas.description')"
          name="description"
          v-validate="'required'"
          v-bind:error-messages="errors.collect('description')"
          data-cy="diploma-form-description"
        ></v-textarea>
        <br />
        <v-select
          v-model="diploma.courseList"
          :items="items"
          v-bind:label="$t('diplomas.courses')"
          chips
          deletable-chips
          clearable
          outline
          multiple
          hide-selected
          return-object
          item-value="id"
          item-text="name"
          :menu-props="{ closeOnContentClick: true }"
        ></v-select>
      </form>
    </v-card-text>
    <v-card-actions>
      <v-btn
        color="secondary"
        flat
        :disabled="formDisabled"
        v-on:click="cancel"
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
        :disabled="formDisabled"
        :loading="saveLoading"
        data-cy="form-save"
        v-on:click="save"
        >{{ $t("actions.save") }}</v-btn
      >
    </v-card-actions>
  </v-card>
</template>

<script>
import { isEmpty } from "lodash";

export default {
  name: "DiplomaEditor",
  props: {
    initialData: {
      type: Object,
      required: true
    },
    editMode: {
      type: Boolean,
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
      coursesPool: [], // courses for this diploma (the list of courses for this diploma)
      diploma: {},
      addMore: false
    };
  },

  computed: {
    title() {
      return this.editMode ? this.$t("actions.edit") : this.$t("diplomas.new");
    },
    items() {
      return this.coursesPool;
    },
    formDisabled() {
      return this.saveLoading || this.addMoreLoading;
    }
  },

  watch: {
    initialData(diplomaProp) {
      if (isEmpty(diplomaProp)) {
        this.clear();
      } else {
        this.diploma = diplomaProp;
      }
    }
  },

  methods: {
    cancel() {
      this.$emit("cancel");
    },

    clear() {
      this.diploma = {};
      this.$validator.reset();
    },

    addAnother() {
      this.addMore = true;
      this.save();
    },

    save() {
      this.$validator.validateAll().then(() => {
        if (!this.errors.any()) {
          this.$validator.reset();
          if (this.addMore) this.$emit("addAnother", this.diploma);
          else this.$emit("save", this.diploma);
        }
        this.addMore = false;
      });
    }
  },

  mounted() {
    this.$http
      .get("/api/v1/courses/courses")
      .then(resp => (this.coursesPool = resp.data));
  }
};
</script>
