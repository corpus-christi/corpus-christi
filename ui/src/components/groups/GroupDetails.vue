<template>
  <v-layout>
    <v-flex xs12>
      <v-card>
        <v-card-title primary-title>
          <div>
            <h3 class="headline mb-0">{{ group.name }}</h3>
            <div>{{ group.description }}</div>
            <div>Manager: {{ getManagerName() }}</div>
          </div>
        </v-card-title>

        <v-card-actions>
          <v-btn
            flat
            ripple
            color="primary"
            data-cy="navigate-to-members"
            v-on:click="navigateTo('/members')"
          >
            <v-icon>person</v-icon>&nbsp;{{ $t("groups.members.title") }}
          </v-btn>
          <v-btn
            flat
            ripple
            color="primary"
            data-cy="navigate-to-meetings"
            v-on:click="navigateTo('/meetings')"
          >
            <v-icon>devices_other</v-icon>&nbsp;{{
              $t("groups.meetings.title")
            }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-flex>
  </v-layout>
</template>

<script>
export default {
  name: "GroupDetails",
  data() {
    return {
      group: {},
      pageLoaded: false
    };
  },

  mounted() {
    this.pageLoaded = false;
    this.getGroup().then(() => {
      this.pageLoaded = true;
    });
  },

  methods: {
    getGroup() {
      const id = this.$route.params.group;
      return this.$http.get(`/api/v1/groups/groups/${id}`).then(resp => {
        this.group = resp.data;
      });
    },

    navigateTo(path) {
      this.$router.push({
        path: "/groups/" + this.$route.params.group + path
      });
    },

    getManagerName() {
      if(this.group.managerInfo){
        var man = this.group.managerInfo.person;
        return (
          man.firstName +
          " " +
          man.lastName +
          " " +
          (man.secondLastName ? man.secondLastName : "")
        );
      }
      return true;
    }
  }
};
</script>
