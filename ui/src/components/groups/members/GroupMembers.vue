<template>
  <div>
    <v-toolbar>
      <v-row align="center" justify="space-between">
        <v-col md="3" class="text-no-wrap">
          <v-toolbar-title v-if="!select">{{
            t("events.participants.title")
          }}</v-toolbar-title>
          <v-btn
            color="primary"
            variant="elevated"
            v-on:click="toggleEmailDialog"
            v-if="select"
            icon
            size="small"
          >
            <v-icon>email</v-icon>
          </v-btn>
          <v-btn
            color="primary"
            variant="elevated"
            v-on:click="activateSelectArchiveDialog"
            data-cy="archive"
            v-if="select"
            icon
            size="small"
          >
            <v-icon>archive</v-icon>
          </v-btn>
          <v-btn
            color="primary"
            variant="elevated"
            v-on:click="unarchiveFab"
            v-if="select"
            icon
            size="small"
          >
            <v-icon>undo</v-icon>
          </v-btn>
        </v-col>
        <v-col md="2">
          <v-text-field
            v-model="search"
            append-icon="search"
            v-bind:label="t('actions.search')"
            single-line
            hide-details
          />
        </v-col>
        <v-col md="1">
          <v-select
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
          <v-btn
            color="primary"
            variant="elevated"
            v-on:click="openParticipantDialog"
            data-cy="add-participant"
          >
            <v-icon dark left>add</v-icon>
            {{ t("actions.add-person") }}
          </v-btn>
        </v-col>
      </v-row>
    </v-toolbar>
    <v-data-table
      show-select
      v-model="selected"
      :items-per-page-options="rowsPerPageItem"
      :headers="headers"
      :items="visibleMembers"
      :search="search"
      :loading="tableLoading"
      class="elevation-1"
    >
      <template #item="{ item, isSelected, toggleSelect }">
        <tr>
          <td><v-checkbox :model-value="isSelected({ value: item })" @change="toggleSelect({ value: item })" hide-details /></td>
          <td>{{ item.person.firstName }}</td>
          <td>{{ item.person.lastName }}</td>
          <td>{{ item.person.email }}</td>
          <td>{{ item.person.phone }}</td>
          <td class="text-no-wrap">
            <template v-if="item.active">
              <v-tooltip bottom>
                <template #activator="{ props: tooltipProps }">
                  <v-btn
                    icon
                    variant="outlined"
                    size="small"
                    color="primary"
                    v-bind="tooltipProps"
                    v-on:click="editPerson(item.person)"
                    data-cy="edit"
                  >
                    <v-icon size="small">edit</v-icon>
                  </v-btn>
                </template>
                <span>{{ t("actions.edit") }}</span>
              </v-tooltip>
            </template>
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
                    v-on:click="massUnarchive(item)"
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
          <v-spacer />
          <v-btn
            v-on:click="massArchive"
            color="primary"
            variant="elevated"
            :loading="archiveDialog.loading"
            data-cy="confirm-archive"
            >{{ t("actions.confirm") }}</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Add Participant Dialog -->
    <v-dialog v-model="addParticipantDialog.show" max-width="350px">
      <v-card>
        <v-card-title>
          <div>
            <h3 class="headline mb-0">
              {{ t("person.actions.add-participant") }}
            </h3>
          </div>
        </v-card-title>
        <v-card-text>
          <EntitySearch
            multiple
            person
            v-model="addParticipantDialog.newParticipants"
          />
        </v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="cancelNewParticipantDialog"
            color="secondary"
            variant="text"
            data-cy=""
            >{{ t("actions.cancel") }}</v-btn
          >
          <v-spacer />
          <v-btn
            v-on:click="addParticipants"
            :disabled="addParticipantDialog.newParticipants.length === 0"
            color="primary"
            variant="elevated"
            :loading="addParticipantDialog.loading"
            data-cy="confirm-participant"
            >Add Participants</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- New/Edit dialog -->
    <PersonDialog
      @snack="showSnackbar"
      @cancel="cancelPerson"
      @refreshPeople="getMembers"
      :dialog-state="dialogState"
      :all-people="people"
      :person="person"
    />

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

    <!-- Email dialog -->
    <v-dialog v-model="emailDialog.show" max-width="700px">
      <v-card>
        <v-card-title>
          <div>
            <h3 class="headline mb-0">
              {{ t("groups.members.email.compose") }}
            </h3>
          </div>
        </v-card-title>
        <v-card-text>
          <v-select
            v-model="email.recipients"
            :label="t('groups.members.email.to')"
            :items="parsedMembers"
            multiple
            chips
            deletable-chips
            hide-selected
            :no-data-text="t('groups.messages.no-remaining-members')"
          >
          </v-select>
        </v-card-text>
        <v-card-text>
          <v-select
            v-model="email.cc"
            :label="t('groups.members.email.cc')"
            :items="parsedMembers"
            multiple
            chips
            deletable-chips
            hide-selected
            :no-data-text="t('groups.messages.no-remaining-members')"
          >
          </v-select>
        </v-card-text>
        <v-card-text>
          <v-select
            v-model="email.bcc"
            :label="t('groups.members.email.bcc')"
            :items="parsedMembers"
            multiple
            chips
            deletable-chips
            :no-data-text="t('groups.messages.no-remaining-members')"
          >
          </v-select>
        </v-card-text>
        <v-card-text>
          <v-text-field
            :label="t('groups.members.email.subject')"
            v-model="email.subject"
          >
          </v-text-field>
        </v-card-text>
        <v-card-text>
          <v-textarea
            :label="t('groups.members.email.body')"
            v-model="email.body"
          >
          </v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-btn
            v-on:click="toggleEmailDialog"
            color="secondary"
            variant="text"
            data-cy=""
            >{{ t("actions.cancel") }}</v-btn
          >
          <v-spacer></v-spacer>
          <v-btn
            v-on:click="sendEmail"
            :disabled="email.recipients.length == 0"
            color="primary"
            variant="elevated"
            data-cy="confirm-email"
            >{{ t("groups.members.email.send") }}</v-btn
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
import { ref, computed, watch, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import EntitySearch from "../../EntitySearch.vue";
import PersonDialog from "../../PersonDialog.vue";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;
const route = useRoute();

const rowsPerPageItem = [10, 15, 25, { title: "All", value: -1 }];
const tableLoading = ref(false);
const dialogState = ref("");
const search = ref("");
const members = ref<any[]>([]);
const people = ref<any[]>([]);
const person = ref<any>({});
const parsedMembers = ref<any[]>([]);
const selected = ref<any[]>([]);
const select = ref(false);
const archiveSelect = ref(false);
const unarchiveSelect = ref(false);
const viewStatus = ref("viewActive");

const email = ref({
  subject: "",
  body: "",
  recipients: [] as string[],
  cc: [] as string[],
  bcc: [] as string[],
  managerName: "",
  managerEmail: ""
});

const emailDialog = ref({ show: false, loading: false });
const addParticipantDialog = ref({
  show: false,
  newParticipants: [] as any[],
  loading: false
});
const deleteDialog = ref({ show: false, participantId: -1, loading: false });
const archiveDialog = ref({ show: false, memberId: -1, loading: false });
const snackbar = ref({ show: false, text: "" });

const viewOptions = computed(() => [
  { title: t("actions.view-active"), value: "viewActive" },
  { title: t("actions.view-archived"), value: "viewArchived" },
  { title: t("actions.view-all"), value: "viewAll" }
]);

const headers = computed(() => [
  { title: t("person.name.first"), value: "person.firstName", width: "20%" },
  { title: t("person.name.last"), value: "person.lastName", width: "20%" },
  { title: t("person.email"), value: "person.email", width: "22.5%" },
  { title: t("person.phone"), value: "person.phone", width: "22.5%" },
  { title: t("actions.header"), sortable: false }
]);

const visibleMembers = computed(() => {
  let list = members.value;
  if (viewStatus.value === "viewActive") {
    return list.filter((ev: any) => ev.active);
  } else if (viewStatus.value === "viewArchived") {
    return list.filter((ev: any) => !ev.active);
  } else {
    return list;
  }
});

watch(selected, () => {
  if (selected.value.length > 0) {
    select.value = true;
  } else {
    select.value = false;
  }
  email.value.recipients = getEmailRecipients();
});

function parseMembers() {
  members.value.map((e: any) => {
    if (e.person.email) {
      parsedMembers.value.push({
        title: e.person.firstName + " " + e.person.lastName,
        value: e.person.email
      });
    }
  });
}

function openParticipantDialog() {
  addParticipantDialog.value.show = true;
}

function cancelNewParticipantDialog() {
  addParticipantDialog.value.show = false;
}

function editPerson(p: any) {
  dialogState.value = "edit";
  person.value = p;
}

function cancelPerson() {
  dialogState.value = "";
}

function addParticipants() {
  addParticipantDialog.value.loading = true;
  let promises: Promise<any>[] = [];

  for (let p of addParticipantDialog.value.newParticipants) {
    const idx = members.value.findIndex(
      (gr_pe: any) => gr_pe.person.person_id === p.id
    );
    if (idx === -1) {
      promises.push(addParticipant(p.id));
    }
  }

  Promise.all(promises)
    .then(() => {
      showSnackbar(t("groups.messages.members-added"));
      addParticipantDialog.value.loading = false;
      addParticipantDialog.value.show = false;
      addParticipantDialog.value.newParticipants = [];
      getMembers();
    })
    .catch(err => {
      console.log(err);
      addParticipantDialog.value.loading = false;
      showSnackbar(t("groups.messages.error-adding-members"));
    });
}

function getEmailRecipients() {
  return selected.value
    .map((e: any) => e.person.email)
    .filter(function(e: any) {
      return e != null;
    });
}

function sendEmail() {
  http
    .post(`/api/v1/emails/`, email.value)
    .then(() => {
      toggleEmailDialog();
      selected.value = [];
      email.value.subject = "";
      email.value.body = "";
      email.value.cc = [];
      email.value.bcc = [];
      showSnackbar(t("groups.messages.email-sent"));
    })
    .catch(err => {
      showSnackbar(t("groups.messages.error-no-manager-email"));
      console.log(email.value);
      console.log(err);
    });
}

function toggleEmailDialog() {
  if (selected.value.length > 0) {
    email.value.recipients = getEmailRecipients();
    emailDialog.value.show = !emailDialog.value.show;
  } else {
    showSnackbar("No valid email addresses are selected");
  }
}

function addParticipant(id: number) {
  const groupId = route.params.group;
  for (var member of members.value) {
    if (id == member.person.id) {
      return Promise.resolve(true);
    }
  }
  return http.post(`/api/v1/groups/members`, {
    group_id: groupId,
    person_id: id,
    joined: "2018-12-25"
  });
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

function containsActive() {
  let isActive = false;
  selected.value.map((e: any) => {
    if (e.active) isActive = true;
  });
  return isActive;
}

function massArchive() {
  if (archiveSelect.value) {
    selected.value.map((e: any) => {
      archiveDialog.value.memberId = e.id;
      archiveGroup();
    });
    archiveSelect.value = false;
  } else {
    archiveGroup();
  }
}

function activateSelectArchiveDialog() {
  if (containsActive()) {
    if (selected.value.length == 1) {
      activateArchiveDialog(selected.value[0].person.id);
    } else {
      archiveDialog.value.show = true;
    }
    archiveSelect.value = true;
  } else {
    showSnackbar(t("groups.messages.error-active-not-selected"));
  }
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
  archiveSelect.value = false;
}

function archiveGroup() {
  console.log("Archived member");
  archiveDialog.value.loading = true;
  const memberId = archiveDialog.value.memberId;
  const idx = members.value.findIndex((ev: any) => ev.id === memberId);
  http
    .put(`/api/v1/groups/members/deactivate/${memberId}`)
    .then(resp => {
      console.log("ARCHIVE", resp);
      members.value[idx].active = false;
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

function unarchiveFab() {
  if (!containsActive()) {
    unarchiveSelect.value = true;
    massUnarchive(null);
  } else {
    showSnackbar(t("groups.messages.error-archived-not-selected"));
  }
}

function massUnarchive(member: any) {
  if (unarchiveSelect.value) {
    selected.value.map((e: any) => {
      unarchive(e);
    });
    unarchiveSelect.value = false;
  } else {
    unarchive(member);
  }
}

function unarchive(member: any) {
  const idx = members.value.findIndex((ev: any) => ev.id === member.id);
  const memberId = member.id;
  member.id *= -1;
  http
    .put(`/api/v1/groups/members/activate/${memberId}`)
    .then(resp => {
      console.log("UNARCHIVED", resp);
      Object.assign(members.value[idx], resp.data);
      showSnackbar(t("groups.messages.member-unarchived"));
    })
    .catch(err => {
      console.error("UNARCHIVE FALURE", err.response);
      showSnackbar(t("groups.messages.error-unarchiving-member"));
    });
}

function getMembers() {
  tableLoading.value = true;
  const id = route.params.group;
  http.get(`/api/v1/groups/groups/${id}`).then(resp => {
    email.value.managerName =
      resp.data.managerInfo.person.firstName +
      " " +
      resp.data.managerInfo.person.lastName +
      " " +
      resp.data.managerInfo.person.secondLastName;
    email.value.managerEmail = resp.data.managerInfo.person.email;
    members.value = resp.data.memberList;
    people.value = members.value.map((e: any) => e.person);
    parseMembers();
    tableLoading.value = false;
  });
}

onMounted(() => {
  getMembers();
});
</script>

<style>
.v-icon {
  display: inline-flex !important;
}
</style>
