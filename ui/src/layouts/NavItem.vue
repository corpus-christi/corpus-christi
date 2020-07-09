<template>
  <div>
    <v-list-item
      v-if="!item.children || item.children.length === 0"
      :to="{ name: item.route }"
      :data-cy="item.route"
    >
      <v-list-item-action v-if="item.icon && !isChild">
        <v-icon>{{ item.icon }}</v-icon>
      </v-list-item-action>
      <v-list-item-title>{{ item.title }}</v-list-item-title>
    </v-list-item>
    <v-list-group v-else :sub-group="isChild" no-action>
      <v-list-item
        slot="activator"
        :to="{ name: item.route }"
        :data-cy="item.route"
      >
        <v-list-item-action v-if="item.icon && !isChild">
          <v-icon>{{ item.icon }}</v-icon>
        </v-list-item-action>
        <v-list-item-title>{{ item.title }}</v-list-item-title>
      </v-list-item>

      <NavItem
        v-for="child in item.children"
        :key="child.route"
        :item="child"
        :isChild="true"
      />
    </v-list-group>
  </div>
</template>

<script>
export default {
  name: "NavItem",
  props: {
    item: {
      type: Object,
      required: true,
    },
    isChild: {
      type: Boolean,
      default: false,
    },
  },
};
</script>
