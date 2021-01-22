<template>
  <v-container>
    <v-tabs v-model="tab" color="primary" slider-color="accent">
      <v-tab ripple data-cy="person-table-tab">
        <v-icon>person</v-icon>
        &nbsp;{{ $t("people.title") }}
      </v-tab>
      <v-tab ripple data-cy="roles-table-tab">
        <v-icon>supervisor_account</v-icon>
        &nbsp;{{ $t("people.title-roles") }}
      </v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab">
      <v-tab-item>
        <PersonTable
          v-bind:peopleList="peopleList"
          v-bind:rolesList="rolesList"
          v-bind:tableLoaded="tableLoaded"
          v-on:fetchPeopleList="fetchPeopleList"
        />
      </v-tab-item>
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
import PersonTable from "../components/people/PersonTable";
import RolesTable from "../components/people/RolesTable";

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
