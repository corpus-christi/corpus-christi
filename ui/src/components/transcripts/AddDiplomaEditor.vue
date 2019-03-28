<template>
  <!-- https://codesandbox.io/s/mjy97x85py?from-embed -->
  <ValidationObserver ref="obs">
    <v-card slot-scope="{ invalid, validated }">
      <v-card-title>
        <span class="headline">{{ name }}</span>
      </v-card-title>
      <v-card-text>
        <v-form>
          <ValidationProvider name="select" rules="required">
            <v-select
              slot-scope="{ errors, valid }"
              v-model="diploma.id"
              :items="items"
              v-bind:label="$t('diplomas.diploma')"
              outline
              item-value="id"
              item-text="name"
              :success="valid"
              :menu-props="{ closeOnContentClick: true }"
              required
            ></v-select>
          </ValidationProvider>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-btn color="secondary" flat :disabled="saving" v-on:click="cancel">{{
          $t("actions.cancel")
        }}</v-btn>
        <v-spacer></v-spacer>
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
  name: "AddDiplomaEditor",

  components: {
    ValidationProvider,
    ValidationObserver
  },

  props: {
    diplomasThisStudent: Array,
    saving: {
      type: Boolean,
      default: false
    }
  },

  data: function() {
    return {
      diploma: {},
      diplomasPool: [] // courses for this diploma (the list of courses for this diploma)
    };
  },

  computed: {
    name() {
      return this.$t("diplomas.new");
    },
    items() {
      return this.diplomasPool.filter(
        diploma => !this.diplomasThisStudent.includes(diploma.id)
      );
    }
  },

  methods: {
    cancel() {
      //this.clear();
      this.diploma = {};
      this.$emit("cancel");
    },
    async save() {
      const result = await this.$refs.obs.validate();
      //console.log("result: ", result);
      if (result) {
        this.$refs.obs.reset();
        this.$emit("save", this.diploma);
      }
    }
  },

  mounted() {
    this.$http.get("/api/v1/courses/diplomas").then(resp => {
      this.diplomasPool = [];
      //console.log('diplomas fetched: ', resp);
      resp.data.forEach(diploma => {
        this.diplomasPool.push({
          name: diploma.name,
          id: diploma.id
        });
      });
      //console.log('diplomasPool: ', this.diplomasPool);
      this.$refs.obs.validate();
    });
  }
};
</script>
