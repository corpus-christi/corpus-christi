<template>
  <div>
    <v-toolbar flat>
      <v-toolbar-title>{{ $t("groups.treeview.title") }}</v-toolbar-title>
      <v-spacer />
      <v-btn color="primary" :to="{ name: 'all-groups' }">
        <v-icon>list</v-icon>
        {{ $t("groups.treeview.show-list") }}
      </v-btn>
      <template v-slot:extension>
        <v-tabs color="transparent" centered>
          <v-tab :to="{ name: 'group-treeview-category' }">
            Category View</v-tab
          >
          <v-tab :to="{ name: 'group-treeview-hierarchy' }">
            Hierarchy View</v-tab
          >
        </v-tabs>
      </template>
    </v-toolbar>
    <router-view />
  </div>
</template>
