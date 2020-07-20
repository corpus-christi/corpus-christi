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
        <v-tabs centered>
          <v-tab :to="{ name: 'group-treeview-category' }">
            {{ $t("groups.treeview.category-view") }}
          </v-tab>
          <v-tab :to="{ name: 'group-treeview-hierarchy' }">
            {{ $t("groups.treeview.hierarchy-view") }}</v-tab
          >
        </v-tabs>
      </template>
    </v-toolbar>
    <router-view />
  </div>
</template>
