<template>
  <v-container style="max-width: 600px;">
    <v-timeline dense clipped id="time-line-container">
      <v-timeline-item fill-dot class="white--text mb-12" color="orange" large>
        <template v-slot:icon>
          <span>{{
            currentAccount.firstName[0] + currentAccount.lastName[0]
          }}</span>
        </template>
        <v-card>
          <v-text-field
            v-model="input"
            hide-details
            flat
            label="Leave a comment..."
            solo
            @keydown.enter="comment"
          >
            <template v-slot:append>
              <v-btn class="mx-0" depressed @click="comment">
                Post
              </v-btn>
            </template>
          </v-text-field>
        </v-card>
      </v-timeline-item>

      <v-slide-x-transition group>
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
      </v-slide-x-transition>
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
            let year = this.parser(this.singleTime[i].joined)[0];
            let month = this.parser(this.singleTime[i].joined)[1];
            let day = this.parser(this.singleTime[i].joined)[2];
            let dateId =
              year * 365 +
              month * 30 +
              day * day +
              this.singleTime[i].personId * 0.1;
            this.timeMap[dateId] = this.singleTime[i];
          } else {
            let year = this.parser(this.singleTime[i].left)[0];
            let month = this.parser(this.singleTime[i].left)[1];
            let day = this.parser(this.singleTime[i].left)[2];
            let dateId =
              year * 366 +
              month * 30 +
              day * day +
              this.singleTime[i].personId * 0.2;
            this.timeMap[dateId] = this.singleTime[i];
          }
        }
        let tem = [];
        let arr = Object.keys(this.timeMap);
        for (let i = 0; i < arr.length; i++) {
          tem.push(Number(arr[i]));
        }

        for (let i = 0; i < tem.length; i++) {
          for (let j = 0; j < this.history.length; j++) {
            if (
              tem[i] ===
              this.calJoined(this.history[j].joined, this.history[j].personId)
            ) {
              this.events.push({
                id: this.nonce++,
                text:
                  this.history[j].person.firstName +
                  " " +
                  this.history[j].person.lastName +
                  " Joined",
                time: this.history[j].joined,
              });
            } else if (
              tem[i] ===
              this.calLeft(this.history[j].left, this.history[j].personId)
            ) {
              this.events.push({
                id: this.nonce++,
                text:
                  this.history[j].person.firstName +
                  " " +
                  this.history[j].person.lastName +
                  " Left",
                time: this.history[j].left,
              });
            }
          }
        }
      });
    },
    calJoined(time, personId) {
      let year = this.parser(time)[0];
      let month = this.parser(time)[1];
      let day = this.parser(time)[2];
      let dateId = year * 365 + month * 30 + day * day + personId * 0.1;
      return dateId;
    },
    calLeft(time, personId) {
      let year = this.parser(time)[0];
      let month = this.parser(time)[1];
      let day = this.parser(time)[2];
      let dateId = year * 366 + month * 30 + day * day + personId * 0.2;
      return dateId;
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
