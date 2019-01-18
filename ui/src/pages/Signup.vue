<template>
  <v-card>
    <NewAccountForm/>
  </v-card>
</template>

<script>
import NewAccountForm from "./../components/NewAccountForm";

export default {
  name: "Signup",
  components: { NewAccountForm }
};
</script>
