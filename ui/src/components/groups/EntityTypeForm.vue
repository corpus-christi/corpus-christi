<template>
  <!-- reusable form to select or/and create group type or manager type in place -->
  <v-layout column justify-center align-space-around>
    <v-flex>
      <entity-search
        :disabled="entityTypePanel.show"
        :group-type="isGroupTypeMode"
        :manager-type="!isGroupTypeMode"
        v-bind:value="entityType"
        @input="$emit('input', $event)"
        v-bind="$attrs"
        :key="entitySearchKey"
      />
    </v-flex>
    <v-flex class="text-xs-center">
      <v-btn
        color="primary"
        flat
        small
        @click="showEntityTypePanel"
        :disabled="entityTypePanel.show"
      >
        {{ getTranslation("create-new") }}
      </v-btn>
    </v-flex>
    <v-flex>
      <v-expand-transition>
        <v-card elevation="1" v-if="entityTypePanel.show">
          <v-card-text>
            <v-text-field
              :label="getTranslation('name')"
              v-model="newEntityTypeName"
            ></v-text-field>
          </v-card-text>
          <v-card-actions>
            <v-btn small flat @click="hideEntityTypePanel">{{
              $t("actions.close")
            }}</v-btn>
            <v-spacer />
            <v-btn small flat color="primary" @click="createEntityType">{{
              $t("actions.save")
            }}</v-btn>
          </v-card-actions>
        </v-card>
      </v-expand-transition>
    </v-flex>
  </v-layout>
</template>
<script>
import EntitySearch from "../EntitySearch";
import { pick } from "lodash";
export default {
  name: "EntityTypeForm",
  components: { EntitySearch },
  props: {
    entityTypeName: {
      /* either groupType or managerType */
      type: String,
      default: "groupType"
    },
    value: {
      /* { id: ..., name: ... } */
      type: Object
    }
  },
  watch: {
    value(newValue) {
      this.entityType = newValue;
    }
  },
  methods: {
    getTranslation(key) {
      return this.$t(
        `groups.entity-types.${
          this.isGroupTypeMode ? "group-types" : "manager-types"
        }.${key}`
      );
    },
    showEntityTypePanel() {
      this.entityTypePanel.show = true;
    },
    hideEntityTypePanel() {
      this.entityTypePanel.show = false;
    },
    createEntityType() {
      this.$http
        .post(this.endpoint, { name: this.newEntityTypeName })
        .then(resp => {
          this.hideEntityTypePanel();
          this.newEntityTypeName = "";
          this.entitySearchKey = resp.data.id; // reload entity-search
          this.entityType = pick(resp.data, ["id", "name"]); // notify child
          this.$emit("input", this.entityType); // notify parent
        });
    }
  },
  computed: {
    isGroupTypeMode() {
      return this.entityTypeName == "groupType";
    },
    endpoint() {
      return `/api/v1/groups/${
        this.isGroupTypeMode ? "group-types" : "manager-types"
      }`;
    }
  },
  data() {
    return {
      newEntityTypeName: "",
      entityType: {},
      entityTypePanel: {
        show: false
      },
      entitySearchKey: 0 // used to re-render the component
    };
  }
};
</script>
