<template>
  <div>
    <v-btn
      outline
      color="primary"
      v-on:click="$router.push({ path: '/groups/' + currentGroupId + '/meetings' })"
    ><v-icon>arrow_back</v-icon>Back</v-btn
    >
    <v-tabs color="transparent" slider-color="accent">
      <v-tab
        ripple
        :to="{ name: 'meeting-members' }"
      >
        <v-icon>people_alt</v-icon>&nbsp;{{ $t("groups.members.title") }}
      </v-tab>
      <v-tab
        ripple
        :to="{ name: 'meeting-visitors' }"
      >
        <v-icon>emoji_people</v-icon>&nbsp;{{ $t("groups.members.title-visitor") }}
      </v-tab>
    </v-tabs>
    <hr class="vertical-spacer" />
    <router-view></router-view>


  </div>
</template>

<script>
  // import EntitySearch from "../EntitySearch";
    export default {
      name: "MeetingDetails",
      data(){
        return{
          currentGroupId:null
        }
      },
      methods: {
        fetchMeeting() {//fetch meeting and get all the participants in a meeting
          this.tableLoading = true;
          const meetingId = this.$route.params.meeting;
          this.$http
            .get(`/api/v1/groups/meetings/${meetingId}`)
            .then(resp => {
              this.currentGroupId = resp.data.groupId;
            });
          this.$http
            .get(`/api/v1/groups/meetings/${meetingId}/attendances`)
            .then(resp => {
              this.attendances = resp.data;
            });
        },
      },
      mounted: function(){
        this.fetchMeeting();
      }
    }
</script>

<style scoped>

</style>
