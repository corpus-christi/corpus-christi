<template>
  <v-card :color="cardColor">
    <v-card-title>
      <v-icon v-if="dragEnabled">drag_indicator</v-icon>
      <editable-text v-model="currentState.name" :edit-mode="inEditMode" />
      <v-spacer />
      <v-switch :disabled="!inEditMode" v-model="currentState.active" />
    </v-card-title>

    <v-card-subtitle>{{ currentState.type }}</v-card-subtitle>

    <v-card-text v-if="currentState.enumeratedValues.length > 0">
      <draggable v-model="currentState.enumeratedValues">
        <v-list-item
          v-for="(enumeratedValue, idx) in currentState.enumeratedValues"
          :key="idx"
        >
          <v-list-item-content>
            <v-list-item-title>
              <editable-text
                v-model="enumeratedValue.value"
                :edit-mode="inEditMode"
                draggable
              />
            </v-list-item-title>
          </v-list-item-content>
          <v-list-item-action>
            <v-btn
              v-if="enumeratedValue.value.length === 0"
              text
              small
              @click="removeValue(idx)"
            >
              <v-icon>clear</v-icon>
            </v-btn>
            <v-switch
              v-else
              :disabled="!inEditMode"
              v-model="enumeratedValue.active"
            />
          </v-list-item-action>
        </v-list-item>
      </draggable>
      <v-row justify="center">
        <v-btn v-if="inEditMode" icon @click="addValue">
          <v-icon>add_circle</v-icon>
        </v-btn>
      </v-row>
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
    enumeratedValues: { type: Array },
    dragEnabled: { type: Boolean, default: false },
  },

  data() {
    return {
      inEditMode: false,

      currentState: {
        name: this.name,
        type: this.type,
        active: this.active,
        enumeratedValues: cloneDeep(this.enumeratedValues),
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
      this.currentState.enumeratedValues = this.currentState.enumeratedValues.filter(
        (v) => v.value.length > 0
      );
    },

    addValue() {
      this.currentState.enumeratedValues.push({
        value: "",
        active: false,
      });
    },

    removeValue(idx) {
      this.currentState.enumeratedValues.splice(idx, 1);
    },
  },
};
</script>
