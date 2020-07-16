<template>
  <div>
    <v-layout column>
      <v-layout row wrap>
        <v-flex xs12>
          <v-card class="ma-1">
            <v-container fill-height fluid>
              <v-flex xs9 sm9 align-end flexbox>
                <span class="headline">
                  <b>{{ $t("groups.name") }}: </b>{{ group.name }}</span
                >
              </v-flex>
              <v-layout xs3 sm3 align-end justify-end>
                <v-btn flat color="primary">
                  <v-icon>edit</v-icon>&nbsp;{{ $t("actions.edit") }}
                </v-btn>
              </v-layout>
            </v-container>
          </v-card>
        </v-flex>
      </v-layout>
    </v-layout>

    <v-layout column>
      <v-layout row wrap>
        <v-flex xs12>
          <v-card class="ma-1">
            <v-container fill-height fluid>
              <v-flex xs9 sm9 align-end flexbox>
                <span>
                  <b>{{ $t("groups.group-type") }}: </b>
                  {{ group.groupType.name }}
                </span>
                <span>
                  <b>{{ $t("groups.description") }}: </b>
                  {{ group.description }}
                </span>
              </v-flex>
            </v-container>
          </v-card>
        </v-flex>
      </v-layout>
    </v-layout>

    <!-- New/Edit dialog
    <v-dialog v-model="groupDialog.show" max-width="500px" persistent>
      <group-form
        v-bind:editMode="groupDialog.editMode"
        v-bind:initialData="groupDialog.group"
        v-bind:saveLoading="groupDialog.saveLoading"
        v-bind:addMoreLoading="groupDialog.addMoreLoading"
        v-on:cancel="cancelGroup"
        v-on:save="saveGroup"
        v-on:add-another="addAnotherGroup"
      />
    </v-dialog>
    -->
    <!--
    <v-toolbar>
      <v-btn fab x-small @click="prev">
              <v-icon small>mdi-chevron-left</v-icon>
            </v-btn>
            <v-btn fab small @click="next">
              <v-icon small>mdi-chevron-right</v-icon>
            </v-btn>
     </v-toolbar>
    <v-row>
      <v-col>
        <v-sheet height="400">
          <v-calendar
            ref="calendar"
            :value="today"
            :events="events"
            color="primary"
            type="month"
          ></v-calendar>
        </v-sheet>
      </v-col>
    </v-row>
 -->
  </div>
</template>

<script>
export default {
  name: "GroupDetails",

  events: [
    {
      name: "Weekly Meeting",
      start: "2020-07-07 09:00",
      end: "2020-07-07 10:00",
    },
    {
      name: "Thomas' Birthday",
      start: "2020-07-10",
    },
    {
      name: "Mash Potatoes",
      start: "2020-07-09 12:30",
      end: "2020-07-09 15:30",
    },
  ],
  data() {
    return {
      group: {},
      pageLoaded: false,
      groupDialog: {
        show: false,
        editMode: false,
        saveLoading: false,
        addMoreLoading: false,
        editingGroupId: null,
        group: {},
      },
    };
  },

  mounted() {
    this.$refs.calendar.scrollToTime("08:00");
    this.pageLoaded = false;
    this.getGroup().then(() => {
      this.pageLoaded = true;
    });
    this.$refs.calendar.scrollToTime("08:00");
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
    prev() {
      this.$refs.calendar.prev();
    },
    next() {
      this.$refs.calendar.next();
    },
  },
};
</script>
