<template>
  <!-- New/Edit dialog -->
  <v-dialog
    scrollable
    persistent
    v-model="personDialog.show"
    max-width="1000px"
  >
    <v-row no-gutters>
      <v-col>
        <v-card>
          <v-row align="center" justify="center" no-gutters>
            <v-card-title class="headline">
              {{ t(personDialog.title) }}
            </v-card-title>
          </v-row>
        </v-card>
        <PersonForm
          v-bind:initialData="personDialog.person"
          v-bind:addAnotherEnabled="personDialog.addAnotherEnabled"
          v-bind:saveButtonText="personDialog.saveButtonText"
          v-bind:showAccountInfo="personDialog.showAccountInfo"
          v-bind:isAccountRequired="false"
          v-on:cancel="cancelPerson"
          v-on:saved="savePerson"
          v-on:added-another="addAnother"
        />
      </v-col>
    </v-row>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import PersonForm from "./people/PersonForm.vue";

const { t } = useI18n();

const props = defineProps<{
  dialogState: string;
  person: Record<string, any>;
  allPeople: any[];
}>();

const emit = defineEmits(["cancel", "snack", "refreshPeople"]);

const personDialog = ref({
  show: false,
  title: "",
  person: {} as Record<string, any>,
  addAnotherEnabled: false,
  showAccountInfo: false,
  saveButtonText: ""
});

watch(() => props.dialogState, (val) => {
  if (val === "edit") editPerson(props.person);
  if (val === "new") newPerson();
});

function activatePersonDialog(person: Record<string, any> = {}, isEditTitle = false) {
  personDialog.value.title = isEditTitle
    ? "person.actions.edit"
    : "person.actions.new";
  personDialog.value.showAccountInfo = !isEditTitle;
  personDialog.value.addAnotherEnabled = !isEditTitle;
  personDialog.value.person = person;
  personDialog.value.show = true;
}

function editPerson(person: Record<string, any>) {
  activatePersonDialog({ ...person }, true);
}

function newPerson() {
  activatePersonDialog();
}

function cancelPerson() {
  personDialog.value.show = false;
  emit("cancel");
}

function savePerson() {
  let idx = props.allPeople.findIndex(p => p.id === props.person.id);
  if (idx === -1) {
    emit("snack", t("person.messages.person-add"));
  } else {
    emit("snack", t("person.messages.person-edit"));
  }
  cancelPerson();
  emit("refreshPeople");
}

function addAnother() {
  emit("refreshPeople");
  activatePersonDialog();
  emit("snack", t("person.messages.person-add"));
}
</script>
