<template>
  <v-container>
    <v-tabs color="transparent" slider-color="accent">
      <v-tab ripple>
        <v-icon>list</v-icon>&nbsp;{{ $t("events.details.title") }}
      </v-tab>
      <v-tab-item>
        <PersonTable v-bind:peopleList="peopleList" v-bind:rolesList="rolesList" v-on:fetchPeopleList="fetchPeopleList"/>
      </v-tab-item>
      <v-tab ripple>
        <v-icon>person </v-icon>&nbsp;{{ $t("events.participants.title") }}
      </v-tab>
      <v-tab-item> 
        <RolesTable v-bind:peopleList="peopleList" v-bind:rolesList="rolesList" v-on:fetchPeopleList="fetchPeopleList"/> 
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
      rolesList: []
    };
  },

  methods: {
    fetchPeopleList() {
      this.$http
        .get("/api/v1/people/persons")
        .then(resp => {
          console.log("FETCHED", resp);
          this.peopleList = resp.data;
          // this.activePeople = this.allPeople.filter(person => person.active);
          // this.archivedPeople = this.allPeople.filter(person => !person.active);
        })
        .catch(err => console.error("FAILURE", err.response));
    },

    fetchRolesList() {
      this.$http
        .get("/api/v1/people/role")
        .then(resp => {
          console.log("FETCHED", resp);
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
    this.fetchPeopleList();
    this.fetchRolesList();
  }
};
</script>

<style scoped>
.vertical-spacer {
  margin-bottom: 16px;
}
</style>
