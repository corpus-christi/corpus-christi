<template>
  <v-card>
    <v-card-title>
      <span class="headline">{{ name }}</span>
    </v-card-title>
    <v-card-text>
      <form>
        <v-text-field
          v-model="group.name"
          v-bind:label="$t('groups.name')"
          name="title"
          v-validate="'required'"
          v-bind:error-messages="errors.first('')"
          data-cy="title"
        ></v-text-field>
        <v-textarea
          rows="3"
          v-model="group.description"
          v-bind:label="$t('groups.group-description')"
          name="description"
          data-cy="description"
        ></v-textarea>
        <v-autocomplete
          data-cy="entity-search-field"
          v-model="group.manager"
          v-bind:label="$t('actions.search-people')"
          prepend-icon="search"
          :filter="filter"
          :items="people"
          :loading="autoCompleteLoading"
          return-object
          menu-props="closeOnClick, closeOnContentClick"
        >
          <template
            slot="selection"
            slot-scope="data"
          >{{data.item.firstName}} {{data.item.lastName}} {{data.item.secondLastName}}</template>
          <template
            slot="item"
            slot-scope="data"
          >{{data.item.firstName}} {{data.item.lastName}} {{data.item.secondLastName}}</template>
        </v-autocomplete>
      </form>
    </v-card-text>
    <v-card-actions>
      <v-btn
        color="secondary"
        flat
        v-on:click="cancel"
        :disabled="formDisabled"
        data-cy="form-cancel"
      >{{ $t("actions.cancel") }}</v-btn>
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        outline
        v-on:click="addAnother"
        v-if="editMode === false"
        :loading="addMoreLoading"
        :disabled="formDisabled"
        data-cy="form-addanother"
      >{{ $t("actions.add-another") }}</v-btn>
      <v-btn
        color="primary"
        raised
        v-on:click="save"
        :loading="saveLoading"
        :disabled="formDisabled"
        data-cy="form-save"
      >{{ $t("actions.save") }}</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import { isEmpty } from "lodash";
import { mapGetters } from "vuex";
export default {
  name: "GroupForm",
  watch: {
    initialData(groupProp) {
      if (isEmpty(groupProp)) {
        this.clear();
      } else {
        this.group = groupProp;
        this.group.manager = groupProp.managerInfo;
      }
    }
  },
  mounted() {
    this.autoCompleteLoading = true;
    this.$http
      .get("/api/v1/people/persons")
      .then(resp => {
        this.people = resp.data;
        this.people = this.people.filter(person => {
          return person.accountInfo !== null;
        });
        this.autoCompleteLoading = false;
      })
      .catch(error => {
        console.log(error);
        this.autoCompleteLoading = false;
      });
  },
  computed: {
    groupKeys() {
      return Object.keys(this.group);
    },

    name() {
      return this.editMode
        ? this.$t("groups.edit-group")
        : this.$t("groups.create-group");
    },

    formDisabled() {
      return this.saveLoading || this.addMoreLoading;
    },

    ...mapGetters(["currentLanguageCode"])
  },

  methods: {
    cancel() {
      this.clear();
      this.$emit("cancel");
    },

    clear() {
      for (let key of this.groupKeys) {
        this.group[key] = "";
      }
      delete this.group.address;
      this.$validator.reset();
    },

    filter(item, searchText) {
      searchText = searchText.toLowerCase().trim();
      let name = item.firstName + item.lastName + item.secondaryLastName;
      name = name.toLowerCase();
      return name.includes(searchText);
    },

    save() {
      this.$validator.validateAll().then(() => {
        if (!this.errors.any()) {
          this.group.active = true;
          this.$emit("save", this.group);
        }
      });
    },

    addAnother() {
      // this.$validator.validateAll().then(() => {
      //   if (!this.errors.any()) {
      //     this.event.start = this.getTimestamp(this.startDate, this.startTime);
      //     this.event.end = this.getTimestamp(this.endDate, this.endTime);
      //     this.event.active = true;
      //     this.$emit("add-another", this.event);
      //   }
      // });
    }
  },
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
      group: {},
      people: [],
      autoCompleteLoading: false
    };
  }
};
</script>
