<template>
  <v-container>
    <event-table></event-table>
  </v-container>
</template>

<script>
import EventTable from "../components/events/EventTable";

export default {
  name: "Events",
  components: { "event-table": EventTable }
};
</script>
