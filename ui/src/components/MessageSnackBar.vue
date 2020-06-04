<template>
  <!-- display a message or error to the end user
    usage: <MessageSnackBar v-bind:bus="bus"></MessageSnackBar>
      where bus is a vue instance.
    do bus.$emit('message', 'message to be displayed')
    can replace 'message' with 'error' or 'notification' for different style of messages
    for reference of the event bus model, see https://code.luasoftware.com/tutorials/vuejs/parent-call-child-component-method/
    -->
  <div>
    <!-- TODO: add multiple messages support? 
      Currently new messages will override the old ones, and count down will not restart <2020-06-04, David Deng> -->
    <!-- START: to be removed -->
    <v-btn
      color="primary"
      :text="true"
      @click="$http.get('api/v1/groups/group-types/1')"
      >make an invalid request</v-btn
    >
    <!-- END: to be removed -->
    <v-snackbar
      v-model="snackBarObj.show"
      v-bind:timeout="snackBarObj.timeout"
      v-bind:color="snackBarObj.color"
      multi-line
      top
    >
      {{ snackBarObj.content }}
      <v-btn flat color="normal" @click="snackBarObj.show = false"
        >Dismiss</v-btn
      >
      <v-btn flat color="primary">Report Error(not implemented)</v-btn>
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
        content: "",
        timeout: 12000,
        show: false
      }
    };
  },
  mounted() {
    this.bus.$on("message", this.showMessage);
    this.bus.$on("error", this.showError);
    this.bus.$on("notification", this.showNotification);
  },
  methods: {
    showMessage(content, color = "green lighten-3") {
      this.snackBarObj.content = content;
      this.snackBarObj.color = color;
      this.snackBarObj.show = true;
    },
    showError(content) {
      this.showMessage(content, "red lighten-3");
    },
    showNotification(content) {
      this.showMessage(content, "blue lighten-3");
    }
  }
};
</script>
