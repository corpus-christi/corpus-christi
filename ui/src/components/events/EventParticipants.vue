<template>
    <div>
        <v-layout row>
      <v-flex>
        <entity-search
        person
        searchEndpoint="http://localhost:3000/people"
        v-on:setSelected="setNewParticipant"/>
        </v-flex>
        <v-flex>
        <v-btn v-on:click="addParticipant" color="primary">Add Participant</v-btn>
        </v-flex>
        </v-layout>
    </div>
</template>

<script>
import EntitySearch from "../EntitySearch";
export default {
    components: { "entity-search": EntitySearch },
    name: "EventParticipants",
    data() {
        return {
            newParticipant: null
        }
    },

    methods: {
        setNewParticipant(id) {
            console.log('setting participant: ' + id)
            this.newParticipant = id
        },
        addParticipant() {
            console.log('Adding')
            this.newParticipant = null
        }
    }
}
</script>