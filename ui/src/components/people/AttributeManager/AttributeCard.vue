<template>
  <v-card>
    <v-card-title>
      <editable-text v-model="currentState.name" :edit-mode="inEditMode" />
      <v-spacer />
      <v-switch :disabled="!inEditMode" v-model="currentState.active" />
    </v-card-title>
    <v-card-subtitle>{{ $t(currentState.type) }}</v-card-subtitle>
    <v-card-text v-if="currentState.values.length > 0">
      <v-list-item v-for="(value, idx) in currentState.values" :key="idx">
        <v-list-item-content>
          <v-list-item-title>
            <editable-text v-model="value.label" :edit-mode="inEditMode" />
          </v-list-item-title>
        </v-list-item-content>
        <v-list-item-action>
          <v-switch :disabled="!inEditMode" v-model="value.active" />
        </v-list-item-action>
      </v-list-item>
    </v-card-text>
    <v-card-actions>
      <v-spacer />
      <v-btn text :disabled="inEditMode" @click="startEditing">
        {{ $t("edit") }}
      </v-btn>
      <v-btn text :disabled="!inEditMode" @click="cancelEditing">
        {{ $t("cancel") }}
      </v-btn>
      <v-btn text :disabled="!inEditMode" @click="saveEdits">
        {{ $t("save") }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import EditableText from "./EditableText";
import clone from "lodash/clone";

export default {
  name: "AttributeCard",

  components: {
    EditableText,
  },

  props: {
    name: { type: String, required: true },
    type: { type: String, required: true },
    active: { type: Boolean, required: true },
    values: { type: Array },
  },

  data() {
    return {
      inEditMode: false,

      currentState: {
        name: this.name,
        type: this.type,
        active: this.active,
        values: clone(this.values),
      },

      clonedState: null,
    };
  },

  methods: {
    startEditing() {
      this.clonedState = clone(this.currentState);
      this.inEditMode = true;
    },

    cancelEditing() {
      this.currentState = this.clonedState;
      this.inEditMode = false;
    },

    saveEdits() {
      this.inEditMode = false;
    },
  },
};
</script>
