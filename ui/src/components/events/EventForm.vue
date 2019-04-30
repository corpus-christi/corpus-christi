<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ title }}</span>
    </v-card-title>
    <v-card-text>
      <form>
        <v-layout align-space-around justify-center column fill-height>
          <v-text-field
            v-model="event.title"
            v-bind:label="$t('events.title')"
            name="title"
            v-validate="'required'"
            v-bind:error-messages="errors.first('title')"
            data-cy="title"
          ></v-text-field>
          <v-textarea
            rows="3"
            v-model="event.description"
            v-bind:label="$t('events.event-description')"
            name="description"
            data-cy="description"
          ></v-textarea>
          <v-btn
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
        <v-layout align-center justify-space-around>
          <v-flex>
            <entity-search
              location
              v-model="event.location"
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

        <v-layout>
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
        <v-layout>
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
import { isEmpty } from "lodash";
import { mapGetters } from "vuex";
import EntitySearch from "../EntitySearch";
import AddressForm from "../AddressForm";
import ImageChooser from "../images/ImageChooser";

export default {
  components: {
    "entity-search": EntitySearch,
    "address-form": AddressForm,
    "image-chooser": ImageChooser
  },
  name: "EventForm",
  props: {
    editMode: {
      type: Boolean,
      required: true
    },
    initialData: {
      type: Object,
      required: true
    },
    saveLoading: {
      type: Boolean
    },
    addMoreLoading: {
      type: Boolean
    }
  },
  data: function() {
    return {
      event: {},
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
        this.event = eventProp;
        if (this.event.start != null) {
          this.event.start = new Date(this.event.start);
          this.startDate = this.getDateFromTimestamp(this.event.start);
          this.startTime = this.getTimeFromTimestamp(this.event.start);
        }
        if (this.event.end != null) {
          this.event.end = new Date(this.event.end);
          this.endDate = this.getDateFromTimestamp(this.event.end);
          this.endTime = this.getTimeFromTimestamp(this.event.end);
        }
        if (this.event.images && this.event.images.length > 0) {
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
        if (!this.event.dayDuration) {
          this.endDate = date;
        } else {
          this.endDate = this.addDaystoDate(date, this.event.dayDuration);
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
      return Object.keys(this.event);
    },
    title() {
      return this.editMode
        ? this.$t("events.edit-event")
        : this.$t("events.create-event");
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
      if (this.event.images) {
        return this.event.images.length > 0
          ? this.event.images[0].image_id
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
        this.event[key] = "";
      }
      delete this.event.location;
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
          this.event.start = this.getTimestamp(this.startDate, this.startTime);
          this.event.end = this.getTimestamp(this.endDate, this.endTime);
          this.event.active = true;
          if (this.addMore) this.$emit("addAnother", this.event);
          else this.$emit("save", this.event);
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
      this.event.location = address;
      this.currentAddress = address.address_id;
    },

    chooseImage(id) {
      this.event.newImageId = id;
      this.imageSaved = true;
    },

    deleteImage() {
      this.showImageChooser = false;
      delete this.event.newImageId;
      this.event.images = [];
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
