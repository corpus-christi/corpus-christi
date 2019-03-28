<template>
  <!-- https://codesandbox.io/s/mjy97x85py?from-embed -->
  <ValidationObserver ref="obs">
    <v-card slot-scope="{ invalid, validated }">
      <v-card-title>
        <span class="headline">{{ name }}</span>
      </v-card-title>
      <v-card-text>
        <v-form>
          <ValidationProvider name="Name" rules="required|max:128">
            <v-text-field
              slot-scope="{ errors }"
              v-model="diploma.name"
              :counter="128"
              :error-messages="errors"
              v-bind:label="$t('diplomas.title')"
              name="name"
              required
            ></v-text-field>
          </ValidationProvider>
          <v-textarea
            v-model="diploma.description"
            v-bind:label="$t('diplomas.description')"
            name="description"
          ></v-textarea>

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
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-btn color="secondary" flat :disabled="saving" v-on:click="cancel">{{
          $t("actions.cancel")
        }}</v-btn>
        <v-spacer></v-spacer>
        <v-btn color="primary" flat :disabled="saving" v-on:click="clear">{{
          $t("actions.clear")
        }}</v-btn>
        <v-btn
          color="primary"
          raised
          :disabled="saving || invalid || !validated"
          :loading="saving"
          v-on:click="save"
          >{{ $t("actions.save") }}</v-btn
        >
      </v-card-actions>
    </v-card>
  </ValidationObserver>
</template>

<script>
import { ValidationObserver, ValidationProvider } from "vee-validate";

export default {
  name: "DiplomaEditor",

  components: {
    ValidationProvider,
    ValidationObserver
  },

  props: {
    diploma: Object,
    saving: {
      type: Boolean,
      default: false
    },
    editMode: {
      type: Boolean,
      required: true
    }
  },

  data: function() {
    return {
      coursesPool: [] // courses for this diploma (the list of courses for this diploma)
    };
  },

  computed: {
    name() {
      return this.editMode ? this.$t("actions.edit") : this.$t("diplomas.new");
    },
    items() {
      return this.coursesPool;
    }
  },

  methods: {
    cancel() {
      this.clear();
      this.$emit("cancel");
    },

    async clear() {
      this.$refs.obs.reset();
      this.$emit("clearForm");
      /*
      this.$nextTick(() => {
        this.$refs.obs.reset();
      });
      */
    },
    async save() {
      const result = await this.$refs.obs.validate();
      console.log("result: ", result);
      if (result) {
        //this.$validator.reset();
        this.$refs.obs.reset();
        this.$emit("save", this.diploma);
      }
    }
  },

  mounted() {
    this.$http
      .get("/api/v1/courses/courses")
      .then(resp => (this.coursesPool = resp.data));
  }
};
</script>
