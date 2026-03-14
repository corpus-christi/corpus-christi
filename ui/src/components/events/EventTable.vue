<template>
  <div>
    <v-row justify="center">
      <v-col shrink class="mb-2">
        <h1 class="hidden-sm-and-up">{{ t("events.header") }}</h1>
      </v-col>
    </v-row>
    <v-toolbar class="pa-1">
      <v-row justify="space-between">
        <v-col shrink class="align-self-center">
          <v-toolbar-title class="hidden-xs-only">{{
            t("events.header")
          }}</v-toolbar-title>
        </v-col>
        <v-spacer></v-spacer>
        <v-text-field
          class="max-width-250 mr-2"
          v-model="search"
          append-icon="search"
          v-bind:label="t('actions.search')"
          single-line
          hide-details
          data-cy="form-search"
        ></v-text-field>
        <v-col shrink>
          <v-btn
            class="hidden-xs-only mr-2"
            color="primary"
            variant="elevated"
            v-on:click.stop="newEvent"
            data-cy="add-event"
          >
            <v-icon dark>add</v-icon>
            <span class="mr-1"> {{ t("actions.add-event") }} </span>
          </v-btn>
          <v-btn
            class="hidden-sm-and-up"
            color="primary"
            variant="elevated"
            icon
            v-on:click.stop="newEvent"
            data-cy="add-event-small"
          >
            <v-icon dark>add</v-icon>
          </v-btn>
        </v-col>
      </v-row>
      <template #extension>
        <v-row justify="space-between" align="center">
          <v-col>
            <v-select
              class="max-width-250 mr-2"
              hide-details
              solo
              single-line
              :items="viewOptions"
              v-model="viewStatus"
              data-cy="view-status-select"
            >
            </v-select>
          </v-col>
          <v-col shrink>
            <v-switch
              hide-details
              v-model="viewPast"
              data-cy="view-past-switch"
              v-bind:label="t('actions.view-past')"
            >
            </v-switch>
          </v-col>
        </v-row>
      </template>
    </v-toolbar>
    <v-data-table
      :headers="headers"
      :items-per-page-options="rowsPerPageItem"
      :items="visibleEvents"
      :search="search"
      :loading="tableLoading"
      class="elevation-1"
    >
      <template #item="{ item }">
        <!-- TODO: Add icons for past, upcoming, etc. -->
        <tr>
          <td>
            <v-icon
              v-if="eventOngoing(item)"
              size="small"
              color="secondary"
              >autorenew</v-icon
            >
          </td>
          <td class="hover-hand" v-on:click="navigateToEvent(item.id)">
            <span> {{ item.title }}</span>
          </td>
          <td class="hover-hand" v-on:click="navigateToEvent(item.id)">
            {{ getDisplayDate(item.start) }}
          </td>
          <td class="hover-hand" v-on:click="navigateToEvent(item.id)">
            {{ getDisplayLocation(item.location) }}
          </td>
          <td>
            <template v-if="item.active">
              <v-tooltip bottom>
                <template #activator="{ props: tooltipProps }">
                  <v-btn
                    icon
                    variant="outlined"
                    size="small"
                    color="primary"
                    v-bind="tooltipProps"
                    v-on:click="editEvent(item)"
                    data-cy="edit"
                  >
                    <v-icon size="small">edit</v-icon>
                  </v-btn>
                </template>
                <span>{{ t("actions.edit") }}</span>
              </v-tooltip>
              <v-tooltip bottom>
                <template #activator="{ props: tooltipProps }">
                  <v-btn
                    icon
                    variant="outlined"
                    size="small"
                    color="primary"
                    v-bind="tooltipProps"
                    v-on:click="duplicate(item)"
                    data-cy="duplicate"
                  >
                    <v-icon size="small">filter_none</v-icon>
                  </v-btn>
                </template>
                <span>{{ t("actions.duplicate") }}</span>
              </v-tooltip>
              <v-tooltip bottom>
                <template #activator="{ props: tooltipProps }">
                  <v-btn
                    icon
                    variant="outlined"
                    size="small"
                    color="primary"
                    v-bind="tooltipProps"
                    v-on:click="confirmArchive(item)"
                    data-cy="archive"
                  >
                    <v-icon size="small">archive</v-icon>
                  </v-btn>
                </template>
                <span>{{ t("actions.tooltips.archive") }}</span>
              </v-tooltip>
            </template>
            <template v-else>
              <v-tooltip bottom>
                <template #activator="{ props: tooltipProps }">
                  <v-btn
                    icon
                    variant="outlined"
                    size="small"
                    color="primary"
                    v-bind="tooltipProps"
                    v-on:click="unarchive(item)"
                    :loading="item.id < 0"
                    data-cy="unarchive"
                  >
                    <v-icon size="small">undo</v-icon>
                  </v-btn>
                </template>
                <span>{{ t("actions.tooltips.activate") }}</span>
              </v-tooltip>
            </template>
          </td>
        </tr>
      </template>
    </v-data-table>

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <template #actions>
        <v-btn variant="text" @click="snackbar.show = false">
          {{ t("actions.close") }}
        </v-btn>
      </template>
    </v-snackbar>

    <!-- New/Edit dialog -->
    <v-dialog v-model="eventDialog.show" max-width="500px" persistent>
      <event-form
        v-bind:editMode="eventDialog.editMode"
        v-bind:initialData="eventDialog.event"
        v-bind:saveLoading="eventDialog.saveLoading"
        v-bind:addMoreLoading="eventDialog.addMoreLoading"
        v-on:cancel="cancelEvent"
        v-on:save="saveEvent"
        v-on:addAnother="addAnother"
        addImageField
        endDateTimeField
        startDateTimeField
        v-bind:titleLabel="t('events.title')"
        v-bind:descriptionLabel="t('events.event-description')"
        v-bind:locationLabel="t('events.event-location')"
      />
    </v-dialog>

    <!-- Archive dialog -->
    <v-dialog v-model="archiveDialog.show" max-width="350px">
      <v-card>
        <v-card-text>{{ t("events.confirm-archive") }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelArchive"
            color="secondary"
            variant="text"
            data-cy="cancel-archive"
            >{{ t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="archiveEvent"
            color="primary"
            variant="elevated"
            :loading="archiveDialog.loading"
            data-cy="confirm-archive"
            >{{ t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import { useAuthStore } from "@/stores/auth";
import CustomForm from "../CustomForm.vue";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;
const router = useRouter();
const authStore = useAuthStore();

const rowsPerPageItem = [10, 15, 25, { title: "All", value: -1 }];
const tableLoading = ref(true);
const events = ref<any[]>([]);
const search = ref("");
const addMore = ref(false);
const viewStatus = ref("viewActive");
const viewPast = ref(false);

const eventDialog = ref({
  show: false,
  editMode: false,
  saveLoading: false,
  addMoreLoading: false,
  event: {} as any
});

const archiveDialog = ref({ show: false, eventId: -1, loading: false });
const snackbar = ref({ show: false, text: "" });

const headers = computed(() => [
  { title: "", sortable: false, width: "5%" },
  { title: t("events.title"), value: "title" },
  { title: t("events.start-time"), value: "start" },
  { title: t("events.event-location"), value: "location_name" },
  { title: t("actions.header"), sortable: false }
]);

const viewOptions = computed(() => [
  { title: t("actions.view-active"), value: "viewActive" },
  { title: t("actions.view-archived"), value: "viewArchived" },
  { title: t("actions.view-all"), value: "viewAll" }
]);

const visibleEvents = computed(() => {
  let list = events.value;
  if (!viewPast.value) {
    let today = new Date();
    list = events.value.filter(ev => new Date(ev.end) >= today);
  }
  if (viewStatus.value == "viewActive") {
    list = list.filter(ev => ev.active);
  } else if (viewStatus.value == "viewArchived") {
    list = list.filter(ev => !ev.active);
  }
  return list;
});

function activateEventDialog(event: any = {}, editMode = false) {
  eventDialog.value.editMode = editMode;
  eventDialog.value.event = event;
  eventDialog.value.show = true;
}

function editEvent(event: any) {
  activateEventDialog({ ...event }, true);
}

function activateArchiveDialog(eventId: number) {
  archiveDialog.value.show = true;
  archiveDialog.value.eventId = eventId;
}

function confirmArchive(event: any) {
  activateArchiveDialog(event.id);
}

function duplicate(event: any) {
  let id = event.id;
  http
    .get(`/api/v1/events/${id}?include_teams=1&include_assets=1&include_persons=1`)
    .then(resp => {
      const copyEvent = JSON.parse(JSON.stringify(resp.data));
      copyEvent.start = new Date(copyEvent.start);
      copyEvent.end = new Date(copyEvent.end);
      const startDate = copyEvent.start.toDateString();
      const endDate = copyEvent.end.toDateString();
      if (startDate != endDate) {
        const diff = copyEvent.end - copyEvent.start;
        copyEvent.dayDuration = Math.ceil(diff / 86400000);
      }
      copyEvent.start = new Date(copyEvent.start).getTime();
      copyEvent.end = new Date(copyEvent.end).getTime();
      copyEvent.start %= 86400000;
      copyEvent.end %= 86400000;
      delete copyEvent.id;
      activateEventDialog(copyEvent);
    })
    .catch(err => console.log("DUPLICATE ERROR", err));
}

function archiveEvent() {
  console.log("Archived event");
  archiveDialog.value.loading = true;
  const eventId = archiveDialog.value.eventId;
  const idx = events.value.findIndex(ev => ev.id === eventId);
  http
    .delete(`/api/v1/events/${eventId}`)
    .then(resp => {
      console.log("ARCHIVE", resp);
      events.value[idx].active = false;
      archiveDialog.value.loading = false;
      archiveDialog.value.show = false;
      showSnackbar(t("events.event-archived"));
    })
    .catch(err => {
      console.error("ARCHIVE FALURE", err.response);
      archiveDialog.value.loading = false;
      archiveDialog.value.show = false;
      showSnackbar(t("events.error-archiving-event"));
    });
}

function unarchive(event: any) {
  const idx = events.value.findIndex(ev => ev.id === event.id);
  const patchId = event.id;
  event.id *= -1;
  http
    .patch(`/api/v1/events/${patchId}`, { active: true })
    .then(resp => {
      console.log("UNARCHIVED", resp);
      Object.assign(events.value[idx], resp.data);
      showSnackbar(t("events.event-unarchived"));
    })
    .catch(err => {
      console.error("UNARCHIVE FALURE", err.response);
      showSnackbar(t("events.error-unarchiving-event"));
    });
}

function cancelArchive() {
  archiveDialog.value.show = false;
}

function newEvent() {
  activateEventDialog();
}

function clearEvent() {
  addMore.value = false;
  eventDialog.value.saveLoading = false;
  eventDialog.value.addMoreLoading = false;
  eventDialog.value.event = {};
}

function cancelEvent() {
  addMore.value = false;
  eventDialog.value.show = false;
  eventDialog.value.saveLoading = false;
  eventDialog.value.addMoreLoading = false;
}

function addAnother(event: any) {
  addMore.value = true;
  eventDialog.value.addMoreLoading = true;
  saveEvent(event);
}

function save(event: any) {
  eventDialog.value.saveLoading = true;
  saveEvent(event);
}

async function saveEvent(event: any) {
  if (event.location) {
    event.location_id = event.location.id;
  }
  delete event.images;

  let newEvent = JSON.parse(JSON.stringify(event));
  const oldImageId = await getOldImageId(event.id);
  const newImageId = newEvent.newImageId;
  delete newEvent.newImageId;
  delete newEvent.location;
  delete newEvent.dayDuration;
  delete newEvent.id;
  delete newEvent.aggregate;
  delete newEvent.attendance;

  console.log(newImageId, oldImageId);

  if (eventDialog.value.editMode) {
    const eventId = event.id;
    if (newImageId) {
      if (oldImageId) {
        http
          .put(`/api/v1/events/${eventId}/images/${newImageId}?old=${oldImageId}`)
          .then(resp => {
            console.log("IMAGEEVENT EDITED", resp);
            http
              .put(`/api/v1/events/${eventId}`, newEvent)
              .then(resp => {
                console.log("EDITED", resp);
                refreshEventsTable();
                cancelEvent();
                showSnackbar(t("events.event-edited"));
              })
              .catch(err => {
                console.error("PUT FALURE", err.response);
                eventDialog.value.saveLoading = false;
                showSnackbar(t("events.error-editing-event"));
              });
          })
          .catch(err => {
            console.error("ERROR PUTTING IMAGE ON EVENT", err.response);
            eventDialog.value.saveLoading = false;
            showSnackbar(t("events.error-editing-event"));
          });
      } else {
        http
          .post(`/api/v1/events/${eventId}/images/${newImageId}`)
          .then(resp => {
            console.log("IMAGEEVENT EDITED", resp);
            http
              .put(`/api/v1/events/${eventId}`, newEvent)
              .then(resp => {
                console.log("EDITED", resp);
                refreshEventsTable();
                cancelEvent();
                showSnackbar(t("events.event-edited"));
              })
              .catch(err => {
                console.error("PUT FALURE", err.response);
                eventDialog.value.saveLoading = false;
                showSnackbar(t("events.error-editing-event"));
              });
          })
          .catch(err => {
            console.error("ERROR ADDING IMAGE TO EVENT", err.response);
            eventDialog.value.saveLoading = false;
            showSnackbar(t("events.error-editing-event"));
          });
      }
    } else {
      if (oldImageId) {
        http
          .delete(`/api/v1/events/${eventId}/images/${oldImageId}`)
          .then(resp => {
            console.log("IMAGEEVENT EDITED", resp);
            http
              .put(`/api/v1/events/${eventId}`, newEvent)
              .then(resp => {
                console.log("EDITED", resp);
                refreshEventsTable();
                cancelEvent();
                showSnackbar(t("events.event-edited"));
              })
              .catch(err => {
                console.error("PUT FALURE", err.response);
                eventDialog.value.saveLoading = false;
                showSnackbar(t("events.error-editing-event"));
              });
          })
          .catch(err => {
            console.error("ERROR DELETING IMAGE FROM EVENT", err.response);
            eventDialog.value.saveLoading = false;
            showSnackbar(t("events.error-editing-event"));
          });
      } else {
        http
          .put(`/api/v1/events/${eventId}`, newEvent)
          .then(resp => {
            console.log("EDITED", resp);
            refreshEventsTable();
            cancelEvent();
            showSnackbar(t("events.event-edited"));
          })
          .catch(err => {
            console.error("PUT FALURE", err.response);
            eventDialog.value.saveLoading = false;
            showSnackbar(t("events.error-editing-event"));
          });
      }
    }
  } else {
    let newTeams = newEvent.teams;
    delete newEvent.teams;
    let newPersons = newEvent.persons;
    delete newEvent.persons;
    let newAssets = newEvent.assets;
    delete newEvent.assets;
    http
      .post("/api/v1/events/", newEvent)
      .then(resp => {
        let promises = getDuplicationPromises(
          resp.data.id,
          newTeams,
          newPersons,
          newAssets,
          newImageId
        );
        if (promises) {
          Promise.all(promises).then(values => {
            console.log(values);
            return resp;
          });
        }
        return resp;
      })
      .then(resp => {
        console.log("ADDED", resp);
        if (addMore.value) {
          clearEvent();
        } else {
          cancelEvent();
        }
        showSnackbar(t("events.event-added"));
        refreshEventsTable();
      })
      .catch(err => {
        console.error("POST FAILURE", err.response);
        eventDialog.value.saveLoading = false;
        eventDialog.value.addMoreLoading = false;
        showSnackbar(t("events.error-adding-event"));
      });
  }
}

function refreshEventsTable() {
  tableLoading.value = true;
  http
    .get("/api/v1/events/?return_group=all&include_images=1")
    .then(resp => {
      events.value = resp.data;
      tableLoading.value = false;
    });
}

function getDuplicationPromises(
  eventId: number,
  newTeams: any[],
  newPersons: any[],
  newAssets: any[],
  newImageId: any
) {
  if (!newTeams && !newPersons && !newAssets && !newImageId) return null;
  let promises: any[] = [];
  if (newTeams) {
    for (let team of newTeams) {
      promises.push(postEventTeam(eventId, team.team_id));
    }
  }
  if (newPersons) {
    for (let p of newPersons) {
      promises.push(postEventPerson(eventId, p.person_id, p.description));
    }
  }
  if (newAssets) {
    for (let a of newAssets) {
      promises.push(postEventAsset(eventId, a.asset_id));
    }
  }
  if (newImageId) {
    promises.push(postImageEvent(eventId, newImageId));
  }
  return promises;
}

function postEventTeam(eventId: number, teamId: number) {
  return http.post(`/api/v1/events/${eventId}/teams/${teamId}`);
}

function postEventAsset(eventId: number, assetId: number) {
  return http.post(`/api/v1/events/${eventId}/assets/${assetId}`);
}

function postEventPerson(eventId: number, personId: number, description: string) {
  return http.post(`/api/v1/events/${eventId}/individuals/${personId}`, { description });
}

function postImageEvent(eventId: number, newImageId: number) {
  return http.post(`/api/v1/events/${eventId}/images/${newImageId}`);
}

async function getOldImageId(id: number) {
  if (!id) {
    return null;
  }
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

function showSnackbar(message: string) {
  snackbar.value.text = message;
  snackbar.value.show = true;
}

function getDisplayDate(dateString: string) {
  let date = new Date(dateString);
  return date.toLocaleTimeString(authStore.currentLanguageCode, {
    year: "numeric",
    month: "numeric",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  });
}

function getDisplayLocation(location: any, length = 20) {
  if (location && location.description) {
    let name = location.description;
    if (name && name.length && name.length > 0) {
      if (name.length > length) {
        return `${name.substring(0, length - 3)}...`;
      }
      return name;
    }
  }
  return "";
}

function navigateToEvent(id: number) {
  router.push({ path: "/event/" + id });
}

function eventOngoing(event: any) {
  let start = new Date(event.start);
  let end = new Date(event.end);
  return start <= new Date() && new Date() <= end;
}

onMounted(() => {
  refreshEventsTable();
});
</script>

<style scoped>
.hover-hand {
  cursor: pointer;
}

.max-width-250 {
  max-width: 250px;
}
</style>
