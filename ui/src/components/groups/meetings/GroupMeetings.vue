<template>
  <div>
    <v-toolbar>
      <v-toolbar-title>{{ t("groups.meetings.title") }}</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-text-field
        v-model="search"
        append-icon="search"
        v-bind:label="t('actions.search')"
        single-line
        hide-details
      ></v-text-field>
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        variant="elevated"
        v-on:click="activateCreateMeetingDialog"
        data-cy="add-meeting"
      >
        <v-icon dark left>add</v-icon>
        {{ t("groups.meetings.add-meeting") }}
      </v-btn>
    </v-toolbar>
    <v-data-table
      :items-per-page-options="rowsPerPageItem"
      :headers="headers"
      :items="meetings"
      :search="search"
      :loading="tableLoading"
      class="elevation-1"
    >
      <template #item="{ item }">
        <tr>
          <td>{{ item.description }}</td>
          <td>{{ formatDate(item.startTime) }}</td>
          <td>{{ formatDate(item.stopTime) }}</td>
          <td>{{ getDisplayLocation(item.location) }}</td>
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
              <v-tooltip bottom v-if="!item.active">
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

    <!-- Archive dialog -->
    <v-dialog v-model="archiveDialog.show" max-width="350px">
      <v-card>
        <v-card-text>{{
          t("groups.messages.confirm-member-archive")
        }}</v-card-text>
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
            v-on:click="archiveGroup"
            color="primary"
            variant="elevated"
            :loading="archiveDialog.loading"
            data-cy="confirm-archive"
            >{{ t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Add/Edit Meeting Dialog -->
    <v-dialog v-model="meetingDialog.show" persistent max-width="500px">
      <MeetingForm
        :edit-mode="false"
        :initial-data="meetingDialog.meeting"
        :save-loading="meetingDialog.saveLoading"
        descriptionLabel="Description Label"
        locationLabel="Location Label"
        startDateTimeField
        endDateTimeField
        v-on:cancel="cancelMeetingDialog"
        v-on:save="saveMeeting"
      ></MeetingForm>
    </v-dialog>

    <!-- Delete dialog -->
    <v-dialog v-model="deleteDialog.show" max-width="350px">
      <v-card>
        <v-card-text>{{
          t("events.participants.confirm-remove")
        }}</v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelDelete"
            color="secondary"
            variant="text"
            data-cy="cancel-delete"
            >{{ t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="deleteParticipant"
            color="primary"
            variant="elevated"
            :loading="deleteDialog.loading"
            data-cy="confirm-delete"
            >{{ t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar.show">
      {{ snackbar.text }}
      <template #actions>
        <v-btn variant="text" @click="snackbar.show = false">
          {{ t("actions.close") }}
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import CustomForm from "../../CustomForm.vue";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;
const route = useRoute();

// CustomForm used as MeetingForm
const MeetingForm = CustomForm;

const rowsPerPageItem = [10, 15, 25, { title: "All", value: -1 }];
const tableLoading = ref(false);
const search = ref("");
const meetings = ref<any[]>([]);

const meetingDialog = ref({
  show: false,
  meeting: null as any,
  saveLoading: false
});

const deleteDialog = ref({
  show: false,
  participantId: -1,
  loading: false
});

const archiveDialog = ref({
  show: false,
  memberId: -1,
  loading: false
});

const snackbar = ref({ show: false, text: "" });

const headers = computed(() => [
  { title: t("groups.description"), value: "description", width: "20%" },
  { title: t("events.start-time"), value: "startTime", width: "20%" },
  { title: t("events.stop-time"), value: "stopTime", width: "22.5%" },
  { title: t("events.event-location"), value: "location_name" },
  { title: t("actions.header"), sortable: false }
]);

function formatDate(dateStr: string) {
  if (!dateStr) return "";
  return new Date(dateStr).toLocaleString();
}

function activateCreateMeetingDialog() {
  meetingDialog.value.show = true;
}

function cancelMeetingDialog() {
  meetingDialog.value.show = false;
}

function saveMeeting(meeting: any) {
  meetingDialog.value.saveLoading = true;

  meeting.groupId = route.params.group;
  meeting.addressId = meeting.location.address.id;
  meeting.startTime = meeting.start;
  meeting.stopTime = meeting.end;

  delete meeting.location;
  delete meeting.start;
  delete meeting.end;
  console.log(meeting);

  const existingMeeting = meetings.value.find(({ id }) => id === meeting.id);
  if (typeof existingMeeting === "undefined") {
    createMeeting(meeting);
  } else {
    updateMeeting(meeting);
  }
}

function createMeeting(meeting: any) {
  return http
    .post(`/api/v1/groups/meetings`, meeting)
    .then(() => {
      console.log("meeting created");
      showSnackbar(t("groups.messages.meeting-added"));
      meetingDialog.value.saveLoading = false;
      meetingDialog.value.show = false;
      getMeetings();
    })
    .catch(err => {
      console.log(err);
      meetingDialog.value.saveLoading = false;
      showSnackbar(t("groups.messages.error-adding-meeting"));
    });
}

function updateMeeting(_meeting: any) {
  // placeholder for update logic
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

function deleteParticipant() {
  deleteDialog.value.loading = true;
  const participantId = deleteDialog.value.participantId;
  const id = route.params.event;
  http
    .delete(`/api/v1/events/${id}/participants/${participantId}`)
    .then(() => {
      deleteDialog.value.loading = false;
      deleteDialog.value.show = false;
      showSnackbar(t("events.participants.removed"));
    })
    .catch(err => {
      console.log(err);
      deleteDialog.value.loading = false;
      deleteDialog.value.show = false;
      showSnackbar(t("events.participants.error-removing"));
    });
}

function cancelDelete() {
  deleteDialog.value.show = false;
}

function showSnackbar(message: string) {
  snackbar.value.text = message;
  snackbar.value.show = true;
}

function activateArchiveDialog(memberId: number) {
  archiveDialog.value.show = true;
  archiveDialog.value.memberId = memberId;
}

function confirmArchive(event: any) {
  console.log(event);
  activateArchiveDialog(event.id);
}

function cancelArchive() {
  archiveDialog.value.show = false;
}

function archiveGroup() {
  console.log("Archived member");
  archiveDialog.value.loading = true;
  const memberId = archiveDialog.value.memberId;
  const idx = meetings.value.findIndex((ev: any) => ev.id === memberId);
  http
    .put(`/api/v1/groups/members/deactivate/${memberId}`)
    .then(resp => {
      console.log("ARCHIVE", resp);
      meetings.value[idx].active = false;
      archiveDialog.value.loading = false;
      archiveDialog.value.show = false;
      showSnackbar(t("groups.messages.member-archived"));
    })
    .catch(err => {
      console.error("ARCHIVE FALURE", err.response);
      archiveDialog.value.loading = false;
      archiveDialog.value.show = false;
      showSnackbar(t("groups.messages.error-archiving-member"));
    });
}

function unarchive(member: any) {
  const idx = meetings.value.findIndex((ev: any) => ev.id === member.id);
  const memberId = member.id;
  member.id *= -1;
  http
    .put(`/api/v1/groups/members/activate/${memberId}`)
    .then(resp => {
      console.log("UNARCHIVED", resp);
      Object.assign(meetings.value[idx], resp.data);
      showSnackbar(t("groups.messages.member-unarchived"));
    })
    .catch(err => {
      console.error("UNARCHIVE FALURE", err.response);
      showSnackbar(t("groups.messages.error-unarchiving-member"));
    });
}

function getMeetings() {
  tableLoading.value = true;
  const id = route.params.group;
  http.get(`/api/v1/groups/meetings/group/${id}`).then(resp => {
    if (!resp.data.msg) {
      meetings.value = resp.data;
    }
    console.log(meetings.value);
    tableLoading.value = false;
  });
}

onMounted(() => {
  getMeetings();
});
</script>
