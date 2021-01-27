<template>
  <v-container>
    <!-- Create the Tabs -->
    <v-tabs v-model="tab" color="primary" slider-color="accent">
      <!-- People Tab -->
      <v-tab ripple data-cy="person-table-tab">
        <v-icon>person</v-icon>
        &nbsp;{{ $t("people.title") }}
      </v-tab>
      <!-- Roles Tab -->
      <v-tab ripple data-cy="roles-table-tab">
        <v-icon>supervisor_account</v-icon>
        &nbsp;{{ $t("people.title-roles") }}
      </v-tab>
    </v-tabs>
    <!-- Populate the Tabs -->
    <v-tabs-items v-model="tab">
      <!-- Table of People -->
      <v-tab-item>
        <PersonTable
          v-bind:peopleList="peopleList"
          v-bind:rolesList="rolesList"
          v-bind:tableLoaded="tableLoaded"
          v-on:fetchPeopleList="fetchPeopleList"
        />
      </v-tab-item>
      <!-- Table of Roles -->
      <v-tab-item>
        <RolesTable
          v-bind:peopleList="peopleList"
          v-bind:rolesList="rolesList"
          v-bind:tableLoaded="tableLoaded"
          v-on:fetchPeopleList="fetchPeopleList"
        />
      </v-tab-item>
    </v-tabs-items>
  </v-container>
</template>

<script>
/**
 * @file
 * @name People.vue
 */
import PersonTable from "../components/people/PersonTable";
import RolesTable from "../components/people/RolesTable";

/**
 * @module
 * @name People
 * @exports ../router.js
 * Draws the /people page. More content available in ui/src/components/people
 */
export default {
  name: "People",
  components: {
    PersonTable,
    RolesTable,
  },
  data() {
    return {
      tab: null,
      peopleList: [],
      rolesList: [],
      tableLoaded: false,
    };
  },

  methods: {
    fetchPeopleList() {
      this.tableLoaded = false;
      this.$http
        .get("/api/v1/people/persons?include_images=1")
        .then((resp) => {
          console.log("GET");
          console.log(resp.data);
          this.peopleList = resp.data;
          this.tableLoaded = true;
        })
        .catch((err) => console.error("FAILURE", err.response));
    },

    fetchRolesList() {
      this.$http
        .get("/api/v1/people/role")
        .then((resp) => {
          let roles = [];
          for (const role of resp.data) {
            roles.push({
              text: role.nameI18n,
              value: role.id,
            });
          }
          this.rolesList = roles;
        })
        .catch((err) => console.error("FAILURE", err.response));
    },
  },

  mounted: function () {
    this.fetchRolesList();
    this.fetchPeopleList();
  },
};
</script>
