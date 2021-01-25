<template>
  <v-container>
    <v-toolbar class="mb-4">
      <v-toolbar-title>{{ $t("people.attributes") }}</v-toolbar-title>
      <v-spacer />
      <v-switch
        class="mr-2"
        hide-details
        color="primary"
        :label="$t('people.rearrange')"
        @change="dragEnabled = !dragEnabled"
      />
      <v-menu>
        <template v-slot:activator="{ on }">
          <v-btn color="primary" v-on="on">
            <v-icon left>playlist_add</v-icon>
            {{ $t("people.add-attribute") }}
          </v-btn>
        </template>
        <v-list>
          <v-list-item v-for="(type, idx) in attributeTypes" :key="idx">
            <v-list-item-title>{{ $t(type.i18nKey) }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-toolbar>
    <draggable v-model="allAttributes" class="row" :disabled="!dragEnabled">
      <v-col cols="6" v-for="attr in allAttributes" :key="attr.name">
        <attribute-card
          :name="$t(attr.nameI18n)"
          :type="attr.typeI18n"
          :active="attr.active"
          :values="attr.enumerated_values || []"
          :dragEnabled="dragEnabled"
        />
      </v-col>
    </draggable>
  </v-container>
</template>

<script>
import AttributeCard from "./AttributeCard";
import draggable from "vuedraggable";

export default {
  name: "Attributes",

  components: {
    AttributeCard,
    draggable,
  },

  data() {
    return {
      attributeTypes: [],
      allAttributes: [],
      newType: null,
      dragEnabled: false,
    };
  },

  mounted() {
    this.$http
      .get("/api/v1/attributes/attribute-types")
      .then((resp) => (this.attributeTypes = resp.data));
    this.$http
      .get("/api/v1/attributes/attributes")
      .then((resp) => (this.allAttributes = resp.data));
  },
};
</script>
