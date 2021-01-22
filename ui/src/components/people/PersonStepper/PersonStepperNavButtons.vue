<template>
  <v-container>
    <v-row>
      <v-btn
        v-if="showCancelButton"
        color="secondary"
        text
        v-on:click="$emit('cancel')"
        data-cy="cancel"
        >{{ $t("actions.cancel") }}
      </v-btn>

      <v-spacer />

      <v-btn
        class="mr-2"
        v-if="showPreviousButton"
        color="primary"
        v-on:click="$emit('previous')"
        :disabled="isDisabled"
        data-cy="previous"
      >
        {{ $t("people.previous") }}
      </v-btn>

      <v-btn
        v-if="showNextButton"
        color="primary"
        v-on:click="$emit('next')"
        :disabled="isDisabled"
        data-cy="next"
      >
        {{ $t("people.next") }}
      </v-btn>

      <v-btn
        v-if="showSaveButton"
        color="primary"
        v-on:click="$emit('save')"
        :loading="isSavingActive"
        :disabled="isDisabled"
        data-cy="save"
      >
        {{ $t(saveButtonText) }}
      </v-btn>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: "PersonStepperNavButtons",

  props: {
    showCancelButton: {
      type: Boolean,
      default: true,
    },
    showNextButton: {
      type: Boolean,
      default: true,
    },
    showPreviousButton: {
      type: Boolean,
      default: true,
    },
    showSaveButton: {
      type: Boolean,
      default: false,
    },
    saveButtonText: {
      type: String,
      required: false,
      default: "actions.save",
    },
    isSavingActive: {
      type: Boolean,
      default: false,
    },
    isDisabled: {
      type: Boolean,
      required: true,
    },
  },
};
</script>
