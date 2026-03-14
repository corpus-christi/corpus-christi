<template>
  <v-col>
    <v-row wrap>
      <v-col cols="12">
        <v-card class="ma-1">
          <template v-if="eventLoaded">
            <v-container fill-height fluid>
              <v-col cols="9" sm="9" class="align-end">
                <span class="headline">{{ event.title }}</span>
              </v-col>
              <v-row cols="3" sm="3" align="end" justify="end">
                <v-btn
                  variant="text"
                  color="primary"
                  data-cy="edit-event"
                  v-on:click="editEvent(event)"
                >
                  <v-icon>edit</v-icon>&nbsp;{{ t("actions.edit") }}
                </v-btn>
              </v-row>
            </v-container>
            <v-card-text class="pa-4">
              <v-row wrap>
                <v-col cols="12" sm="6">
                  <div>
                    <b>{{ t("events.attendance") }}: </b>
                    <span v-if="event.attendance != null">{{
                      event.attendance
                    }}</span>
                    <span v-else>{{ t("events.attendance-none") }}</span>
                    <v-btn
                      icon
                      variant="outlined"
                      size="small"
                      color="primary"
                      data-cy="edit-attendance"
                      v-on:click="openAttendanceDialog()"
                    >
                      <v-icon size="small" color="primary">edit</v-icon>
                    </v-btn>
                  </div>
                  <div v-if="event.location">
                    <b>{{ t("events.location") }}: </b>
                    <div class="multi-line ml-2">{{ displayLocation }}</div>
                  </div>
                  <div>
                    <b>{{ t("events.start-time") }}: </b
                    >{{ getDisplayDate(event.start) }}
                  </div>
                  <div>
                    <b>{{ t("events.end-time") }}: </b
                    >{{ getDisplayDate(event.end) }}
                  </div>
                  <div class="mt-2 mb-2">{{ event.description }}</div>
                </v-col>
                <v-col cols="12" sm="6">
                  <!-- Image -->
                  <template v-if="event.images && event.images.length > 0">
                    <v-img
                      max-height="400px"
                      class="image picture"
                      :src="fetchImage"
                    >
                    </v-img>
                  </template>

                  <!-- Placeholder if no image uploaded -->
                  <template v-else>
                    <v-img class="picture" :src="arcoPlaceholder"> </v-img>
                  </template>
                </v-col>
              </v-row>
            </v-card-text>
            <v-card-actions>
              <v-row justify="space-between" wrap>
                <v-btn
                  variant="text"
                  color="primary"
                  data-cy="navigate-to-participants"
                  :to="'/event/' + route.params.event + '/participants'"
                >
                  <v-icon>person</v-icon>&nbsp;{{
                    t("events.participants.title")
                  }}
                </v-btn>
              </v-row>
            </v-card-actions>
          </template>
          <v-row v-else justify="center" style="height: 500px;">
            <div class="ma-5 pa-5">
              <v-progress-circular
                indeterminate
                color="primary"
              ></v-progress-circular>
            </div>
          </v-row>
        </v-card>
      </v-col>
    </v-row>

    <v-row wrap>
      <v-col cols="12" lg="6">
        <v-col>
          <event-team-details
            :teams="event.teams"
            :loaded="teamsLoaded"
            v-on:snackbar="showSnackbar($event)"
            v-on:team-added="reloadTeams()"
          ></event-team-details>
          <event-person-details
            :persons="event.persons"
            :loaded="personsLoaded"
            v-on:snackbar="showSnackbar($event)"
            v-on:person-added="reloadPersons()"
          ></event-person-details>
        </v-col>
      </v-col>
      <v-col cols="12" lg="6">
        <v-col>
          <event-asset-details
            :assets="event.assets"
            :loaded="assetsLoaded"
            v-on:snackbar="showSnackbar($event)"
            v-on:asset-added="reloadAssets()"
          ></event-asset-details>
          <event-group-details
            :groups="event.groups"
            :loaded="groupsLoaded"
            v-on:snackbar="showSnackbar($event)"
            v-on:group-added="reloadGroups()"
          ></event-group-details>
        </v-col>
      </v-col>
    </v-row>

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <template #actions>
        <v-btn variant="text" @click="snackbar.show = false" data-cy="close-snackbar">
          {{ t("actions.close") }}
        </v-btn>
      </template>
    </v-snackbar>

    <!-- Edit Event dialog -->
    <v-dialog v-model="eventDialog.show" persistent max-width="500px">
      <event-form
        v-bind:editMode="true"
        v-bind:initialData="eventDialog.event"
        v-bind:saveLoading="eventDialog.saveLoading"
        v-on:cancel="cancelEvent"
        v-on:save="saveEvent"
        addImageField
        endDateTimeField
        startDateTimeField
        v-bind:titleLabel="t('events.title')"
        v-bind:descriptionLabel="t('events.event-description')"
        v-bind:locationLabel="t('events.event-location')"
      />
    </v-dialog>

    <!-- Attendance dialog -->
    <v-dialog v-model="attendanceDialog.show" persistent max-width="250px">
      <event-attendance-form
        v-bind:attendance="attendanceDialog.number"
        v-bind:saving="attendanceDialog.saving"
        v-on:cancel="attendanceDialog.show = false"
        v-on:save-attendance="saveAttendance($event)"
      ></event-attendance-form>
    </v-dialog>
  </v-col>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import { useAuthStore } from "@/stores/auth";
import CustomForm from "../CustomForm.vue";
import EventTeamDetails from "./EventTeamDetails.vue";
import EventAssetDetails from "./EventAssetDetails.vue";
import EventPersonDetails from "./EventPersonDetails.vue";
import EventGroupDetails from "./EventGroupDetails.vue";
import EventAttendanceForm from "./EventAttendanceForm.vue";
import arcoPlaceholderImg from "../../../assets/arco-placeholder.jpg";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;
const route = useRoute();
const authStore = useAuthStore();

// Component aliases
const eventForm = CustomForm;
const eventTeamDetails = EventTeamDetails;
const eventAssetDetails = EventAssetDetails;
const eventPersonDetails = EventPersonDetails;
const eventGroupDetails = EventGroupDetails;
const eventAttendanceForm = EventAttendanceForm;

const event = ref<Record<string, any>>({});
const eventDialog = ref({ show: false, saveLoading: false, event: {} as Record<string, any> });
const attendanceDialog = ref({ show: false, saving: false, number: null as any });
const snackbar = ref({ show: false, text: "" });
const eventLoaded = ref(false);
const teamsLoaded = ref(false);
const groupsLoaded = ref(false);
const assetsLoaded = ref(false);
const personsLoaded = ref(false);
const arcoPlaceholder = arcoPlaceholderImg;

const displayLocation = computed(() => {
  let location = event.value.location;
  let str = "";
  if (location) {
    str += `${location.description}`;
    if (location.address) {
      str += `\n${location.address.name}`;
      str += `\n${location.address.address}`;
      str += `\n${location.address.city}, ${location.address.country?.code}`;
    }
  }
  return str;
});

const fetchImage = computed(() => {
  return `/api/v1/images/${event.value.images?.[0]?.image?.id}?${Math.random()}`;
});

function getEvent() {
  const id = route.params.event;
  return http
    .get(`/api/v1/events/${id}?include_teams=1&include_assets=1&include_persons=1&include_images=1&include_groups=1`)
    .then(resp => {
      event.value = resp.data;
      event.value.teams = !event.value.teams
        ? []
        : event.value.teams.map((t: any) => t.team);
      event.value.assets = !event.value.assets
        ? []
        : event.value.assets.map((a: any) => a.asset);
      event.value.groups = !event.value.groups
        ? []
        : event.value.groups
            .filter((g: any) => {
              if (g.group) {
                return g.active && g.group.active;
              }
              return false;
            })
            .map((g: any) => g.group);
      event.value.persons = !event.value.persons
        ? []
        : event.value.persons.map((p: any) => Object.assign(p, { id: p.person_id }));
    });
}

function reloadTeams() {
  teamsLoaded.value = false;
  const id = route.params.event;
  http.get(`/api/v1/events/${id}?include_teams=1`).then(resp => {
    let eventData = resp.data;
    event.value.teams = !eventData.teams
      ? []
      : eventData.teams.map((t: any) => t.team);
    teamsLoaded.value = true;
  });
}

function reloadAssets() {
  assetsLoaded.value = false;
  const id = route.params.event;
  http.get(`/api/v1/events/${id}?include_assets=1`).then(resp => {
    let eventData = resp.data;
    event.value.assets = !eventData.assets
      ? []
      : eventData.assets.map((a: any) => a.asset);
    assetsLoaded.value = true;
  });
}

function reloadPersons() {
  personsLoaded.value = false;
  const id = route.params.event;
  http.get(`/api/v1/events/${id}?include_persons=1`).then(resp => {
    let eventData = resp.data;
    event.value.persons = !eventData.persons
      ? []
      : eventData.persons.map((p: any) => Object.assign(p, { id: p.person_id }));
    personsLoaded.value = true;
  });
}

function reloadGroups() {
  groupsLoaded.value = false;
  const id = route.params.event;
  http.get(`/api/v1/events/${id}?include_groups=1`).then(resp => {
    let eventData = resp.data;
    event.value.groups = !eventData.groups
      ? []
      : eventData.groups
          .filter((g: any) => {
            if (g.group) {
              return g.active && g.group.active;
            }
            return false;
          })
          .map((g: any) => g.group);
    groupsLoaded.value = true;
  });
}

function editEvent(ev: any) {
  eventDialog.value.event = JSON.parse(JSON.stringify(ev));
  eventDialog.value.show = true;
}

function cancelEvent() {
  eventDialog.value.show = false;
}

async function saveEvent(ev: any) {
  eventDialog.value.saveLoading = true;
  if (ev.location) {
    ev.location_id = ev.location.id;
  }
  let newEvent = JSON.parse(JSON.stringify(ev));
  const oldImageId = await getOldImageId(ev.id);
  const newImageId = newEvent.newImageId;
  delete newEvent.newImageId;
  delete newEvent.location;
  delete newEvent.assets;
  delete newEvent.teams;
  delete newEvent.groups;
  delete newEvent.persons;
  delete newEvent.dayDuration;
  delete newEvent.id;
  delete newEvent.images;
  const eventId = ev.id;

  const finishSave = () => {
    http.put(`/api/v1/events/${eventId}`, newEvent)
      .then(resp => {
        console.log("EDITED", resp);
        eventDialog.value.show = false;
        eventDialog.value.saveLoading = false;
        eventLoaded.value = false;
        getEvent().then(() => (eventLoaded.value = true));
        showSnackbar(t("events.event-edited"));
      })
      .catch(err => {
        console.error("PUT FAILURE", err.response);
        eventDialog.value.saveLoading = false;
        showSnackbar(t("events.error-editing-event"));
      });
  };

  if (newImageId) {
    if (oldImageId) {
      http.put(`/api/v1/events/${eventId}/images/${newImageId}?old=${oldImageId}`)
        .then(() => finishSave())
        .catch(err => {
          console.error("ERROR PUTTING IMAGE", err.response);
          eventDialog.value.saveLoading = false;
          showSnackbar(t("events.error-editing-event"));
        });
    } else {
      http.post(`/api/v1/events/${eventId}/images/${newImageId}`)
        .then(() => finishSave())
        .catch(err => {
          console.error("ERROR POSTING IMAGE", err.response);
          eventDialog.value.saveLoading = false;
          showSnackbar(t("events.error-editing-event"));
        });
    }
  } else {
    if (oldImageId) {
      http.delete(`/api/v1/events/${eventId}/images/${oldImageId}`)
        .then(() => finishSave())
        .catch(err => {
          console.error("ERROR DELETING IMAGE", err.response);
          eventDialog.value.saveLoading = false;
          showSnackbar(t("events.error-editing-event"));
        });
    } else {
      finishSave();
    }
  }
}

async function getOldImageId(id: any) {
  if (!id) return null;
  return await http
    .get(`/api/v1/events/${id}?include_images=1`)
    .then(resp => {
      if (resp.data.images && resp.data.images.length > 0) {
        return resp.data.images[0].image_id;
      } else {
        return null;
      }
    })
    .catch(err => {
      console.error("ERROR FETCHING EVENT", err);
      return null;
    });
}

function openAttendanceDialog() {
  attendanceDialog.value.show = true;
  attendanceDialog.value.saving = false;
  attendanceDialog.value.number = event.value.attendance;
}

function closeAttendanceDialog() {
  attendanceDialog.value.show = false;
  attendanceDialog.value.saving = false;
  attendanceDialog.value.number = null;
}

function saveAttendance(number: number) {
  const id = route.params.event;
  http
    .patch(`/api/v1/events/${id}`, { attendance: number })
    .then(resp => {
      console.log(resp);
      event.value.attendance = resp.data.attendance;
      closeAttendanceDialog();
    })
    .catch(err => {
      console.error("ATTENDANCE PATCH FAILURE", err.response);
      attendanceDialog.value.saving = false;
    });
}

function getDisplayDate(ts: any) {
  let date = new Date(ts);
  return date.toLocaleTimeString(authStore.currentLanguageCode, {
    year: "numeric",
    month: "numeric",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  });
}

function showSnackbar(message: string) {
  snackbar.value.text = message;
  snackbar.value.show = true;
}

onMounted(() => {
  eventLoaded.value = false;
  teamsLoaded.value = false;
  groupsLoaded.value = false;
  assetsLoaded.value = false;
  personsLoaded.value = false;
  getEvent().then(() => {
    eventLoaded.value = true;
    teamsLoaded.value = true;
    groupsLoaded.value = true;
    assetsLoaded.value = true;
    personsLoaded.value = true;
  });
});
</script>

<style scoped>
.multi-line {
  white-space: pre;
}
</style>
