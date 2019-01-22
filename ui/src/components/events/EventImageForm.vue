<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ $t("events.upload-image") }}</span>
    </v-card-title>
    <v-card-text>
      <form method="POST" ref="imageForm" @submit.prevent="postImage">
        <input type="file" name="file" ref="fileChooser" />
      </form>
      <v-text-field
        data-cy="image-description"
        name="description"
        v-model="description"
        :label="$t('events.image-description')"
      ></v-text-field>
    </v-card-text>
    <v-card-actions>
      <v-btn
        color="secondary"
        flat
        v-on:click="$emit('cancel')"
        :disabled="saving"
        data-cy="image-cancel"
        >{{ $t("actions.cancel") }}</v-btn
      >
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        v-on:click="save"
        :loading="saving"
        data-cy="image-save"
        >{{ $t("actions.save") }}</v-btn
      >
    </v-card-actions>
  </v-card>
</template>
<script>
export default {
  name: "EventImageForm",
  props: {
    eventId: {
      required: true
    }
  },

  data() {
    return {
      saving: false,
      description: ""
    };
  },

  methods: {
    save() {
      this.postImage().then(resp => {
        console.log(resp.data);
        let imageId = resp.data.id;
        var url = `/api/v1/events/${this.eventId}/images/${imageId}`;
        this.$http.post(url, { description: this.description }).then(resp => {
          console.log("image added to event!", resp);
          this.$emit("saved");
        });
      });
    },
    postImage() {
      var formData = new FormData(this.$refs.imageForm);
      var url = "/api/v1/images/";
      return this.$http
        .post(url, formData)
        .then(resp => {
          console.log("IMAGE ADDED", resp);
          return resp;
        })
        .catch(err => {
          console.error("IMAGE UPLOAD FAILURE", err.response);
        });
    }
  }
};
</script>
