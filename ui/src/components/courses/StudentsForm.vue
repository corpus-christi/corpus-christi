<template>
  <v-card>
    <v-card-title primary-title>
      <div>
        <h3 class="headline mb-0">
          {{ $t("person.actions.add-participant") }}
        </h3>
      </div>
    </v-card-title>
    <v-card-text>
      <form>
        <entity-search person v-model="newStudent" />
      </form>
      
      <v-expansion-panel v-model="showExpansion" expand>
        <v-expansion-panel-content>
          <div slot="header">{{ $t("courses.create-new-person") }}</div>
          <PersonForm 
            v-bind:initialData="{}"
            v-on:cancel="cancelNewPerson"
            v-on:saved="savedNewPerson"/>
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-card-text>
      
    <v-card-actions>
      <v-btn
        color="secondary"
        flat
        :disabled="saving"
        v-on:click="cancel"
        data-cy="studentform-cancel"
        >{{ $t("actions.cancel") }}
      </v-btn>
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        raised
        :disabled="Object.keys(newStudent).length == 0"
        :loading="saving"
        v-on:click="save"
        data-cy="studentform-save"
        >{{ $t("actions.save") }}</v-btn
      >
    </v-card-actions>
  </v-card>
</template>

<script>
import EntitySearch from "../EntitySearch";
import { mapGetters } from "vuex";
import { isEmpty } from "lodash";
import PersonForm from "../people/PersonForm";

export default {
  name: "StudentsForm",
  components: {
    EntitySearch,
    PersonForm
  },
  data: function() {
    return {
      newStudent: {},
      showExpansion: [false]
    };
  },
  
  computed: {
    title() {
      return this.$t("courses.new-offering");
    },
    
    ...mapGetters(["currentLanguageCode"])
  },
  
  watch: {
    // Make sure data stays in sync with any changes to `initialData` from parent.
    initialData(studentProp) {
      if (isEmpty(studentProp)) {
        this.clear();
      } else {
        this.newStudent = studentProp;
      }
    }
  },
  
  props: {
    initialData: {
      type: Object,
      required: true
    },
    saving: {
      type: Boolean,
      default: false
    }
  },
  
  methods: {
    
    cancelNewPerson() {
      this.showExpansion = [false];
    },
    
    savedNewPerson(person) {
      this.newStudent = person;
      this.showExpansion = [false];
    },
    
    // Abandon ship.
   cancel() {
     this.clear();
     this.$emit("cancel");
   },

   // Clear the forms.
   clear() {
     this.newStudent = {};
     this.$validator.reset();
   },
   
   // Trigger a save event, returning the updated `Course Offering`.
   save() {
     this.$validator.validateAll().then(() => {
       if (!this.errors.any()) {
         this.$emit("save", this.newStudent);
       }
     });
   }
   
  }
}    
</script>
