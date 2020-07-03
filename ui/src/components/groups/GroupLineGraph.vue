<template>
  <div>
    <v-btn
      outline
      color="primary"
      v-on:click="$router.push({ path: '/groups/all' })"
    ><v-icon>arrow_back</v-icon>Back</v-btn
    >
      <v-toolbar dense
      height="70"
      >
        <!-- Select time scale -->
        <v-flex md3>
        <v-container fluid>
              <v-select
                @change="changeTimeScale"
                v-model="selectedTimeScale"
                :items="timeScale"
                label="Time Scale"
              ></v-select>
        </v-container>
        </v-flex>
        <!--   Select groups     -->
        <v-flex md2>
          <v-select
            v-model="selectedGroups"
            :items="groups"
            item-text="name"
            label="Selected group(s)"
            multiple
            return-object
            :small-chips="true"
          >
            <template v-slot:prepend-item>
              <v-list-tile
                ripple
                @click="toggle"
              >
                <v-list-tile-content>
                  <v-list-tile-title
                    class="d-flex justify-center"
                  >Select All</v-list-tile-title>
                </v-list-tile-content>
              </v-list-tile>
              <v-divider class="mt-2"></v-divider>
            </template>
            <template v-slot:selection="{ item , index }">
              <v-chip v-if="index === 0">
                {{ fistSelectedGroup.name }}
              </v-chip>
              <span
                v-if="index === 1"
                class="grey--text caption"
              >(+{{ selectedGroups.length - 1 }} others)</span>
            </template>
          </v-select>
        </v-flex>
        <v-spacer />
      </v-toolbar>
    <canvas id="myChart2" width="400" height="180"></canvas>

    <v-toolbar>
      <v-btn class="mx-2" fab small @click="decrease">
        <v-icon dark>navigate_before</v-icon>
      </v-btn>
      <v-chip
        class="ma-2"
        large
        color="blue accent-1"
      >
        {{ currentYear }}
      </v-chip>
      <v-btn class="mx-2" fab small @click="increase">
        <v-icon dark>navigate_next</v-icon>
      </v-btn>
    </v-toolbar>
  </div>
</template>

<script>
  import Chart from 'chart.js';
  import moment from 'moment'

  export default {
    components: {},
    data() {
      return {
        timeScale: ['Weekly', 'Monthly', 'Annually'],
        selectedGroups: [],
        selectedGroupsStore:[],
        groups: [],
        selectedTimeScale:null,
        labels:["January", "Febrwuary", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
        currentYear: null,
        page: null,
        selectedYearMeeting:[],
        currentYearGraph:[],
        data:null
      }
    },

    computed:{
      likesAllFruit () {
        return this.selectedGroups.length === this.groups.length
      },
      getTimeScale(){
        return 1;
      },
      fistSelectedGroup() {
        this.reloadGraph();
        return this.selectedGroups[0];
      }
    },

    mounted() {
      this.getAllGroups();
    },

    methods: {
      calculateGraph(inputGroup){
        let template1 = [0,0,0,0,0,0,0,0,0,0,0,0];
        if (this.selectedTimeScale === "Monthly") {
          for (let i=0; i< inputGroup.meetings.length; i++){
              let meetingYear = this.parseYear(inputGroup.meetings[i].startTime)[0];
              let meetingMonth = this.parseYear(inputGroup.meetings[i].startTime)[1];
              switch(meetingMonth){
                case '01':
                  template1[0] = template1[0] +  inputGroup.meetings[i].attendances.length;
                  break;
                case '02':
                  template1[1] = template1[1] +  inputGroup.meetings[i].attendances.length;
                  break;
                case '03':
                  template1[2] = template1[2] +  inputGroup.meetings[i].attendances.length;
                  break;
                case '04':
                  template1[3] = template1[3] +  inputGroup.meetings[i].attendances.length;
                  break;
                case '05':
                  template1[4] = template1[4] +  inputGroup.meetings[i].attendances.length;
                  break;
                case '06':
                  template1[5] = template1[5] +  inputGroup.meetings[i].attendances.length;
                  break;
                case '07':
                  template1[6] = template1[6] +  inputGroup.meetings[i].attendances.length;
                  break;
                case '08':
                  template1[7] = template1[7] +  inputGroup.meetings[i].attendances.length;
                  break;
                case '09':
                  template1[8] = template1[8] +  inputGroup.meetings[i].attendances.length;
                  break;
                case '10':
                  template1[9] = template1[9] +  inputGroup.meetings[i].attendances.length;
                  break;
                case '11':
                  template1[10] = template1[10] +  inputGroup.meetings[i].attendances.length;
                  break;
                case '12':
                  template1[11] = template1[11] +  inputGroup.meetings[i].attendances.length;
                  break;
              }
          }
          return template1;
        };
      },

      parseYear(startTime){
        let time = startTime.split('-');
        return time;
      },

      decrease() {
        this.currentYear = this.currentYear - 1;
      },
      increase (){
        this.currentYear = Number(this.currentYear) + 1;
      },

      toggle () {
        this.$nextTick(() => {
          if (this.likesAllFruit) {
            this.selectedGroups = []
          } else {
            this.selectedGroups = this.groups.slice()
          }
        })
      },
      getAllGroups(){
        this.selectedTimeScale = "Monthly";
        this.$http
          .get(`/api/v1/groups/groups`)
          .then(resp => {
            for(let group of resp.data){
              this.groups.push(
                group.id = {
                  name: group.name,
                  id: group.id,
                  meetings: group.meetings
                }
              );
            }
          })
          .then(() => this.loadGraph());
      },

      changeTimeScale(){
        if (this.selectedTimeScale === 'Annually'){
          this.labels = ["January", "Febrwuary", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
        }
        else if(this.selectedTimeScale === 'Monthly'){
          this.labels = ["January", "Febrwuary", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
        }
      },

      loadGraph (){
        this.currentYear = moment().format('YYYY');
        if (this.selectedTimeScale === "Monthly" && this.selectedGroups.length == 0){
          let ctx2 = document.getElementById("myChart2");
          let myChart2 = new Chart(ctx2, {
            type: "line",
            data: {
              labels: this.labels,
              datasets: [
                {
                  label: ["No group selected"],
                  backgroundColor: "rgba(225,10,10,0.3)",
                  borderColor: "rgba(225,103,110,1)",
                  borderWidth: 1,
                  pointStrokeColor: "#fff",
                  pointStyle: "crossRot",
                  data: [],
                  cubicInterpolationMode: "monotone",
                  spanGaps: "false",
                  fill: "false"
                },
              ]
            },
            options: {
            }
          });
        }
        else if(this.selectedTimeScale === "Monthly" && this.selectedGroups.length > 0){
          let ctx2 = document.getElementById("myChart2");
          let myChart2 = new Chart(ctx2, {
            type: "line",
            data: {
              labels: this.labels,
              datasets: [
                {
                  label: ["test1"],
                  backgroundColor: "rgba(225,10,10,0.3)",
                  borderColor: "rgba(225,103,110,1)",
                  borderWidth: 1,
                  pointStrokeColor: "#fff",
                  pointStyle: "crossRot",
                  data: this.data,
                  cubicInterpolationMode: "monotone",
                  spanGaps: "false",
                  fill: "false"
                },
              ]
            },
            options: {
            }
          });
        }
      },

      reloadGraph(){
        let numberOfLines = this.selectedGroups.length;
        let graphsNum = this.selectedGroups;
        let ctx2 = document.getElementById("myChart2");
        let myChart2 = new Chart(ctx2, {
          type: "line",
          data: {
            labels: this.labels,
            datasets: []
          },
          options: {
          }
        });

        for (let i =0; i< numberOfLines; i++){
          myChart2.data.datasets.push(
            {
              label: this.selectedGroups[i].name,
              backgroundColor: this.backgroundColorGenerator(),
              borderColor: this.borderColorGenerator(),
              borderWidth: 1,
              pointStrokeColor: "#000",
              pointStyle: "crossRot",
              data: this.calculateGraph(this.selectedGroups[i]),
              cubicInterpolationMode: "monotone",
              spanGaps: "false",
              fill: "false"
            }
          );
        }
        myChart2.update();
      },
      backgroundColorGenerator(){
        let red = Math.floor(Math.random() * 256);
        let green = Math.floor(Math.random() * 256);
        let Blue = Math.floor(Math.random() * 256);
        let Alpha = Math.floor(Math.random() * 256);
        return (`rgba(${ red }, ${ green }, ${ Blue }, ${ Alpha })`);
      },
      borderColorGenerator(){
        let red = Math.floor(Math.random() * 256);
        let green = Math.floor(Math.random() * 256);
        let Blue = Math.floor(Math.random() * 256);
        let Alpha = Math.floor(Math.random() * 256);
        return (`rgba(${ red }, ${ green }, ${ Blue }, ${ Alpha })`);
      },
    }
  }
</script>
<style>
  .small {
    width: 500px;
    height: 500px;
  }
</style>
