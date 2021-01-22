<template>
  <!-- New/Edit dialog -->
  <v-dialog v-model="personDialog.show" persistent max-width="768px">
    <PersonStepper
      v-bind:title="personDialog.title"
      v-bind:initialData="personDialog.person"
      v-bind:addAnotherEnabled="personDialog.addAnotherEnabled"
      v-bind:saveButtonText="personDialog.saveButtonText"
      v-bind:showAccountInfo="personDialog.showAccountInfo"
      v-on:cancel="cancelPerson"
      v-on:saved="savePerson"
      v-on:added-another="addAnother"
      v-on:attachPerson="sendToEvent"
    />
  </v-dialog>
</template>

<script>
import PersonStepper from "@/components/people/PersonStepper";

export default {
  name: "PersonDialog",
  components: { PersonStepper },
  props: {
    dialogState: {
      type: String,
      required: true,
    },
    person: {
      type: Object,
      required: true,
    },
    allPeople: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      personDialog: {
        show: false,
        title: "",
        person: {},
        addAnotherEnabled: false,
      },
    };
  },

  watch: {
    dialogState(val) {
      if (val === "edit") this.editPerson(this.person);
      if (val === "new") this.newPerson();
    },
  },

  methods: {
    sendToEvent(newPersonData) {
      this.$emit("attachPerson", newPersonData);
    },

    activatePersonDialog(person = {}, isEditTitle = false) {
      this.personDialog.title = isEditTitle
        ? this.$t("person.actions.edit")
        : this.$t("person.actions.new");
      this.personDialog.showAccountInfo = !isEditTitle;
      this.personDialog.addAnotherEnabled = !isEditTitle;
      this.personDialog.person = person;
      this.personDialog.show = true;
    },

    editPerson(person) {
      this.activatePersonDialog({ ...person }, true);
    },

    newPerson() {
      this.activatePersonDialog();
    },

    cancelPerson() {
      this.personDialog.show = false;
      this.$emit("cancel");
    },

    savePerson() {
      let idx = this.allPeople.findIndex((p) => p.id === this.person.id);
      if (idx === -1) {
        this.$emit("snack", this.$t("person.messages.person-add"));
      } else {
        this.$emit("snack", this.$t("person.messages.person-edit"));
      }
      this.cancelPerson();
      this.$emit("refreshPeople");
    },

    addAnother() {
      this.$emit("refreshPeople");
      this.activatePersonDialog();
      this.$emit("snack", this.$t("person.messages.person-add"));
    },
  },
};
</script>
