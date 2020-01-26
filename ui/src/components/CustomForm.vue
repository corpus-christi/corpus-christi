<template>
  <v-card>
    <!-- TODO: It would be ideal in the future to make these date pickers a component in themselves -->
    <v-card-title>
      <span class="headline">{{ title }}</span>
    </v-card-title>
    <v-card-text>
      <form>
        <v-layout align-space-around justify-center column fill-height>
          <v-text-field
            v-if="titleLabel"
            v-model="object.title"
            v-bind:label="titleLabel"
            name="title"
            v-validate="'required'"
            v-bind:error-messages="errors.first('title')"
            data-cy="title"
          ></v-text-field>
          <v-textarea
            rows="3"
            v-if="descriptionLabel"
            v-model="object.description"
            v-bind:label="descriptionLabel"
            name="description"
            data-cy="description"
          ></v-textarea>
          <v-btn
            v-if="addImageField"
            class="text-xs-center"
            color="primary"
            flat
            small
            @click="showImageChooser = true"
            :disabled="showImageChooser"
          >
            {{ $t("images.actions.add-image") }}
          </v-btn>
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
        </v-layout>
        <v-layout align-center justify-space-around v-if="locationLabel">
          <v-flex>
            <entity-search
              location
              v-model="object.location"
              v-bind:label="locationLabel"
              name="location"
              v-bind:error-messages="errors.first('location')"
              :disabled="showAddressCreator"
              :key="currentAddress"
            />
          </v-flex>
          <v-flex shrink>
            <v-btn
              flat
              color="primary"
              small
              @click="showAddressCreator = true"
              >{{ $t("actions.add-address") }}</v-btn
            >
          </v-flex>
        </v-layout>

        <v-expand-transition>
          <address-form
            v-if="showAddressCreator"
            @cancel="showAddressCreator = false"
            @saved="updateEntitySearch"
          ></address-form>
        </v-expand-transition>

        <v-layout v-if="startDateTimeField">
          <v-flex xs12 md6>
            <!-- Start Date -->
            <v-menu
              :close-on-content-click="false"
              v-model="showStartDatePicker"
              :nudge-right="40"
              lazy
              transition="scale-transition"
              offset-y
              full-width
              min-width="290px"
              data-cy="start-date-menu"
            >
              <v-text-field
                slot="activator"
                v-model="startDate"
                v-bind:label="$t('events.start-date')"
                prepend-icon="event"
                readonly
                name="startDate"
                ref="startDate"
                v-validate="'required'"
                v-bind:error-messages="errors.first('startDate')"
              ></v-text-field>
              <v-date-picker
                v-bind:locale="currentLanguageCode"
                v-model="startDate"
                @input="showStartDatePicker = false"
                :min="today"
                data-cy="start-date-picker"
              ></v-date-picker>
            </v-menu>
          </v-flex>
          <v-flex xs12 md6 ml-5>
            <!-- Start Time -->
            <v-dialog
              ref="dialog1"
              v-model="startTimeModal"
              :return-value.sync="startTime"
              lazy
              full-width
              width="290px"
              persistent
              data-cy="start-time-dialog"
            >
              <v-text-field
                slot="activator"
                v-model="startTime"
                name="startTime"
                v-validate="'required'"
                v-bind:error-messages="errors.first('startTime')"
                v-bind:label="$t('events.start-time')"
                prepend-icon="schedule"
                readonly
              ></v-text-field>
              <v-time-picker
                v-if="startTimeModal"
                :format="timeFormat"
                v-model="startTime"
                :max="startDate == endDate ? endTime : null"
                data-cy="start-time-picker"
              >
                <v-spacer></v-spacer>
                <v-btn
                  flat
                  color="primary"
                  @click="startTimeModal = false"
                  data-cy="start-time-cancel"
                  >{{ $t("actions.cancel") }}</v-btn
                >
                <v-btn
                  flat
                  color="primary"
                  @click="$refs.dialog1.save(startTime)"
                  data-cy="start-time-ok"
                  >{{ $t("actions.confirm") }}</v-btn
                >
              </v-time-picker>
            </v-dialog>
          </v-flex>
        </v-layout>
        <v-layout v-if="endDateTimeField">
          <v-flex xs12 md6>
            <!-- End Date -->
            <v-menu
              :close-on-content-click="false"
              v-model="showEndDatePicker"
              :nudge-right="40"
              lazy
              transition="scale-transition"
              offset-y
              full-width
              min-width="290px"
              data-cy="end-date-menu"
              :disabled="!startDateTimeSelected"
            >
              <v-text-field
                slot="activator"
                v-model="endDate"
                v-bind:label="$t('events.end-date')"
                prepend-icon="event"
                name="endDate"
                ref="endDate"
                v-validate="'required'"
                v-bind:error-messages="errors.first('endDate')"
                readonly
                :disabled="!startDateTimeSelected"
              ></v-text-field>

              <v-date-picker
                v-bind:locale="currentLanguageCode"
                v-model="endDate"
                @input="showEndDatePicker = false"
                data-cy="end-date-picker"
                :min="startDate || today"
              ></v-date-picker>
            </v-menu>
          </v-flex>
          <v-flex xs12 md6 ml-5>
            <!-- End Time -->
            <v-dialog
              ref="dialog2"
              v-model="endTimeModal"
              :disabled="!startDateTimeSelected"
              :return-value.sync="endTime"
              lazy
              full-width
              width="290px"
              persistent
              data-cy="end-time-dialog"
            >
              <v-text-field
                slot="activator"
                v-model="endTime"
                name="endTime"
                v-validate="'required'"
                v-bind:error-messages="errors.first('endTime')"
                v-bind:label="$t('events.end-time')"
                prepend-icon="update"
                :disabled="!startDateTimeSelected"
                readonly
              ></v-text-field>
              <v-time-picker
                v-if="endTimeModal"
                :format="timeFormat"
                v-model="endTime"
                :min="startDate == endDate ? startTime : null"
                data-cy="end-time-picker"
              >
                <v-spacer></v-spacer>
                <v-btn
                  flat
                  color="primary"
                  @click="endTimeModal = false"
                  data-cy="end-time-cancel"
                  >{{ $t("actions.cancel") }}</v-btn
                >
                <v-btn
                  flat
                  color="primary"
                  @click="$refs.dialog2.save(endTime)"
                  data-cy="end-time-ok"
                  >{{ $t("actions.confirm") }}</v-btn
                >
              </v-time-picker>
            </v-dialog>
          </v-flex>
        </v-layout>
        <input
          name="today"
          type="text"
          ref="today"
          v-bind:value="today"
          hidden
          readonly
        />
      </form>
    </v-card-text>
    <v-divider></v-divider>
    <v-card-actions>
      <v-btn
        color="secondary"
        flat
        v-on:click="cancel"
        :disabled="formDisabled"
        data-cy="form-cancel"
        >{{ $t("actions.cancel") }}</v-btn
      >
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        outline
        v-on:click="addAnother"
        v-if="!editMode"
        :loading="addMoreLoading"
        :disabled="formDisabled"
        data-cy="form-addanother"
        >{{ $t("actions.add-another") }}</v-btn
      >
      <v-btn
        color="primary"
        raised
        v-on:click="save"
        :loading="saveLoading"
        :disabled="formDisabled"
        data-cy="form-save"
        >{{ $t("actions.save") }}</v-btn
      >
    </v-card-actions>
  </v-card>
</template>

<script>
//When using this component, pass the prop (label or boolean) for all fields you wish to display. 
import { isEmpty } from "lodash";
import { mapGetters } from "vuex";
import EntitySearch from "./EntitySearch";
import AddressForm from "./AddressForm";
import ImageChooser from "./images/ImageChooser";

export default {
  components: {
    "entity-search": EntitySearch,
    "address-form": AddressForm,
    "image-chooser": ImageChooser
  },
  name: "CustomForm",
  props: {
    addMoreLoading: {
      type: Boolean
    },
    addImageField: {
      type: Boolean,
      required: false,
      default: false
    },
    descriptionLabel: {
      type: String,
      required: false
    },
    editMode: {
      type: Boolean,
      required: true
    },
    endDateTimeField: {
        type: Boolean,
        required: false,
        default: false
    },
    locationLabel: {
      type: String,
      required: false
    },
    initialData: {
      type: Object,
      default: null
    },
    saveLoading: {
      type: Boolean
    },
    startDateTimeField: {
        type: Boolean,
        required: false,
        default: false
    },
    titleLabel: {
      type: String,
      required: false
    }
  },
  data: function() {
    return {
      object: {},
      startTime: "",
      startDate: "",
      endTime: "",
      endDate: "",
      addMore: false,
      showStartDatePicker: false,
      showEndDatePicker: false,
      startTimeModal: false,
      endTimeModal: false,
      showAddressCreator: false,
      showImageChooser: false,
      imageSaved: false,
      currentAddress: 0
    };
  },

  watch: {
    // Make sure data stays in sync with any changes to `initialData` from parent.
    initialData(eventProp) {
      if (isEmpty(eventProp)) {
        this.clear();
      } else {
        this.object = eventProp;
        if (this.object.start != null) {
          this.object.start = new Date(this.object.start);
          this.startDate = this.getDateFromTimestamp(this.object.start);
          this.startTime = this.getTimeFromTimestamp(this.object.start);
        }
        if (this.object.end != null) {
          this.object.end = new Date(this.object.end);
          this.endDate = this.getDateFromTimestamp(this.object.end);
          this.endTime = this.getTimeFromTimestamp(this.object.end);
        }
        if (this.object.images && this.object.images.length > 0) {
          this.showImageChooser = true;
          this.imageSaved = true;
        } else {
          this.showImageChooser = false;
          this.imageSaved = false;
        }
      }
    },

    startDate(date) {
      this.clearEndTimeIfInvalid();
      if (!this.endDate || new Date(this.endDate) < new Date(date)) {
        if (!this.object.dayDuration) {
          this.endDate = date;
        } else {
          this.endDate = this.addDaystoDate(date, this.object.dayDuration);
        }
      }
    },

    endDate() {
      this.clearEndTimeIfInvalid();
    }
  },
  computed: {
    // List the keys in an Event record.
    eventKeys() {
      return Object.keys(this.object);
    },
    title() {
      return this.editMode ? this.$t(this.editText) : this.$t(this.createText);
    },

    timeFormat() {
      if (this.currentLanguageCode.substring(0, 2) == "en") {
        return "ampm";
      } else return "24hr";
    },

    formDisabled() {
      return (
        this.saveLoading ||
        this.addMoreLoading ||
        this.showAddressCreator ||
        (this.showImageChooser && !this.imageSaved)
      );
    },

    today() {
      return this.getDateFromTimestamp(Date.now());
    },

    startDateTimeSelected() {
      return this.startDate && this.startTime;
    },

    getImageId() {
      if (this.object.images) {
        return this.object.images.length > 0
          ? this.object.images[0].image_id
          : -1;
      } else {
        return -1;
      }
    },

    ...mapGetters(["currentLanguageCode"])
  },

  methods: {
    cancel() {
      this.$emit("cancel");
    },

    // Clear the form and the validators.
    clear() {
      for (let key of this.eventKeys) {
        this.object[key] = "";
      }
      delete this.object.location;
      this.startTime = "";
      this.startDate = "";
      this.endTime = "";
      this.endDate = "";
      this.showStartDatePicker = false;
      this.showEndDatePicker = false;
      this.startTimeModal = false;
      this.endTimeModal = false;
      this.showImageChooser = false;
      this.showAddressCreator = false;
      this.$validator.reset();
    },

    save() {
      this.$validator.validateAll().then(() => {
        if (!this.errors.any()) {
          this.object.start = this.getTimestamp(this.startDate, this.startTime);
          this.object.end = this.getTimestamp(this.endDate, this.endTime);
          this.object.active = true;
          if (this.addMore) this.$emit("addAnother", this.object);
          else this.$emit("save", this.object);
        }
        this.addMore = false;
      });
    },

    addAnother() {
      this.addMore = true;
      this.save();
    },

    getTimestamp(date, time) {
      let datems = new Date(date).getTime();
      let timemin = this.getMinutesFromTime(time);
      let timems = timemin * 60000;
      let tzoffset = new Date().getTimezoneOffset() * 60000;
      return new Date(datems + timems + tzoffset);
    },

    getMinutesFromTime(time) {
      let timearr = time.split(":");
      let mins = Number(timearr[0]) * 60 + Number(timearr[1]);
      return mins;
    },

    getDateFromTimestamp(ts) {
      let date = new Date(ts);
      if (date.getTime() < 86400000) {
        //ms in a day
        return "";
      }
      let yr = date.toLocaleDateString(this.currentLanguageCode, {
        year: "numeric"
      });
      let mo = date.toLocaleDateString(this.currentLanguageCode, {
        month: "2-digit"
      });
      let da = date.toLocaleDateString(this.currentLanguageCode, {
        day: "2-digit"
      });
      return `${yr}-${mo}-${da}`;
    },

    getTimeFromTimestamp(ts) {
      let date = new Date(ts);
      let hr = String(date.getHours()).padStart(2, "0");
      let min = String(date.getMinutes()).padStart(2, "0");
      return `${hr}:${min}`;
    },

    addDaystoDate(date, dayDuration) {
      let date1 = this.getTimestamp(date, "00:00");
      date1.setDate(date1.getDate() + dayDuration);
      return this.getDateFromTimestamp(date1);
    },

    clearEndTimeIfInvalid() {
      if (this.startDate == this.endDate) {
        let endMins = this.getMinutesFromTime(this.endTime);
        let startMins = this.getMinutesFromTime(this.startTime);
        if (endMins < startMins) {
          this.endTime = "";
        }
      }
    },

    updateEntitySearch(address) {
      console.log(address);
      this.object.location = address;
      this.currentAddress = address.address_id;
    },

    chooseImage(id) {
      this.object.newImageId = id;
      this.imageSaved = true;
    },

    deleteImage() {
      this.showImageChooser = false;
      delete this.object.newImageId;
      this.object.images = [];
      this.imageSaved = false;
    },

    cancelImageChooser() {
      this.showImageChooser = false;
    },

    missingImage() {
      this.imageSaved = false;
    }
  }
};
</script>
