<template>
    <div>
        <v-toolbar>
            <v-toolbar-title>{{ $t("events.title") }}</v-toolbar-title>
            <v-spacer></v-spacer>
            <v-text-field
                v-model="search"
                append-icon="search"
                v-bind:label="$t('actions.search')"
                single-line
                hide-details
            ></v-text-field>
            <v-spacer></v-spacer>

            <v-btn
            color="primary"
            raised
            v-on:click="openParticipantDialog"
            data-cy="add-participant">
                <v-icon dark left>add</v-icon>
                {{ $t("actions.addperson") }}
            </v-btn>
        </v-toolbar>

        <v-dialog v-model="newParticipantDialog.show" max-width="350px">
        <v-card>
            <v-card-text>
                <entity-search
                person
                v-model="newParticipant"
                searchEndpoint="http://localhost:3000/people"/>
            </v-card-text>
            <v-card-actions>
                <v-btn v-on:click="cancelNewParticipantDialog" color="secondary" flat data-cy="">{{ $t("actions.cancel") }}</v-btn>
                <v-spacer></v-spacer>
                <v-btn v-on:click="addParticipant" :disabled="newParticipant == null" color="primary" raised :loading="newParticipantDialog.loading" data-cy="">Add Participant</v-btn>
            </v-card-actions>
        </v-card>
        </v-dialog>
    </div>
</template>

<script>
import EntitySearch from "../EntitySearch";
export default {
    components: { "entity-search": EntitySearch },
    name: "EventParticipants",
    data() {
        return {
            selectedValue: null,
            search: "",
            newParticipant: null,
            newParticipantDialog: {
                show: false,
                eventId: -1,
                loading: false
            },
        }
    },
    

    methods: {
        setNewParticipant(id) {
            console.log('setting participant: ' + id)
            this.newParticipant = id
        },
        addParticipant() {
            this.newParticipant = null
        },

        activateNewParticipantDialog(eventId) {
            this.newParticipantDialog.show = true;
            this.newParticipantDialog.eventId = eventId;
        },
        openParticipantDialog(event) {
            this.activateNewParticipantDialog(event.id);
        },
        cancelNewParticipantDialog() {
            this.newParticipantDialog.show = false;
        },
    }
}
</script>