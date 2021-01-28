<template>
  <div>
    <v-container style="max-width: 600px">
      <v-timeline clipped align-top id="time-line-container">
        <v-timeline-item
          fill-dot
          class="white--text mb-12"
          color="orange"
          large
        >
          <template v-slot:icon>
            <span
              v-text="currentAccount.firstName[0] + currentAccount.lastName[0]"
            >
            </span>
          </template>
        </v-timeline-item>
        <v-timeline-item
          v-for="event in timeline"
          :key="event.id"
          class="mb-4"
          :color="defineColor(event) ? 'green lighten-1' : 'red'"
          small
          :left="true"
        >
          <v-card>
            <template>
              <v-card-title class="orange lighten-2" v-model="admin">
                {{ $t("groups.membership-history.note") }}
                <v-spacer />
                <v-tooltip bottom>
                  <template v-slot:activator="{ on }" v-if="ifAdmin">
                    <v-btn
                      color="orange lighten-2"
                      small
                      v-on="on"
                      v-on:click="clearNote(event, event.id)"
                      ><v-icon>clear</v-icon></v-btn
                    >
                  </template>
                  <span>{{ $t("groups.membership-history.clear-note") }}</span>
                </v-tooltip>
                <v-tooltip bottom v-if="ifAdmin">
                  <template v-slot:activator="{ on }">
                    <v-btn
                      color="orange lighten-2"
                      small
                      v-on="on"
                      v-on:click="showDialog(event)"
                      ><v-icon>note_add</v-icon></v-btn
                    >
                  </template>
                  <span>{{ $t("groups.membership-history.change-note") }}</span>
                </v-tooltip>
              </v-card-title>
              <editor-content
                :editor="timeLineItems['timeLineItem' + event.id]"
              />
            </template>
          </v-card>
          <v-row justify="space-between" slot="opposite">
            <v-col
              v-if="event.text.slice(-1) === '-'"
              cols="7"
              v-text="event.text + $t('groups.membership-history.left')"
            ></v-col>
            <v-col
              v-else
              cols="7"
              v-text="event.text + $t('groups.membership-history.joined')"
            ></v-col>
            <v-col
              class="text-right"
              cols="5"
              v-text="event.time.slice(0, -6)"
            ></v-col>
          </v-row>
        </v-timeline-item>
      </v-timeline>

      <!-- Note dialog-->
      <v-dialog v-model="addNoteDialog" persistent max-width="400">
        <v-card>
          <template>
            <editor-menu-bar
              :editor="dialogData"
              v-slot="{ commands, isActive }"
            >
              <div class="menubar">
                <button
                  style="margin: 5px"
                  class="menubar__button"
                  :class="{ 'is-active': isActive.bold() }"
                  @click="commands.bold"
                >
                  <v-icon>format_bold</v-icon>
                </button>
                <button
                  style="margin: 5px"
                  class="menubar__button"
                  :class="{ 'is-active': isActive.italic() }"
                  @click="commands.italic"
                >
                  <v-icon>format_italic</v-icon>
                </button>
                <button
                  style="margin: 5px"
                  class="menubar__button"
                  :class="{ 'is-active': isActive.strike() }"
                  @click="commands.strike"
                >
                  <v-icon>format_strikethrough</v-icon>
                </button>
                <button
                  style="margin: 5px"
                  class="menubar__button"
                  :class="{ 'is-active': isActive.underline() }"
                  @click="commands.underline"
                >
                  <v-icon>format_underlined</v-icon>
                </button>
                <button
                  style="margin: 5px"
                  class="menubar__button"
                  :class="{ 'is-active': isActive.code() }"
                  @click="commands.code"
                >
                  <v-icon>code</v-icon>
                </button>
                <button
                  style="margin: 5px"
                  class="menubar__button"
                  :class="{ 'is-active': isActive.heading({ level: 1 }) }"
                  @click="commands.heading({ level: 1 })"
                >
                  H1
                </button>
                <button
                  style="margin: 5px"
                  class="menubar__button"
                  :class="{ 'is-active': isActive.heading({ level: 2 }) }"
                  @click="commands.heading({ level: 2 })"
                >
                  H2
                </button>
                <button
                  style="margin: 5px"
                  class="menubar__button"
                  :class="{ 'is-active': isActive.heading({ level: 3 }) }"
                  @click="commands.heading({ level: 3 })"
                >
                  H3
                </button>
                <button
                  style="margin: 5px"
                  class="menubar__button"
                  :class="{ 'is-active': isActive.ordered_list() }"
                  @click="commands.ordered_list"
                >
                  <v-icon>format_list_numbered</v-icon>
                </button>
                <button
                  style="margin: 5px"
                  class="menubar__button"
                  :class="{ 'is-active': isActive.bullet_list() }"
                  @click="commands.bullet_list"
                >
                  <v-icon>format_list_bulleted</v-icon>
                </button>
                <button
                  style="margin: 5px"
                  class="menubar__button"
                  :class="{ 'is-active': isActive.code_block() }"
                  @click="commands.code_block"
                >
                  <v-icon>integration_instructions</v-icon>
                </button>
                <button
                  style="margin: 5px"
                  class="menubar__button"
                  :class="{ 'is-active': isActive.blockquote() }"
                  @click="commands.blockquote"
                >
                  <v-icon>format_quote</v-icon>
                </button>
                <button
                  style="margin: 5px"
                  class="menubar__button"
                  @click="commands.undo"
                >
                  <v-icon>undo</v-icon>
                </button>
                <button
                  style="margin: 5px"
                  class="menubar__button"
                  @click="commands.redo"
                >
                  <v-icon>redo</v-icon>
                </button>
              </div>
            </editor-menu-bar>
            <editor-content :editor="dialogData" />
          </template>
          <v-card-text> </v-card-text>
          <v-card-actions>
            <v-tooltip bottom>
              <template v-slot:activator="{ on }">
                <v-btn
                  color="orange lighten-2"
                  small
                  v-on="on"
                  v-on:click="hideDialog"
                  ><v-icon>cancel</v-icon></v-btn
                >
              </template>
              <span>{{ $t("groups.membership-history.cancel") }}</span>
            </v-tooltip>
            <v-spacer />
            <v-tooltip bottom>
              <template v-slot:activator="{ on }">
                <v-btn
                  color="orange lighten-2"
                  small
                  v-on="on"
                  v-on:click="changeNote()"
                  >{{ $t("groups.membership-history.submit") }}</v-btn
                >
              </template>
            </v-tooltip>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-container>
  </div>
</template>

<script>
import { mapState } from "vuex";
import { Editor, EditorContent, EditorMenuBar } from "tiptap";
import {
  Blockquote,
  CodeBlock,
  HardBreak,
  Heading,
  OrderedList,
  BulletList,
  ListItem,
  TodoItem,
  TodoList,
  Bold,
  Code,
  Italic,
  Link,
  Strike,
  Underline,
  History,
} from "tiptap-extensions";
import { eventBus } from "@/plugins/event-bus";

export default {
  name: "GroupMembershipHistory",
  components: { EditorContent, EditorMenuBar },
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
      notes: "",
      right: false,
      left: false,
      historyId: null,
      newNote: null,
      addNoteDialog: false,
      addedNote: null,
      editingNoteId: null,
      admin: null,
      currentEvent: null,
      storedEditor: null,
      currentNote: null,
      timeLineItems: {},
      editor: new Editor({
        extensions: [
          new Blockquote(),
          new CodeBlock(),
          new HardBreak(),
          new Heading({ levels: [1, 2, 3] }),
          new BulletList(),
          new OrderedList(),
          new ListItem(),
          new TodoItem(),
          new TodoList(),
          new Bold(),
          new Code(),
          new Italic(),
          new Link(),
          new Strike(),
          new Underline(),
          new History(),
        ],
        content: "Editor Test",
        onUpdate: ({ getJSON, getHTML }) => {
          this.json = getJSON();
          this.html = getHTML();
        },
      }),
      json: "Update content to see json",
      html: "Update content to see HTML",
    };
  },
  computed: {
    ifAdmin() {
      if (this.currentAccount.roles.includes("role.group-admin")) {
        return true;
      } else return false;
    },
    timeline() {
      return this.events;
    },
    ...mapState(["currentAccount"]),
    ...mapState(["currentLocale"]),
    id() {
      return parseInt(this.$route.params.group);
    },
    locale(text) {
      return text.text;
    },
    dialogData() {
      let data = new Editor({
        extensions: [
          new Blockquote(),
          new CodeBlock(),
          new HardBreak(),
          new Heading({ levels: [1, 2, 3] }),
          new BulletList(),
          new OrderedList(),
          new ListItem(),
          new TodoItem(),
          new TodoList(),
          new Bold(),
          new Code(),
          new Italic(),
          new Link(),
          new Strike(),
          new Underline(),
          new History(),
        ],
        content: this.currentNote,
        onUpdate: ({ getJSON, getHTML }) => {
          this.json = getJSON();
          this.html = getHTML();
        },
      });
      return data;
    },
  },
  methods: {
    timeLineItem(event) {
      if (event.note === undefined) return "";
      else {
        return JSON.parse(event.note);
      }
    },
    hideDialog() {
      this.addNoteDialog = false;
    },
    showDialog(event) {
      this.editingNoteId = event.recordId;
      this.currentEvent = event;
      if (event.note === "") {
        this.currentNote = "";
      } else {
        this.currentNote = JSON.parse(event.note);
      }
      this.addNoteDialog = true;
    },
    clearNote(event) {
      let payload = { note: "" };
      return this.$http
        .patch(`api/v1/groups/member-histories/${event.recordId}`, payload)
        .then((resp) => {
          console.log(resp.status);
          window.location.reload();
        });
    },
    changeNote() {
      let myJSON = JSON.stringify(this.json);
      let payload = { note: myJSON };
      this.addNoteDialog = false;
      return this.$http
        .patch(`api/v1/groups/member-histories/${this.editingNoteId}`, payload)
        .then((resp) => {
          eventBus.$emit("message", {
            content: "groups.membership-history.message.post-success",
          });
          console.log(resp.status);
          window.location.reload();
        })
        .catch((err) => {
          console.log(err);
          eventBus.$emit("error", {
            content: "groups.membership-history.message.post-fail.too-long",
          });
        });
    },
    defineColor(event) {
      return event.text.slice(-1) !== "-";
    },
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
        if (this.notes.length === 0) {
          for (let record of this.history) {
            if (record.note != null) {
              this.notes = this.notes.concat(
                "( ",
                record.person.firstName,
                " ",
                record.person.lastName,
                ": ",
                record.note,
                ")  "
              );
            }
          }
        }
        for (let i = 0; i < this.history.length; i++) {
          this.singleTime.push(this.history[i]);
        }
        for (let i = 0; i < this.singleTime.length; i++) {
          if (this.singleTime[i].is_join === false) {
            if (!(this.singleTime[i].time in this.timeMap)) {
              this.timeMap[this.singleTime[i].time] = {
                join: [],
                left: [],
              };
            }
            if (this.singleTime[i].time in this.timeMap) {
              this.timeMap[this.singleTime[i].time].left.push(
                this.singleTime[i]
              );
            }
          } else {
            if (!(this.singleTime[i].time in this.timeMap)) {
              this.timeMap[this.singleTime[i].time] = {
                join: [],
                left: [],
              };
            }
            if (this.singleTime[i].time in this.timeMap) {
              this.timeMap[this.singleTime[i].time].join.push(
                this.singleTime[i]
              );
            }
          }
        }
        let order = Object.keys(this.timeMap).sort();
        for (let i = 0; i < order.length; i++) {
          let key = order[i];
          for (let j = 0; j < this.timeMap[key].join.length; j++) {
            this.events.push({
              id: this.nonce++,
              text:
                this.timeMap[key].join[j].person.firstName +
                " " +
                this.timeMap[key].join[j].person.lastName +
                " +",
              time: this.timeMap[key].join[j].time,
              note: this.timeMap[key].join[j].note,
              recordId: this.timeMap[key].join[j].id,
            });
          }
          for (let j = 0; j < this.timeMap[key].left.length; j++) {
            this.events.push({
              id: this.nonce++,
              text:
                this.timeMap[key].left[j].person.firstName +
                " " +
                this.timeMap[key].left[j].person.lastName +
                " -",
              time: this.timeMap[key].left[j].time,
              note: this.timeMap[key].left[j].note,
              recordId: this.timeMap[key].left[j].id,
            });
          }
        }
        for (let i = 0; i < order.length; i++) {
          this.timeLineItems["timeLineItem" + i] = new Editor({
            editable: false,
            extensions: [
              new Blockquote(),
              new CodeBlock(),
              new HardBreak(),
              new Heading({ levels: [1, 2, 3] }),
              new BulletList(),
              new OrderedList(),
              new ListItem(),
              new TodoItem(),
              new TodoList(),
              new Bold(),
              new Code(),
              new Italic(),
              new Link(),
              new Strike(),
              new Underline(),
              new History(),
            ],
            content: this.getNote(this.events[i].note),
            onUpdate: ({ getJSON, getHTML }) => {
              this.json = getJSON();
              this.html = getHTML();
            },
          });
        }
      });
    },
    getNote(eventNote) {
      if (eventNote === "") {
        return "";
      } else return JSON.parse(eventNote);
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
  beforeDestroy() {
    this.editor.destroy();
  },
};
</script>

<style scoped></style>
