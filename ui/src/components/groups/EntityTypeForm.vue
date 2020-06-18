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
        {{
          isGroupTypeMode
            ? "create a new group type"
            : "create a new manager type"
        }}
      </v-btn>
    </v-flex>
    <v-flex>
      <v-expand-transition>
        <v-card v-if="entityTypePanel.show">
          <v-card-text>
            <v-text-field
              :label="newEntityTypeTextLabel"
              v-model="newEntityTypeName"
            ></v-text-field>
          </v-card-text>
          <v-card-actions>
            <v-btn small flat @click="hideEntityTypePanel">Close</v-btn>
            <v-btn small flat color="primary" @click="createEntityType"
              >Save</v-btn
            >
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
    },
    newEntityTypeTextLabel() {
      return this.isGroupTypeMode ? "group type name" : "manager type name";
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
