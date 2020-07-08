<template>
  <!-- display a message or error to the end user, and optionally perform a customized action
    usage: <MessageSnackBar v-bind:bus="bus"></MessageSnackBar>
      where bus is a vue instance.
    To display the snackbar, do:
      bus.$emit('message', config: {
        content: '',
        noTranslate: false,
        action: {
          title: '',
          func: (vm) => {...}
        })
    can replace 'message' with 'error' or 'notification' for different style of messages.
    in config, 
      'content' is the content to be displayed, the component will try to localize the string based on current locale if possible.
      setting a truthy value to 'noTranslate' will disable translation
      setting 'action' to false will disable the action button (only show 'dismiss' in the snackbar)
      'action.title' is the text to be displayed on the button
      'action.func' is a function to perform the desired action when the button is clicked, the current Vue instance
        is passed to the function to access relevant context
    for reference of the event bus model, see https://code.luasoftware.com/tutorials/vuejs/parent-call-child-component-method/
    -->
  <div>
    <!-- TODO: add multiple messages support? 
      Currently new messages will override the old ones, and count down will not restart <2020-06-04, David Deng> -->
    <v-snackbar
      v-model="snackBarObj.show"
      v-bind:timeout="snackBarObj.timeout"
      v-bind:color="snackBarObj.color"
      multi-line
      top
    >
      {{ localized(snackBarObj.config.content) }}
      <v-btn flat color="normal" @click="snackBarObj.show = false">
        {{ $t("error-report.actions.dismiss") }}
      </v-btn>
      <v-btn
        v-if="snackBarObj.config.action"
        flat
        color="primary"
        @click="handleAction"
        >{{ localized(snackBarObj.config.action.title) }}</v-btn
      >
    </v-snackbar>
  </div>
</template>

<script>
export default {
  props: ["bus"],
  data() {
    return {
      snackBarObj: {
        color: "normal",
        config: {},
        timeout: 12000,
        show: false,
      },
      reportFrom: {
        show: false,
      },
    };
  },
  computed: {},
  mounted() {
    this.bus.$on("message", this.showMessage);
    this.bus.$on("error", this.showError);
    this.bus.$on("notification", this.showNotification);
  },
  methods: {
    localized(text) {
      return this.snackBarObj.config.noTranslate ? text : this.$t(text);
    },
    handleAction() {
      if (
        !this.snackBarObj.config.action ||
        !this.snackBarObj.config.action.func
      )
        throw new Error("action unavailable");
      this.snackBarObj.config.action.func(this);
    },
    /* show message handlers */
    showMessage(config, color = "green lighten-1") {
      this.snackBarObj.config = config;
      this.snackBarObj.color = color;
      this.snackBarObj.show = true;
    },
    showError(config) {
      this.showMessage(config, "red lighten-1");
    },
    showNotification(config) {
      this.showMessage(config, "blue lighten-1");
    },
  },
};
</script>
