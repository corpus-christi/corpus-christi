<template>
  <v-card>
    <v-card-text>
      <v-layout align-space-around justify-space-between column fill-height>
        <form method="POST" ref="imageForm" v-if="!imageSaved">
          <v-flex class="text-xs-center">
            <v-btn flat color="primary" small @click="openFileChooser">
              {{ $t("actions.choose-image") }}
            </v-btn>
          </v-flex>
          <v-flex
            v-if="!imageSelected && !imageNotFound"
            class="text-xs-center"
          >
            <span>{{ $t("images.messages.no-image") }}</span>
          </v-flex>
          <v-flex v-if="imageNotFound" class="text-xs-center">
            <span>{{ $t("images.messages.not-found") }}</span>
          </v-flex>
          <v-layout
            fill-height
            align-center
            justify-center
            row
            v-if="imageSelected"
          >
            <v-flex class="text-xs-right">
              <span>{{ filename }}</span>
            </v-flex>
            <v-flex>
              <v-btn icon small @click="removePreview">
                <v-icon>close</v-icon>
              </v-btn>
            </v-flex>
          </v-layout>
          <v-flex hidden>
            <input
              type="file"
              hidden
              ref="image_chooser"
              name="file"
              @change="previewImage"
            />
          </v-flex>
          <v-flex>
            <v-text-field
              :placeholder="$t('images.image-description')"
              name="description"
            />
          </v-flex>
        </form>
        <v-flex v-if="imageSaved">
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
      </v-layout>
    </v-card-text>
    <v-card-actions v-if="!imageSaved">
      <v-spacer />
      <v-btn flat @click="cancelDialog"> {{ $t("actions.cancel") }} </v-btn>
      <v-btn color="primary" @click="uploadSelectedImage">
        {{ $t("actions.save") }}
      </v-btn>
    </v-card-actions>
  </v-card>
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
        this.imageSaved = true;
      } else {
        this.imageId = -1;
        this.imageSelected = false;
        this.imageNotFound = false;
        this.imageSaved = false;
      }
    }
  },
  methods: {
    openFileChooser() {
      const imageInput = this.$refs.image_chooser;
      imageInput.click();
    },
    previewImage($event) {
      if ($event.target.files.length > 0) {
        this.imageSelected = true;
        this.imageNotFound = false;
        this.filename = $event.target.files[0].name;
      }
    },
    removePreview() {
      this.$refs.image_chooser.value = "";
      this.imageSelected = false;
      this.imageNotFound = false;
    },
    uploadSelectedImage() {
      if (this.$refs.image_chooser.files.length > 0) {
        const formData = new FormData(this.$refs.imageForm);
        this.$http
          .post("/api/v1/images/", formData)
          .then(resp => {
            console.log(resp);
            this.imageId = resp.data.id;
            this.imageSaved = true;
            this.$emit("selected", this.imageId);
          })
          .catch(err => {
            const response = err.response;
            if (response) {
              if (response.status == 303) {
                this.imageId = response.data.id;
                this.imageSaved = true;
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
      this.imageSaved = false;
      this.imageId = -1;
      this.$emit("deleted");
    },
    noImage(error) {
      console.error("IMAGE LOAD ERROR", error);
      this.imageSelected = false;
      this.imageNotFound = true;
      this.imageSaved = false;
    },
    cancelDialog() {
      this.$emit("cancel");
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
      imageNotFound: false,
      imageSaved: false,
      filename: ""
    };
  }
};
</script>
