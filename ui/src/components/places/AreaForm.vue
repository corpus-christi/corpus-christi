<template>
  <v-card>
    <v-card-text>
      <span class="headling">{{ $t("places.area.create-area") }}</span>
      <v-layout column>
        <v-text-field
          name="area"
          v-model="area.name"
          v-bind:label="$t('places.area.name')"
          :disabled="formDisabled"
        ></v-text-field>

        <v-layout row>
          <v-flex>
            <v-autocomplete
              name="country_code"
              v-model="area.country_code"
              v-bind:label="$t('places.address.country')"
              :disabled="formDisabled"
              :items="dropdownList"
            ></v-autocomplete>
          </v-flex>
        </v-layout>
      </v-layout>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn
        flat
        color="secondary"
        @click="cancelAreaForm"
        :disabled="formDisabled"
        >{{ $t("actions.cancel") }}</v-btn
      >
      <v-btn
        raised
        color="primary"
        @click="saveAreaForm"
        :loading="formDisabled"
        :disabled="formDisabled"
        >{{ $t("actions.save") }}</v-btn
      >
    </v-card-actions>
  </v-card>
</template>

<script>
export default {
  name: "AreaForm",
  props: {
    initialData: {
      type: Object,
      required: true,
    },
    countries: {
      type: Array,
    },
  },
  data: function () {
    return {
      area: {
        id: 0,
        name: "",
        country_code: "",
      },
      formDisabled: false,
      saveIsLoading: false,
    };
  },
  computed: {
    dropdownList() {
      return this.countries.map((element) => {
        return {
          text: this.$t(element.name_i18n),
          value: element.code,
        };
      });
    },
  },
  watch: {
    // Make sure data stays in sync with any changes to `initialData` from parent.
    initialData(areaProp) {
      this.area = areaProp;
    },
  },
  methods: {
    cancelAreaForm() {
      // emit false to close form
      this.$emit("cancel", false);
    },
    saveAreaForm() {
      this.saveArea("saved");
    },
    saveArea(emitMessage) {
      let areaId = this.area.id;
      let areaData = {
        name: this.area.name,
        country_code: this.area.country_code,
      };
      if (areaId) {
        this.updateArea(areaData, areaId, emitMessage);
      } else {
        this.addArea(areaData, emitMessage);
      }
    },
    addArea(areaData, emitMessage) {
      this.$http
        .post("/api/v1/places/areas", areaData)
        .then((resp) => {
          this.$emit(emitMessage, resp.data);
          console.log(areaData);
        })
        .then(() => {
          this.formDisabled = false;
          this.cancelAreaForm();
        })
        .catch((err) => {
          console.log("FAILED", err);
          this.formDisabled = false;
        });
    },
    updateArea(areaData, areaId, emitMessage) {
      console.log(areaData);
      console.log(areaId);
      this.$http
        .put(`/api/v1/places/areas/${areaId}`, areaData)
        .then((resp) => {
          this.$emit(emitMessage, resp.data);
        })
        .then(() => {
          this.formDisabled = false;
          this.cancelAreaForm();
        })
        .catch((err) => {
          console.log("FAILED", err);
          this.formDisabled = false;
        });
    },
  },
};
</script>
