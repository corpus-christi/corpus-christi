<template>
  <v-card>
    <v-card-text>
      <span class="headline">{{ $t("events.attendance") }}</span>
      <v-text-field
        data-cy="attendance-input"
        name="attendance"
        type="number"
        v-model="number"
        :placeholder="$t('events.attendance-label')"
        v-bind:error-messages="errors.first('attendance')"
        v-validate="'required|integer|min_value:0'"
      ></v-text-field>
    </v-card-text>
    <v-card-actions>
      <v-btn
        color="secondary"
        flat
        v-on:click="$emit('cancel')"
        :disabled="saving"
        data-cy="attendance-cancel"
        >{{ $t("actions.cancel") }}</v-btn
      >
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        v-on:click="changeAttendance"
        :loading="saving"
        data-cy="attendance-save"
        >{{ $t("actions.save") }}</v-btn
      >
    </v-card-actions>
  </v-card>
</template>
<script>
export default {
  name: "EventAttendanceForm",
  props: {
    attendance: {
      required: true
    },
    saving: {
      required: true,
      type: Boolean
    }
  },

  data() {
    return {
      number: null
    };
  },

  watch: {
    attendance(val) {
      this.number = val;
    }
  },

  methods: {
    changeAttendance() {
      this.$validator.validateAll().then(() => {
        if (!this.errors.any()) {
          this.$emit("save-attendance", this.number);
        }
      });
    }
  }
};
</script>
