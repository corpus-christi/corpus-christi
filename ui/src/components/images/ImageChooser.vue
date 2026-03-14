<template>
  <v-card>
    <v-card-text>
      <v-row align="space-around" justify="space-between" no-gutters>
        <form method="POST" ref="imageForm">
          <v-col class="text-center">
            <v-btn
              variant="text"
              color="primary"
              size="small"
              @click="openFileChooser"
              v-if="!saved"
            >
              {{ t("actions.choose-image") }}
            </v-btn>
          </v-col>
          <v-col class="text-center" v-if="!preview && !saved && !missing">
            <span>{{ t("images.messages.no-image") }}</span>
          </v-col>
          <v-col v-if="missing" class="text-center">
            <span>{{ t("images.messages.not-found") }}</span>
          </v-col>
          <v-row align="center" justify="center">
            <v-col class="text-right" v-if="preview">
              <span>{{ filename }}</span>
            </v-col>
            <v-col v-if="preview">
              <v-btn icon size="small" @click="removePreview">
                <v-icon>close</v-icon>
              </v-btn>
            </v-col>
          </v-row>
          <v-col style="display:none">
            <input
              type="file"
              hidden
              ref="image_chooser"
              name="file"
              @change="previewImage"
            />
          </v-col>
          <v-col v-if="!saved">
            <v-text-field
              :placeholder="t('images.image-description')"
              name="description"
            />
          </v-col>
        </form>
        <v-col v-if="saved">
          <v-img
            min-width="100%"
            ref="previewRef"
            :src="fetchImage"
            @error="noImage"
          >
            <v-row justify="end" align="start">
              <v-btn
                variant="text"
                icon
                class="d-flex grey darken-4 display-3 white--text"
                @click="deleteSelectedImage"
              >
                <v-icon>close</v-icon>
              </v-btn>
            </v-row>
          </v-img>
        </v-col>
      </v-row>
    </v-card-text>
    <v-card-actions v-if="!saved">
      <v-spacer />
      <v-btn variant="text" @click="cancelDialog"> {{ t("actions.cancel") }} </v-btn>
      <v-btn color="primary" @click="uploadSelectedImage">
        {{ t("actions.save") }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { inject } from "vue";
import type { AxiosInstance } from "axios";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;

const props = defineProps<{
  imageId: number;
}>();

const emit = defineEmits(["saved", "deleted", "missing", "cancel"]);

const id = ref(-1);
const filename = ref("");
const saved = ref(false);
const preview = ref(false);
const missing = ref(false);
const imageForm = ref<HTMLFormElement | null>(null);
const image_chooser = ref<HTMLInputElement | null>(null);
const previewRef = ref<any>(null);

const fetchImage = computed(() => `/api/v1/images/${id.value}?${Math.random()}`);

watch(() => props.imageId, (newId) => {
  clear();
  if (newId > -1) {
    id.value = newId;
    saved.value = true;
  }
});

function clear() {
  id.value = -1;
  saved.value = false;
  preview.value = false;
  missing.value = false;
  filename.value = "";
}

function openFileChooser() {
  image_chooser.value?.click();
}

function previewImage($event: Event) {
  const target = $event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    preview.value = true;
    filename.value = target.files[0].name;
  }
}

function removePreview() {
  filename.value = "";
  preview.value = false;
}

function uploadSelectedImage() {
  if (image_chooser.value && image_chooser.value.files && image_chooser.value.files.length > 0) {
    const formData = new FormData(imageForm.value!);
    http
      .post("/api/v1/images/", formData)
      .then(resp => {
        saveSelectedImage(resp.data.id);
      })
      .catch(err => {
        const response = err.response;
        if (response) {
          if (response.status == 303) {
            saveSelectedImage(response.data.id);
          } else {
            saved.value = false;
            console.error("IMAGE ERROR", response);
          }
        } else {
          saved.value = false;
        }
      });
  }
}

function saveSelectedImage(imageId: number) {
  id.value = imageId;
  saved.value = true;
  preview.value = false;
  missing.value = false;
  emit("saved", imageId);
}

function deleteSelectedImage() {
  clear();
  emit("deleted");
}

function noImage(error: any) {
  console.error("IMAGE MISSING", error);
  missing.value = true;
  preview.value = false;
  saved.value = false;
  emit("missing");
}

function cancelDialog() {
  emit("cancel");
}

onMounted(() => {
  clear();
  if (props.imageId > -1) {
    id.value = props.imageId;
    saved.value = true;
  }
});
</script>
