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
<!--                {{ item.name }}-->
                {{ fistSelectedGroup.name }}
<!--                {{ item }}-->
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

    <!-- Switch buttons for Monthly  (Left and right)  -->
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
        console.log("Selected ", this.selectedGroups);
        return this.selectedGroups.length === this.groups.length
      },
      getTimeScale(){
        console.log("hi", this.selectedTimeScale);
        return 1;
      },
      fistSelectedGroup() {
        console.log("Slelect one group(s)", this.selectedGroups);
        this.reloadGraph();
        return this.selectedGroups[0];
      }
    },

    mounted() {
      //need some change here
      // let ctx2 = document.getElementById("myChart2");
      // let myChart2 = new Chart(ctx2, {
      //   type: "line",
      //   data: {
      //     labels: this.labels,
      //     datasets: [
      //       {
      //         label: ["test1"],
      //         backgroundColor: "rgba(225,10,10,0.3)",
      //         borderColor: "rgba(225,103,110,1)",
      //         borderWidth: 1,
      //         pointStrokeColor: "#fff",
      //         pointStyle: "crossRot",
      //         data: [65, 59, 0, 81, 56, 10, 40, 22, 32, 54, 10, 30],
      //         cubicInterpolationMode: "monotone",
      //         spanGaps: "false",
      //         fill: "false"
      //       },
      //       // {
      //       //   label: ["test2"],
      //       //   backgroundColor: "rgba(75, 192, 192, 1)",
      //       //   borderColor: "rgba(153, 102, 255, 1)",//color of the graph
      //       //   borderWidth: 1,
      //       //   pointStrokeColor: "#000",
      //       //   pointStyle: "crossRot",
      //       //   data: [12, 12, 0, 81, 16, 10, 90, 20, 32, 44, 11, 30],
      //       //   cubicInterpolationMode: "monotone",
      //       //   spanGaps: "false",
      //       //   fill: "false"
      //       // }
      //     ]
      //   },
      //   options: {
      //   }
      // });
      this.getAllGroups();
    },

    methods: {
      //Calculate the current input for selected groups
      calculateGraph(inputGroup){
        let template1 = [0,0,0,0,0,0,0,0,0,0,0,0];
        if (this.selectedTimeScale === "Monthly") { //make it 12 numbers
          // console.log("Start to cal", this.groups);
          for (let i=0; i< inputGroup.meetings.length; i++){
            console.log("one meeting of the group", inputGroup.meetings[i]);
            //Go through the meetings and calculate the attendances
            console.log(inputGroup.meetings[i]);
            // for (let j=0; j< inputGroup.meetings[i].attendances.length; j++){
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
              console.log("Here is the template1", template1);
            // }
            // for (let j=0; j< inputGroup.meetings[i].length; j++){ //all meetings
            //   //parse the meetings attendances
            //   // let meetingYear = this.parseYear(this.groups[i].meetings[j].startTime)[0];
            //   // let meetingMonth = this.parseYear(inputGroup.meetings[i].startTime)[1];
            //   // console.log("current meetingMonth", meetingMonth);
            //   // switch(meetingMonth){
            //   //   case '01':
            //   //     template1[0] = template1[0] +  this.groups[i].meetings[j].attendances.length;
            //   //     break;
            //   //   case '02':
            //   //     template1[1] = template1[1] +  this.groups[i].meetings[j].attendances.length;
            //   //     break;
            //   //   case '03':
            //   //     template1[2] = template1[2] +  this.groups[i].meetings[j].attendances.length;
            //   //     break;
            //   //   case '04':
            //   //     template1[3] = template1[3] +  this.groups[i].meetings[j].attendances.length;
            //   //     break;
            //   //   case '05':
            //   //     template1[4] = template1[4] +  this.groups[i].meetings[j].attendances.length;
            //   //     break;
            //   //   case '06':
            //   //     template1[5] = template1[5] +  this.groups[i].meetings[j].attendances.length;
            //   //     break;
            //   //   case '07':
            //   //     template1[6] = template1[6] +  this.groups[i].meetings[j].attendances.length;
            //   //     break;
            //   //   case '08':
            //   //     template1[7] = template1[7] +  this.groups[i].meetings[j].attendances.length;
            //   //     break;
            //   //   case '09':
            //   //     template1[8] = template1[8] +  this.groups[i].meetings[j].attendances.length;
            //   //     break;
            //   //   case '10':
            //   //     template1[9] = template1[9] +  this.groups[i].meetings[j].attendances.length;
            //   //     break;
            //   //   case '11':
            //   //     template1[10] = template1[10] +  this.groups[i].meetings[j].attendances.length;
            //   //     break;
            //   //   case '12':
            //   //     template1[11] = template1[11] +  this.groups[i].meetings[j].attendances.length;
            //   //     break;
            //   // }
            // }
          }
          // this.data = template1;
          console.log("this data", template1);
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
        console.log(this.currentYear);
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
            //get all the groups's information
            // console.log(resp.data);
            for(let group of resp.data){
              this.groups.push(
                group.id = {
                  name: group.name,
                  id: group.id,
                  meetings: group.meetings
                }
              );
            }
            console.log("Test", this.groups);
          })
          // .then(() => this.calculateGraph())
          .then(() => this.loadGraph());
      },

      changeTimeScale(){
        console.log(this.selectedTimeScale);
        if (this.selectedTimeScale === 'Annually'){
          this.labels = ["January", "Febrwuary", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
        }
        else if(this.selectedTimeScale === 'Monthly'){
          this.labels = ["January", "Febrwuary", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
        }
      },

      loadGraph (){
        console.log("start to load Graph");
        this.currentYear = moment().format('YYYY');
        if (this.selectedTimeScale === "Monthly" && this.selectedGroups.length == 0){//need to load
          console.log("Graph is empty");
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
                // {
                //   label: ["test1"],
                //   backgroundColor: "rgba(225,10,10,0.3)",
                //   borderColor: "rgba(225,103,110,1)",
                //   borderWidth: 1,
                //   pointStrokeColor: "#fff",
                //   pointStyle: "crossRot",
                //   data: this.data,
                //   cubicInterpolationMode: "monotone",
                //   spanGaps: "false",
                //   fill: "false"
                // },
                // {
                //   label: ["test2"],
                //   backgroundColor: "rgba(75, 192, 192, 1)",
                //   borderColor: "rgba(153, 102, 255, 1)",//color of the graph
                //   borderWidth: 1,
                //   pointStrokeColor: "#000",
                //   pointStyle: "crossRot",
                //   data: [12, 12, 0, 81, 16, 10, 90, 20, 32, 44, 11, 30],
                //   cubicInterpolationMode: "monotone",
                //   spanGaps: "false",
                //   fill: "false"
                // }
              ]
            },
            options: {
            }
          });
          console.log(myChart2.data.datasets[0].label);
        }
        else if(this.selectedTimeScale === "Monthly" && this.selectedGroups.length > 0){
          console.log("Graph is not empty");
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
                // {
                //   label: ["test2"],
                //   backgroundColor: "rgba(75, 192, 192, 1)",
                //   borderColor: "rgba(153, 102, 255, 1)",//color of the graph
                //   borderWidth: 1,
                //   pointStrokeColor: "#000",
                //   pointStyle: "crossRot",
                //   data: [12, 12, 0, 81, 16, 10, 90, 20, 32, 44, 11, 30],
                //   cubicInterpolationMode: "monotone",
                //   spanGaps: "false",
                //   fill: "false"
                // }
              ]
            },
            options: {
            }
          });
        }
        // if (this.selectedTimeScale === "weekly"){
        //   let ctx2 = document.getElementById("myChart2");
        //   let myChart2 = new Chart(ctx2, {
        //     type: "line",
        //     data: {
        //       labels: this.labels,
        //       datasets: [
        //         {
        //           label: ["test1"],
        //           backgroundColor: "rgba(225,10,10,0.3)",
        //           borderColor: "rgba(225,103,110,1)",
        //           borderWidth: 1,
        //           pointStrokeColor: "#fff",
        //           pointStyle: "crossRot",
        //           data: [65, 59, 0, 81, 56, 10, 40, 22, 32, 54, 10, 30],
        //           cubicInterpolationMode: "monotone",
        //           spanGaps: "false",
        //           fill: "false"
        //         },
        //         // {
        //         //   label: ["test2"],
        //         //   backgroundColor: "rgba(75, 192, 192, 1)",
        //         //   borderColor: "rgba(153, 102, 255, 1)",//color of the graph
        //         //   borderWidth: 1,
        //         //   pointStrokeColor: "#000",
        //         //   pointStyle: "crossRot",
        //         //   data: [12, 12, 0, 81, 16, 10, 90, 20, 32, 44, 11, 30],
        //         //   cubicInterpolationMode: "monotone",
        //         //   spanGaps: "false",
        //         //   fill: "false"
        //         // }
        //       ]
        //     },
        //     options: {
        //     }
        //   });
        // }
      },

      reloadGraph(){
        console.log("Reload groups: ", this.selectedGroups);
        let numberOfLines = this.selectedGroups.length;
        let graphsNum = this.selectedGroups;
        let ctx2 = document.getElementById("myChart2");
        //calculate the date needed for the the graph
        let myChart2 = new Chart(ctx2, {
          type: "line",
          data: {
            labels: this.labels,
            datasets: []
          },
          options: {
          }
        });
        // myChart2.data.datasets.push(
        //   {
        //     label: ["test2"],
        //     backgroundColor: "rgba(75, 192, 192, 1)",
        //     borderColor: "rgba(153, 102, 160, 1)",//color of the graph
        //     borderWidth: 1,
        //     pointStrokeColor: "#000",
        //     pointStyle: "crossRot",
        //     data: [12, 12, 0, 81, 16, 10, 90, 20, 32, 44, 11, 30], //need to be calculated
        //     cubicInterpolationMode: "monotone",
        //     spanGaps: "false",
        //     fill: "false"
        //   });

        for (let i =0; i< numberOfLines; i++){
          //take a group and calculate the group's grap
          console.log("Draw graph of this group ", this.selectedGroups[i]);
          console.log(myChart2.data.datasets);
          // this.calculateGraph(this.selectedGroups[i]);
          myChart2.data.datasets.push(
            {
              label: this.selectedGroups[i].name,
              backgroundColor: this.backgroundColorGenerator(),//box background color   "rgba(75, 192, 192, 1)"
              borderColor: this.borderColorGenerator(),//color of the graph
              borderWidth: 1,
              pointStrokeColor: "#000",
              pointStyle: "crossRot",
              data: this.calculateGraph(this.selectedGroups[i]), //need to be calculated
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
      graphGenerator(){
        console.log("Show these groups", this.selectedGroups);
        // let graphsNum = this.selectedGroups;
        // let ctx2 = document.getElementById("myChart2");
        // let myChart2 = new Chart(ctx2, {
        //   type: "line",
        //   data: {
        //     labels: this.labels,
        //     datasets: [
        //       {
        //         label: "Hellow",
        //         backgroundColor: "rgba(225,10,10,0.3)",
        //         borderColor: "rgba(225,103,110,1)",
        //         borderWidth: 1,
        //         pointStrokeColor: "#fff",
        //         pointStyle: "crossRot",
        //         data: this.data,
        //         cubicInterpolationMode: "monotone",
        //         spanGaps: "false",
        //         fill: "false"
        //       },
        //       // {
        //       //   label: ["test2"],
        //       //   backgroundColor: "rgba(75, 192, 192, 1)",
        //       //   borderColor: "rgba(153, 102, 255, 1)",//color of the graph
        //       //   borderWidth: 1,
        //       //   pointStrokeColor: "#000",
        //       //   pointStyle: "crossRot",
        //       //   data: [12, 12, 0, 81, 16, 10, 90, 20, 32, 44, 11, 30],
        //       //   cubicInterpolationMode: "monotone",
        //       //   spanGaps: "false",
        //       //   fill: "false"
        //       // }
        //     ]
        //   },
        //   options: {
        //   }
        // });
      }
    }
  }
</script>
<style>
  .small {
    width: 500px;
    height: 500px;
  }
</style>
