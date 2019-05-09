<template>
  <v-card>
    <v-card-text>
      <v-layout align-space-around justify-space-between column fill-height>
        <form method="POST" ref="imageForm">
          <v-flex class="text-xs-center">
            <v-btn
              flat
              color="primary"
              small
              @click="openFileChooser"
              v-if="!saved"
            >
              {{ $t("actions.choose-image") }}
            </v-btn>
          </v-flex>
          <v-flex class="text-xs-center" v-if="!preview && !saved && !missing">
            <span>{{ $t("images.messages.no-image") }}</span>
          </v-flex>
          <v-flex v-if="missing" class="text-xs-center">
            <span>{{ $t("images.messages.not-found") }}</span>
          </v-flex>
          <v-layout fill-height align-center justify-center row>
            <v-flex class="text-xs-right" v-if="preview">
              <span>{{ filename }}</span>
            </v-flex>
            <v-flex v-if="preview">
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
          <v-flex v-if="!saved">
            <v-text-field
              :placeholder="$t('images.image-description')"
              name="description"
            />
          </v-flex>
        </form>
        <v-flex v-if="saved">
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
    <v-card-actions v-if="!saved">
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
      return `/api/v1/images/${this.id}?${Math.random()}`;
    }
  },
  watch: {
    imageId(id) {
      this.clear();
      if (id > -1) {
        this.id = id;
        this.saved = true;
      }
    }
  },
  methods: {
    clear() {
      this.id = -1;
      this.saved = false;
      this.preview = false;
      this.missing = false;
      this.filename = "";
    },

    openFileChooser() {
      const imageInput = this.$refs.image_chooser;
      imageInput.click();
    },

    previewImage($event) {
      if ($event.target.files.length > 0) {
        this.preview = true;
        this.filename = $event.target.files[0].name;
      }
    },

    removePreview() {
      this.filename = "";
      this.preview = false;
    },

    uploadSelectedImage() {
      if (this.$refs.image_chooser.files.length > 0) {
        const formData = new FormData(this.$refs.imageForm);
        this.$http
          .post("/api/v1/images/", formData)
          .then(resp => {
            console.log(resp);
            this.saveSelectedImage(resp.data.id);
          })
          .catch(err => {
            const response = err.response;
            if (response) {
              if (response.status == 303) {
                this.saveSelectedImage(response.data.id);
              } else {
                this.saved = false;
                console.error("IMAGE ERROR", response);
              }
            } else {
              this.saved = false;
            }
          });
      }
      this.$forceUpdate();
    },

    saveSelectedImage(id) {
      this.id = id;
      this.saved = true;
      this.preview = false;
      this.missing = false;
      this.$emit("saved", id);
    },

    deleteSelectedImage() {
      this.clear();
      this.$emit("deleted");
    },
    noImage(error) {
      console.error("IMAGE MISSING", error);
      this.missing = true;
      this.preview = false;
      this.saved = false;
      this.$emit("missing");
    },
    cancelDialog() {
      this.$emit("cancel");
    }
  },
  props: {
    imageId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      id: -1,
      filename: "",
      saved: false,
      preview: false,
      missing: false
    };
  },
  mounted() {
    this.clear();
    if (this.$props.imageId > -1) {
      this.id = this.$props.imageId;
      this.saved = true;
    }
  }
};
</script>
