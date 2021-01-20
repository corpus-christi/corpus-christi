<template>
  <v-row>
    <v-btn
      color="secondary"
      text
      v-on:click="cancel"
      :disabled="formDisabled"
      data-cy="cancel"
      >{{ $t("actions.cancel") }}
    </v-btn>
    <v-spacer />
    <v-btn color="primary" raised v-on:click="previous" data-cy="previous">
      {{ $t("people.previous") }}
    </v-btn>
    <v-btn color="primary" raised v-on:click="next" data-cy="next">
      {{ $t("people.next") }}
    </v-btn>
  </v-row>
</template>

<script>
export default {
  name: "PersonStepperNavButtons",
};
</script>

<style scoped></style>
