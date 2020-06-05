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
      <blog-post v-if= "snackBarObj.content == '404'">{{ $t("events.error-result-not-found") }}</blog-post>
      <blog-post v-if= "snackBarObj.content == '403'">{{ $t("events.Error-result-forbidden") }}</blog-post>
      <blog-post v-if= "snackBarObj.content == '409'">{{ $t("events.Error-result-conflect") }}</blog-post>
<!--      <blog-post v-else>{{ "Client Error"}}</blog-post>-->
      <v-btn flat color="normal" @click="snackBarObj.show = false">
        {{ $t("actions.dismiss") }}
      </v-btn>
      <v-btn flat color="primary" @click="reportFrom.show = true">{{ $t("actions.Report-error") }}</v-btn>
    </v-snackbar>
    <v-card
      v-show = reportFrom.show
    >
      <v-card-title>
        Error Report
      </v-card-title>
      <v-card-text>
        <form>
          <v-col>
            <v-text-field
              label="Make a description of your error"
              outlined
            ></v-text-field>
          </v-col>
        </form>
      </v-card-text>
      <v-btn small rounded color="info">Submit</v-btn>
      <v-btn small rounded color="primary" @click="reportFrom.show = false">Cancel</v-btn>
    </v-card>
  </div>
</template>

<script>
export default {
  props: ["bus"],
  data() {
    return {
      isshow: false,
      snackBarObj: {
        color: "normal",
        content: "",
        timeout: 12000,
        show: false
      },
      reportFrom:{
        content: "",
        timeout: 100,
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
