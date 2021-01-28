<template>
  <div>
    <v-row column>
      <v-row row wrap>
        <v-col xs12>
          <v-card class="ma-1">
            <v-container fill-height fluid>
              <v-col xs9 sm9 align-end flexbox v-if="group">
                <span class="headline">
                  <b>{{ $t("groups.name") }}: </b>{{ group.name }}</span
                >
              </v-col>
            </v-container>
          </v-card>
        </v-col>
      </v-row>
    </v-row>

    <v-row column>
      <v-row row wrap>
        <v-col xs12>
          <v-card class="ma-1">
            <v-container fill-height fluid>
              <v-col xs9 sm9 align-end flexbox v-if="group">
                <span>
                  <b>{{ $t("groups.group-type") }}: </b>
                  {{ group.groupType.name }}
                </span>
                <br />
                <span>
                  <b>{{ $t("groups.description") }}: </b>
                  {{ group.description }}
                </span>
              </v-col>
            </v-container>
          </v-card>
        </v-col>
      </v-row>
    </v-row>

    <!-- Calander -->
    <v-row>
      <v-col>
        <v-toolbar v-if="$refs.calendar">
          <v-btn fab x-small @click="prev">
            <v-icon small>navigate_before</v-icon>
          </v-btn>
          <v-spacer />
          <v-toolbar-title>{{ $refs.calendar.title }}</v-toolbar-title>
          <v-spacer />
          <v-btn fab small @click="next">
            <v-icon small>navigate_next</v-icon>
          </v-btn>
        </v-toolbar>
        <v-sheet height="400">
          <v-calendar
            ref="calendar"
            v-model="anchorDate"
            :events="events"
            :event-overlap-mode="mode"
            :event-overlap-threshold="30"
            color="blue darken-3"
            :event-color="getEventColor"
            type="month"
          ></v-calendar>
        </v-sheet>
      </v-col>
    </v-row>
  </div>
</template>

<script>
export default {
  name: "GroupDetails",
  data() {
    return {
      mode: "stack",
      events: [],
      anchorDate: new Date(),
      group: null,
      groupDialog: {
        show: false,
        editMode: false,
        saveLoading: false,
        addMoreLoading: false,
        editingGroupId: null,
        group: {},
      },
      colors: [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
      ],
    };
  },
  watch: {
    locations() {
      this.eventsList();
    },
  },
  mounted() {
    this.getGroup().then(() => {
      console.log("Group loaded");
    });
    // this.$refs.calendar.scrollToTime("08:00");
    this.eventsToDisplay();
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
        var manager = this.group.managerInfo.person;
        return (
          manager.firstName +
          " " +
          manager.lastName +
          " " +
          (manager.secondLastName ? manager.secondLastName : "")
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
    eventsToDisplay() {
      console.log("called");
      const groupId = this.$route.params.group;
      this.$http
        .get(`/api/v1/groups/groups/${groupId}`)
        .then((resp) => {
          for (let i = 0; i < resp.data.meetings.length; i++) {
            if (resp.data.meetings[i].active) {
              this.events.push({
                name: resp.data.meetings[i].description,
                start: resp.data.meetings[i].startTime.slice(0, 19),
                end: resp.data.meetings[i].stopTime.slice(0, 19),
                color: this.colors[
                  Math.floor(Math.random() * this.colors.length)
                ],
              });
            }
          }
          console.log(this.events);
        })
        .catch(() => {
          this.events = [];
        });
      return 0;
    },
    getEventColor(event) {
      return event.color;
    },
  },
};
</script>
