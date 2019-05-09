<template>
  <v-container>
    <v-tabs color="transparent" slider-color="accent">
      <v-tab ripple data-cy="person-table-tab">
        <v-icon>person</v-icon>
        &nbsp;{{ $t("people.title") }}
      </v-tab>
      <v-tab-item>
        <PersonTable
          v-bind:peopleList="peopleList"
          v-bind:rolesList="rolesList"
          v-bind:tableLoaded="tableLoaded"
          v-on:fetchPeopleList="fetchPeopleList"
        />
      </v-tab-item>
      <v-tab ripple data-cy="roles-table-tab">
        <v-icon>supervisor_account</v-icon>
        &nbsp;{{ $t("people.title-roles") }}
      </v-tab>
      <v-tab-item>
        <RolesTable
          v-bind:peopleList="peopleList"
          v-bind:rolesList="rolesList"
          v-bind:tableLoaded="tableLoaded"
          v-on:fetchPeopleList="fetchPeopleList"
        />
      </v-tab-item>
    </v-tabs>
  </v-container>
</template>

<script>
import PersonTable from "../components/people/PersonTable";
import RolesTable from "../components/people/RolesTable";

export default {
  name: "People",
  components: {
    PersonTable,
    RolesTable
  },
  data() {
    return {
      peopleList: [],
      rolesList: [],
      tableLoaded: false
    };
  },

  methods: {
    fetchPeopleList() {
      this.tableLoaded = false;
      this.$http
        .get("/api/v1/people/persons?include_images=1")
        .then(resp => {
          console.log("FETCHED PEOPLE", resp);
          this.peopleList = resp.data;
          this.tableLoaded = true;
        })
        .catch(err => console.error("FAILURE", err.response));
    },

    fetchRolesList() {
      this.$http
        .get("/api/v1/people/role")
        .then(resp => {
          console.log("FETCHED ROLES", resp);
          let roles = [];
          for (var role of resp.data) {
            roles.push({
              text: role.nameI18n,
              value: role.id
            });
          }
          this.rolesList = roles;
        })
        .catch(err => console.error("FAILURE", err.response));
    }
  },

  mounted: function() {
    this.fetchRolesList();
    this.fetchPeopleList();
  }
};
</script>

<style scoped>
.vertical-spacer {
  margin-bottom: 16px;
}
</style>
