<template>
  <v-container style="max-width: 600px;">
    <v-timeline dense clipped id="time-line-container">
      <v-timeline-item fill-dot class="white--text mb-12" color="orange" large>
        <template v-slot:icon>
          <span>{{
            currentAccount.firstName[0] + currentAccount.lastName[0]
          }}</span>
        </template>
      </v-timeline-item>
      <v-timeline-item
        v-for="event in timeline"
        :key="event.id"
        class="mb-4"
        color="green lighten-1"
        small
      >
        <v-row justify="space-between">
          <v-col cols="7" v-text="event.text"></v-col>
          <v-col class="text-right" cols="5" v-text="event.time"></v-col>
        </v-row>
      </v-timeline-item>
    </v-timeline>
  </v-container>
</template>

<script>
import { mapState } from "vuex";
export default {
  name: "GroupMembershipHistory",
  data() {
    return {
      events: [],
      input: null,
      nonce: 0,
      history: null,
      personalInfo: {},
      singleTime: [],
      timeMap: {},
      content: null,
    };
  },
  computed: {
    timeline() {
      return this.events.slice().reverse();
    },
    ...mapState(["currentAccount"]),
    id() {
      return parseInt(this.$route.params.group);
    },
  },
  methods: {
    comment() {
      const time = new Date().toTimeString();
      this.events.push({
        id: this.nonce++,
        text: this.input,
        time: time.replace(/:\d{2}\sGMT-\d{4}\s\((.*)\)/, (match, contents) => {
          return ` ${contents
            .split(" ")
            .map((v) => v.charAt(0))
            .join("")}`;
        }),
      });

      this.input = null;
    },
    fetchHistory() {
      return this.$http.get("api/v1/groups/member-histories").then((resp) => {
        this.history = resp.data.filter(
          (person_history) => person_history.groupId === this.id
        );
        for (let i = 0; i < this.history.length; i++) {
          this.singleTime.push(this.history[i]);
          this.singleTime.push(this.history[i]);
        }

        for (let i = 0; i < this.singleTime.length; i++) {
          if (i % 2 === 0) {
            if (!(this.singleTime[i].joined in this.timeMap)) {
              this.timeMap[this.singleTime[i].joined] = {
                join: [],
                left: [],
              };
            }
            if (this.singleTime[i].joined in this.timeMap) {
              this.timeMap[this.singleTime[i].joined].join.push(
                this.singleTime[i]
              );
            }
          } else {
            if (!(this.singleTime[i].left in this.timeMap)) {
              this.timeMap[this.singleTime[i].left] = {
                join: [],
                left: [],
              };
            }
            if (this.singleTime[i].left in this.timeMap) {
              this.timeMap[this.singleTime[i].left].left.push(
                this.singleTime[i]
              );
            }
          }
        }
        let order = Object.keys(this.timeMap).sort();
        for (let i = 0; i < order.length; i++) {
          let key = order[i];
          console.log(key);
          for (let j = 0; j < this.timeMap[key].join.length; j++) {
            this.events.push({
              id: this.nonce++,
              text:
                this.timeMap[key].join[j].person.firstName +
                " " +
                this.timeMap[key].join[j].person.lastName +
                " Joined",
              time: this.timeMap[key].join[j].joined,
            });
          }
          for (let j = 0; j < this.timeMap[key].left.length; j++) {
            this.events.push({
              id: this.nonce++,
              text:
                this.timeMap[key].left[j].person.firstName +
                " " +
                this.timeMap[key].left[j].person.lastName +
                " Left",
              time: this.timeMap[key].left[j].left,
            });
          }
        }
      });
    },
    parser(time) {
      let year = parseInt(time.slice(0, 4), 10);
      let month = parseInt(time.slice(5, 7), 10);
      let day = parseInt(time.slice(8), 10);
      return [year, month, day];
    },
  },
  mounted() {
    this.fetchHistory();
  },
};
</script>

<style scoped></style>
