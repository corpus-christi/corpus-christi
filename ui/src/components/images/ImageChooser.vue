<template>
  <v-layout align-space-around justify-space-between column fill-height>
    <form method="POST" ref="imageForm">
      <v-flex class="text-xs-center">
        <v-btn flat color="primary" small @click="openFileChooser">
          {{ $t("actions.choose-image") }}
        </v-btn>
      </v-flex>
      <v-flex v-if="!imageSelected" class="text-xs-center">
        <span>{{ $t("images.messages.no-image") }}</span>
      </v-flex>
      <v-flex v-if="imageNotFound" class="text-xs-center">
        <span>{{ $t("images.messages.not-found") }}</span>
      </v-flex>
      <v-flex hidden>
        <input
          type="file"
          hidden
          ref="image_chooser"
          @change="uploadSelectedImage"
          name="file"
        />
      </v-flex>
      <v-flex v-if="imageId > -1 && !imageNotFound">
        <v-img
          min-width="100%"
          ref="preview"
          :src="fetchImage"
          @error="noImage"
        >
          <v-layout justify-end fill-height align-start>
            <v-btn
              flat
              icon
              class="d-flex grey darken-4 display-3 white--text"
              @click="deleteSelectedImage"
            >
              <v-icon>close</v-icon>
            </v-btn>
          </v-layout>
        </v-img>
      </v-flex>
    </form>
  </v-layout>
</template>

<script>
export default {
  name: "ImageChooser",
  computed: {
    fetchImage() {
      return `/api/v1/images/${this.imageId}?${Math.random()}`;
    }
  },
  watch: {
    oldImageId(id) {
      if (id > -1) {
        this.imageId = id;
        this.imageSelected = true;
        this.imageNotFound = false;
      } else {
        this.imageId = -1;
        this.imageSelected = false;
        this.imageNotFound = false;
      }
    }
  },
  methods: {
    openFileChooser() {
      const imageInput = this.$refs.image_chooser;
      imageInput.click();
    },
    uploadSelectedImage($event) {
      if ($event.target.files.length > 0) {
        const formData = new FormData(this.$refs.imageForm);
        this.$http
          .post("/api/v1/images/", formData)
          .then(resp => {
            console.log(resp);
            this.imageId = resp.data.id;
            this.imageSelected = true;
            this.imageNotFound = false;
            this.$emit("selected", this.imageId);
          })
          .catch(err => {
            const response = err.response;
            if (response) {
              if (response.status == 303) {
                this.imageId = response.data.id;
                this.imageSelected = true;
                this.imageNotFound = false;
                this.$emit("selected", this.imageId);
              } else {
                console.error("IMAGE ERROR", response);
              }
            }
          });
      }
      this.$forceUpdate();
    },
    deleteSelectedImage() {
      this.imageSelected = false;
      this.imageNotFound = false;
      this.imageId = -1;
      this.$emit("deleted");
    },
    noImage(error) {
      console.error("IMAGE LOAD ERROR", error);
      this.imageSelected = true;
      this.imageNotFound = true;
    }
  },
  props: {
    oldImageId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      imageId: -1,
      imageSelected: false,
      imageNotFound: false
    };
  }
};
</script>
