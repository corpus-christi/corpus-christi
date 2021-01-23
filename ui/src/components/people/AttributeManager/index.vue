<template>
  <v-container>
    <v-toolbar class="mb-4">
      <v-toolbar-title>{{ $t("people.attributes") }}</v-toolbar-title>
      <v-spacer />
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
    <v-row justify="left">
      <v-col cols="6" v-for="attr in allAttributes" :key="attr.name">
        <attribute-card
          :name="attr.name"
          :type="attr.type"
          :active="attr.active"
          :values="attr.values || []"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import AttributeCard from "./AttributeCard";

export default {
  name: "Attributes",

  components: { AttributeCard },

  data() {
    return {
      newType: "",

      attributeTypes: [
        { i18nKey: "attribute.checkbox", enumerated: true },
        { i18nKey: "attribute.date", enumerated: false },
        { i18nKey: "attribute.dropdown", enumerated: true },
        { i18nKey: "attribute.float", enumerated: false },
        { i18nKey: "attribute.integer", enumerated: false },
        { i18nKey: "attribute.radio", enumerated: true },
        { i18nKey: "attribute.string", enumerated: false },
      ],

      allAttributes: [
        {
          name: "Alpha",
          type: "attribute.date",
          active: true,
        },
        {
          name: "Service",
          type: "attribute.radio",
          active: true,
          values: [
            { label: "Sunday 9:00", active: true },
            { label: "Sunday 11:00", active: true },
            { label: "Saturday 5:30", active: false },
          ],
        },
        {
          name: "Baptism",
          type: "attribute.date",
          active: true,
        },
        {
          name: "Gamma",
          type: "attribute.date",
          active: true,
        },
        {
          name: "Nineteen",
          type: "attribute.date",
          active: true,
        },
      ],
    };
  },
};
</script>
