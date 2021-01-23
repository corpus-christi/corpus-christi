<template>
  <v-card :color="cardColor">
    <v-card-title>
      <v-icon v-if="dragEnabled">drag_indicator</v-icon>
      <editable-text v-model="currentState.name" :edit-mode="inEditMode" />
      <v-spacer />
      <v-switch :disabled="!inEditMode" v-model="currentState.active" />
    </v-card-title>
    <v-card-subtitle>{{ $t(currentState.type) }}</v-card-subtitle>
    <v-card-text v-if="currentState.values.length > 0">
      <draggable v-model="currentState.values">
        <v-list-item v-for="(value, idx) in currentState.values" :key="idx">
          <v-list-item-content>
            <v-list-item-title>
              <editable-text
                v-model="value.label"
                :edit-mode="inEditMode"
                draggable
              />
            </v-list-item-title>
          </v-list-item-content>
          <v-list-item-action>
            <v-switch :disabled="!inEditMode" v-model="value.active" />
          </v-list-item-action>
        </v-list-item>
      </draggable>
    </v-card-text>
    <v-card-actions>
      <v-spacer />
      <v-btn text :disabled="inEditMode || dragEnabled" @click="startEditing">
        {{ $t("edit") }}
      </v-btn>
      <v-btn
        text
        color="warning"
        :disabled="!inEditMode"
        @click="cancelEditing"
      >
        {{ $t("cancel") }}
      </v-btn>
      <v-btn text color="primary" :disabled="!inEditMode" @click="saveEdits">
        {{ $t("save") }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import EditableText from "./EditableText";
import cloneDeep from "lodash/cloneDeep";
import draggable from "vuedraggable";

export default {
  name: "AttributeCard",

  components: {
    EditableText,
    draggable,
  },

  props: {
    name: { type: String, required: true },
    type: { type: String, required: true },
    active: { type: Boolean, required: true },
    values: { type: Array },
    dragEnabled: { type: Boolean, default: false },
  },

  data() {
    return {
      inEditMode: false,

      currentState: {
        name: this.name,
        type: this.type,
        active: this.active,
        values: cloneDeep(this.values),
      },

      clonedState: null,
    };
  },

  computed: {
    cardColor() {
      return this.currentState.active ? "white" : "grey lighten-3";
    },
  },

  methods: {
    startEditing() {
      this.clonedState = cloneDeep(this.currentState);
      this.inEditMode = true;
    },

    cancelEditing() {
      this.currentState = this.clonedState;
      this.inEditMode = false;
    },

    saveEdits() {
      this.clonedState = null;
      this.inEditMode = false;
    },
  },
};
</script>
