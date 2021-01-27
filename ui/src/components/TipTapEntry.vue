<template>
    <div>
  <editor-menu-bar :editor="dialogData" v-slot="{ commands, isActive }">
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
  <editor-content 
  :editor="dialogData"/>
  <button
  @click="sendBody"
  >Save</button>
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
//import { eventBus } from "../plugins/event-bus";
export default {
  name: "TipTapEntry",
  components: { EditorContent, EditorMenuBar },
  data() {
    return {
      json: "Update content to see json",
      html: "Update content to see HTML",
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
        content: "Ediator Test",
        onUpdate: ({ getJSON, getHTML }) => {
          this.json = getJSON();
          this.html = getHTML();
        },
      }),
    };
  },
  computed: {
    ...mapState(["currentAccount"]),
    ...mapState(["currentLocale"]),
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
      sayHello(){
          console.log("Hello");
      },
      sendBody(){
          console.log("HERE", this.json);
          this.$emit("sending", this.html);
      },
  }
};
</script>