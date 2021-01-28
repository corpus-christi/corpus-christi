<template>
  <v-tooltip bottom>
    <template v-slot:activator="{ on }">
      <v-btn
        icon
        outlined
        small
        class="mr-1"
        color="primary"
        v-on="on"
        @click="$emit('click')"
      >
        <v-icon small>{{ iconName }}</v-icon>
      </v-btn>
    </template>
    <span>{{ tooltipText }}</span>
  </v-tooltip>
</template>

<script>
export default {
  name: "ActionIconButton",
  props: {
    iconName: {
      type: String,
      required: true,
    },
    tooltipText: {
      type: String,
      required: true,
    },
  },
};
</script>
