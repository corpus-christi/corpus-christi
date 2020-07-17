<template>
  <v-row>
    <v-col xs12 sm4>
      <v-card>
        <v-card-title primary-title>
          <div>
            <h3 class="headline mb-0">
              {{ $t("groups.details.class-title") }}: {{ group.name }}
            </h3>
            <div>{{ group.description }}</div>
          </div>
          Group
        </v-card-title>
      </v-card>

      <v-card class="mt-2" v-if="pageLoaded">
        <v-card-title primary-title>
          <div>
            <h3 class="headline mb-0">{{ $t("groups.details.title") }}</h3>
            <div>{{ $t("groups.manager") }}: {{ getManagerName() }}</div>
            <div>
              {{ $t("groups.details.member-count") }}:
              {{ group.members.length }}
            </div>
          </div>
        </v-card-title>
      </v-card>
    </v-col>
  </v-row>
</template>

<script>
export default {
  name: "GroupDetails",
  data() {
    return {
      group: {},
      pageLoaded: false,
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
      return this.$http.get(`/api/v1/groups/groups/${id}`).then((resp) => {
        this.group = resp.data;
      });
    },

    navigateTo(path) {
      this.$router.push({
        path: "/groups/" + this.$route.params.group + path,
      });
    },

    getManagerName() {
      if (this.group.managerInfo) {
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
    },
  },
};
</script>
