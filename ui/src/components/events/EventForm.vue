<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ editMode ? "Edit Event" : "Create Event" }}</span>
    </v-card-title>
    <v-card-text>
      <form>
        <v-text-field
          v-model="event.name"
          label="Event Name"
          name="name"
          v-validate="'required'"
          v-bind:error-messages="errors.collect('name')"
        ></v-text-field>
      </form>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <!-- <v-btn color="primary" flat v-on:click="cancel">
        {{ $t("actions.cancel") }}
      </v-btn>
      <v-btn color="primary" flat v-on:click="clear">
        {{ $t("actions.clear") }}
      </v-btn>-->
      <v-btn color="primary" flat v-on:click="save">{{ $t("actions.save") }}</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import { isEmpty } from "lodash";

export default {
  name: "EventForm",
  watch: {
    // Make sure data stays in sync with any changes to `initialData` from parent.
    initialData(eventProp) {
      if (isEmpty(eventProp)) {
        this.clear();
      } else {
        this.event = eventProp;
      }
    }
  },
  computed: {
    // List the keys in an Event record.
    eventKeys() {
      return Object.keys(this.person);
    }
  },
  methods: {
    // Clear the form and the validators.
    clear() {
      for (let key of this.eventKeys) {
        this.event[key] = "";
      }
      this.$validator.reset();
    },
    save() {
      this.$validator.validateAll();
      if (!this.errors.any()) {
        this.$emit("save", this.event);
      }
    }
  },
  props: {
    editMode: {
      type: Boolean,
      required: true
    },
    initialData: {
      type: Object,
      required: true
    }
  },
  data: function() {
    return {
      event: {}
    };
  }
};
</script>