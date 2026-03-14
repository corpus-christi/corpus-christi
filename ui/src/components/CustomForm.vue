<template>
  <v-card>
    <!-- TODO: It would be ideal in the future to make these date pickers a component in themselves -->
    <v-card-title>
      <span class="headline">{{ title }}</span>
    </v-card-title>
    <v-card-text>
      <form>
        <v-row align="space-around" justify="center">
          <v-col cols="12">
            <v-text-field
              v-if="titleLabel"
              v-model="object.title"
              v-bind:label="titleLabel"
              name="title"
              :error-messages="titleErrors"
              data-cy="title"
            />
          </v-col>
          <v-col cols="12">
            <v-textarea
              rows="3"
              v-if="descriptionLabel"
              v-model="object.description"
              v-bind:label="descriptionLabel"
              name="description"
              data-cy="description"
            />
          </v-col>
          <v-col cols="12">
            <v-btn
              v-if="addImageField"
              class="text-xs-center"
              color="primary"
              variant="text"
              small
              @click="showImageChooser = true"
              :disabled="showImageChooser"
            >
              {{ t("images.actions.add-image") }}
            </v-btn>
          </v-col>
          <v-col cols="12">
            <v-expand-transition>
              <image-chooser
                v-if="showImageChooser"
                :imageId="getImageId"
                v-on:saved="chooseImage"
                v-on:deleted="deleteImage"
                v-on:cancel="cancelImageChooser"
                v-on:missing="missingImage"
              />
            </v-expand-transition>
          </v-col>
        </v-row>
        <v-row align="center" justify="space-around" v-if="locationLabel">
          <v-col>
            <entity-search
              location
              v-model="object.location"
              v-bind:label="locationLabel"
              name="location"
              v-bind:error-messages="locationErrors"
              :disabled="showAddressCreator"
              :key="currentAddress"
            />
          </v-col>
          <v-col cols="auto">
            <v-btn
              variant="text"
              color="primary"
              small
              @click="showAddressCreator = true"
              >{{ t("actions.add-address") }}</v-btn
            >
          </v-col>
        </v-row>

        <v-expand-transition>
          <address-form
            v-if="showAddressCreator"
            @cancel="showAddressCreator = false"
            @saved="updateEntitySearch"
          />
        </v-expand-transition>

        <v-row v-if="startDateTimeField">
          <v-col cols="12" md="6">
            <!-- Start Date -->
            <v-menu
              :close-on-content-click="false"
              v-model="showStartDatePicker"
              :nudge-right="40"
              transition="scale-transition"
              offset-y
              min-width="290px"
              data-cy="start-date-menu"
            >
              <template #activator="{ props }">
                <v-text-field
                  v-bind="props"
                  v-model="startDate"
                  v-bind:label="t('events.start-date')"
                  prepend-icon="event"
                  readonly
                  name="startDate"
                  :error-messages="startDateErrors"
                />
              </template>
              <v-date-picker
                v-bind:locale="authStore.currentLanguageCode"
                v-model="startDate"
                @update:modelValue="showStartDatePicker = false"
                :min="today"
                data-cy="start-date-picker"
              />
            </v-menu>
          </v-col>
          <v-col cols="12" md="6" class="ml-5">
            <!-- Start Time -->
            <v-dialog
              ref="dialog1"
              v-model="startTimeModal"
              v-model:return-value="startTime"
              width="290px"
              persistent
              data-cy="start-time-dialog"
            >
              <template #activator="{ props }">
                <v-text-field
                  v-bind="props"
                  v-model="startTime"
                  name="startTime"
                  :error-messages="startTimeErrors"
                  v-bind:label="t('events.start-time')"
                  prepend-icon="schedule"
                  readonly
                ></v-text-field>
              </template>
              <v-time-picker
                v-if="startTimeModal"
                :format="timeFormat"
                v-model="startTime"
                :max="startDate == endDate ? endTime : undefined"
                data-cy="start-time-picker"
              >
                <v-spacer></v-spacer>
                <v-btn
                  variant="text"
                  color="primary"
                  @click="startTimeModal = false"
                  data-cy="start-time-cancel"
                  >{{ t("actions.cancel") }}</v-btn
                >
                <v-btn
                  variant="text"
                  color="primary"
                  @click="(dialog1 as any).save(startTime)"
                  data-cy="start-time-ok"
                  >{{ t("actions.confirm") }}</v-btn
                >
              </v-time-picker>
            </v-dialog>
          </v-col>
        </v-row>
        <v-row v-if="endDateTimeField">
          <v-col cols="12" md="6">
            <!-- End Date -->
            <v-menu
              :close-on-content-click="false"
              v-model="showEndDatePicker"
              :nudge-right="40"
              transition="scale-transition"
              offset-y
              min-width="290px"
              data-cy="end-date-menu"
              :disabled="!startDateTimeSelected"
            >
              <template #activator="{ props }">
                <v-text-field
                  v-bind="props"
                  v-model="endDate"
                  v-bind:label="t('events.end-date')"
                  prepend-icon="event"
                  name="endDate"
                  :error-messages="endDateErrors"
                  readonly
                  :disabled="!startDateTimeSelected"
                />
              </template>

              <v-date-picker
                v-bind:locale="authStore.currentLanguageCode"
                v-model="endDate"
                @update:modelValue="showEndDatePicker = false"
                data-cy="end-date-picker"
                :min="startDate || today"
              />
            </v-menu>
          </v-col>
          <v-col cols="12" md="6" class="ml-5">
            <!-- End Time -->
            <v-dialog
              ref="dialog2"
              v-model="endTimeModal"
              :disabled="!startDateTimeSelected"
              v-model:return-value="endTime"
              width="290px"
              persistent
              data-cy="end-time-dialog"
            >
              <template #activator="{ props }">
                <v-text-field
                  v-bind="props"
                  v-model="endTime"
                  name="endTime"
                  :error-messages="endTimeErrors"
                  v-bind:label="t('events.end-time')"
                  prepend-icon="update"
                  :disabled="!startDateTimeSelected"
                  readonly
                />
              </template>
              <v-time-picker
                v-if="endTimeModal"
                :format="timeFormat"
                v-model="endTime"
                :min="startDate == endDate ? startTime : undefined"
                data-cy="end-time-picker"
              >
                <v-spacer />
                <v-btn
                  variant="text"
                  color="primary"
                  @click="endTimeModal = false"
                  data-cy="end-time-cancel"
                  >{{ t("actions.cancel") }}</v-btn
                >
                <v-btn
                  variant="text"
                  color="primary"
                  @click="(dialog2 as any).save(endTime)"
                  data-cy="end-time-ok"
                  >{{ t("actions.confirm") }}</v-btn
                >
              </v-time-picker>
            </v-dialog>
          </v-col>
        </v-row>
        <input
          name="today"
          type="text"
          v-bind:value="today"
          hidden
          readonly
        />
      </form>
    </v-card-text>
    <v-divider />
    <v-card-actions>
      <v-btn
        color="secondary"
        variant="text"
        v-on:click="cancel"
        :disabled="formDisabled"
        data-cy="form-cancel"
        >{{ t("actions.cancel") }}</v-btn
      >
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        variant="outlined"
        v-on:click="addAnother"
        v-if="!editMode"
        :loading="addMoreLoading"
        :disabled="formDisabled"
        data-cy="form-addanother"
        >{{ t("actions.add-another") }}</v-btn
      >
      <v-btn
        color="primary"
        v-on:click="save"
        :loading="saveLoading"
        :disabled="formDisabled"
        data-cy="form-save"
        >{{ t("actions.save") }}</v-btn
      >
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
//When using this component, pass the prop (label or boolean) for all fields you wish to display.
import { ref, reactive, computed, watch } from "vue";
import { isEmpty } from "lodash";
import { useI18n } from "vue-i18n";
import { useAuthStore } from "@/stores/auth";
import EntitySearch from "./EntitySearch.vue";
import AddressForm from "./AddressForm.vue";
import ImageChooser from "./images/ImageChooser.vue";

const { t } = useI18n();
const authStore = useAuthStore();

const props = defineProps<{
  addMoreLoading?: boolean;
  addImageField?: boolean;
  descriptionLabel?: string;
  editMode: boolean;
  endDateTimeField?: boolean;
  locationLabel?: string;
  initialData?: Record<string, any> | null;
  saveLoading?: boolean;
  startDateTimeField?: boolean;
  titleLabel?: string;
  editText?: string;
  createText?: string;
}>();

const emit = defineEmits(["cancel", "save", "addAnother"]);

const dialog1 = ref<any>(null);
const dialog2 = ref<any>(null);

const object = ref<Record<string, any>>({});
const startTime = ref("");
const startDate = ref("");
const endTime = ref("");
const endDate = ref("");
const addMore = ref(false);
const showStartDatePicker = ref(false);
const showEndDatePicker = ref(false);
const startTimeModal = ref(false);
const endTimeModal = ref(false);
const showAddressCreator = ref(false);
const showImageChooser = ref(false);
const imageSaved = ref(false);
const currentAddress = ref(0);

// Validation errors
const titleErrors = ref<string[]>([]);
const locationErrors = ref<string[]>([]);
const startDateErrors = ref<string[]>([]);
const startTimeErrors = ref<string[]>([]);
const endDateErrors = ref<string[]>([]);
const endTimeErrors = ref<string[]>([]);

const eventKeys = computed(() => Object.keys(object.value));

const title = computed(() => {
  return props.editMode ? t(props.editText || "") : t(props.createText || "");
});

const timeFormat = computed(() => {
  if (authStore.currentLanguageCode && authStore.currentLanguageCode.substring(0, 2) === "en") {
    return "ampm";
  } else return "24hr";
});

const formDisabled = computed(() => {
  return (
    props.saveLoading ||
    props.addMoreLoading ||
    showAddressCreator.value ||
    (showImageChooser.value && !imageSaved.value)
  );
});

const today = computed(() => {
  return getDateFromTimestamp(Date.now());
});

const startDateTimeSelected = computed(() => {
  return startDate.value && startTime.value;
});

const getImageId = computed(() => {
  if (object.value.images) {
    return object.value.images.length > 0 ? object.value.images[0].image_id : -1;
  } else {
    return -1;
  }
});

watch(
  () => props.initialData,
  (eventProp) => {
    if (!eventProp || isEmpty(eventProp)) {
      clear();
    } else {
      object.value = { ...eventProp };
      if (object.value.start != null) {
        object.value.start = new Date(object.value.start);
        startDate.value = getDateFromTimestamp(object.value.start);
        startTime.value = getTimeFromTimestamp(object.value.start);
      }
      if (object.value.end != null) {
        object.value.end = new Date(object.value.end);
        endDate.value = getDateFromTimestamp(object.value.end);
        endTime.value = getTimeFromTimestamp(object.value.end);
      }
      if (object.value.images && object.value.images.length > 0) {
        showImageChooser.value = true;
        imageSaved.value = true;
      } else {
        showImageChooser.value = false;
        imageSaved.value = false;
      }
    }
  }
);

watch(startDate, (date) => {
  clearEndTimeIfInvalid();
  if (!endDate.value || new Date(endDate.value) < new Date(date)) {
    if (!object.value.dayDuration) {
      endDate.value = date;
    } else {
      endDate.value = addDaystoDate(date, object.value.dayDuration);
    }
  }
});

watch(endDate, () => {
  clearEndTimeIfInvalid();
});

function cancel() {
  emit("cancel");
}

function clear() {
  for (let key of eventKeys.value) {
    object.value[key] = "";
  }
  delete object.value.location;
  startTime.value = "";
  startDate.value = "";
  endTime.value = "";
  endDate.value = "";
  showStartDatePicker.value = false;
  showEndDatePicker.value = false;
  startTimeModal.value = false;
  endTimeModal.value = false;
  showImageChooser.value = false;
  showAddressCreator.value = false;
  titleErrors.value = [];
  locationErrors.value = [];
  startDateErrors.value = [];
  startTimeErrors.value = [];
  endDateErrors.value = [];
  endTimeErrors.value = [];
}

function validateForm(): boolean {
  let valid = true;
  titleErrors.value = [];
  startDateErrors.value = [];
  startTimeErrors.value = [];
  endDateErrors.value = [];
  endTimeErrors.value = [];

  if (props.titleLabel && !object.value.title) {
    titleErrors.value = [t("validations.required")];
    valid = false;
  }
  if (props.startDateTimeField && !startDate.value) {
    startDateErrors.value = [t("validations.required")];
    valid = false;
  }
  if (props.startDateTimeField && !startTime.value) {
    startTimeErrors.value = [t("validations.required")];
    valid = false;
  }
  if (props.endDateTimeField && !endDate.value) {
    endDateErrors.value = [t("validations.required")];
    valid = false;
  }
  if (props.endDateTimeField && !endTime.value) {
    endTimeErrors.value = [t("validations.required")];
    valid = false;
  }
  return valid;
}

function save() {
  if (!validateForm()) return;
  object.value.start = getTimestamp(startDate.value, startTime.value);
  object.value.end = getTimestamp(endDate.value, endTime.value);
  object.value.active = true;
  if (addMore.value) emit("addAnother", object.value);
  else emit("save", object.value);
  addMore.value = false;
}

function addAnother() {
  addMore.value = true;
  save();
}

function getTimestamp(date: string, time: string) {
  let datems = new Date(date).getTime();
  let timemin = getMinutesFromTime(time);
  let timems = timemin * 60000;
  let tzoffset = new Date().getTimezoneOffset() * 60000;
  return new Date(datems + timems + tzoffset);
}

function getMinutesFromTime(time: string) {
  let timearr = time.split(":");
  return Number(timearr[0]) * 60 + Number(timearr[1]);
}

function getDateFromTimestamp(ts: any) {
  let date = new Date(ts);
  if (date.getTime() < 86400000) {
    return "";
  }
  const langCode = authStore.currentLanguageCode || "en";
  let yr = date.toLocaleDateString(langCode, { year: "numeric" });
  let mo = date.toLocaleDateString(langCode, { month: "2-digit" });
  let da = date.toLocaleDateString(langCode, { day: "2-digit" });
  return `${yr}-${mo}-${da}`;
}

function getTimeFromTimestamp(ts: any) {
  let date = new Date(ts);
  let hr = String(date.getHours()).padStart(2, "0");
  let min = String(date.getMinutes()).padStart(2, "0");
  return `${hr}:${min}`;
}

function addDaystoDate(date: string, dayDuration: number) {
  let date1 = getTimestamp(date, "00:00");
  date1.setDate(date1.getDate() + dayDuration);
  return getDateFromTimestamp(date1);
}

function clearEndTimeIfInvalid() {
  if (startDate.value === endDate.value) {
    if (!endTime.value || !startTime.value) return;
    let endMins = getMinutesFromTime(endTime.value);
    let startMins = getMinutesFromTime(startTime.value);
    if (endMins < startMins) {
      endTime.value = "";
    }
  }
}

function updateEntitySearch(address: any) {
  console.log(address);
  object.value.location = address;
  currentAddress.value = address.address_id;
}

function chooseImage(id: any) {
  object.value.newImageId = id;
  imageSaved.value = true;
}

function deleteImage() {
  showImageChooser.value = false;
  delete object.value.newImageId;
  object.value.images = [];
  imageSaved.value = false;
}

function cancelImageChooser() {
  showImageChooser.value = false;
}

function missingImage() {
  imageSaved.value = false;
}
</script>
