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
      <template #activator="{ props: activatorProps }">
        <v-list-item
          v-bind="activatorProps"
          :to="{ name: item.route }"
          :data-cy="item.route"
        >
          <v-list-item-action v-if="item.icon && !isChild">
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-item-action>
          <v-list-item-title>{{ item.title }}</v-list-item-title>
        </v-list-item>
      </template>

      <NavItem
        v-for="child in item.children"
        :key="child.route"
        :item="child"
        :isChild="true"
      />
    </v-list-group>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  item: {
    title: string;
    route: string;
    icon?: string;
    divider?: boolean;
    children?: Array<{ title: string; route: string }>;
  };
  isChild?: boolean;
}>();
</script>
