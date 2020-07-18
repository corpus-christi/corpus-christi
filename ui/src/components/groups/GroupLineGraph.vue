<template>
  <div>
    <v-btn
      outlined
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
              <v-list-item
                ripple
                @click="toggle"
              >
                <v-list-item-content>
                  <v-list-item-title
                    class="d-flex justify-center"
                  >Select All</v-list-item-title>
                </v-list-item-content>
              </v-list-item>
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
    <body id="graph-container">
      <canvas id="myChart2" width="500" height="180"></canvas>
    </body>
    <v-toolbar>
      <v-spacer />
      <template
      v-if="selectedTimeScale === 'Weekly'"
      >
        <v-flex md3>
          <v-menu
            ref="menu"
            v-model="menu"
            :close-on-content-click="false"
            :return-value.sync="startDate"
            transition="scale-transition"
            offset-y
            min-width="290px"
            open-on-hover
          >
            <template v-slot:activator="{ on, attrs }">
              <v-text-field
                v-model="startDate"
                label="Start"
                prepend-icon="event"
                readonly
                v-bind="attrs"
                v-on="on"
              ></v-text-field>
            </template>
            <v-date-picker v-model="startDate" no-title scrollable range>
              <v-spacer></v-spacer>
              <v-btn text color="primary" @click="menu = false">Cancel</v-btn>
              <v-btn text color="primary" @click="$refs.menu.save(startDate)">OK</v-btn>
            </v-date-picker>
          </v-menu>
        </v-flex>
        <v-flex md3>
          <v-menu
            ref="menu1"
            v-model="menu1"
            :close-on-content-click="false"
            :return-value.sync="endDate"
            transition="scale-transition"
            offset-y
            min-width="290px"
          >
            <template v-slot:activator="{ on, attrs }">
              <v-text-field
                v-model="endDate"
                label="end"
                prepend-icon="event"
                readonly
                v-bind="attrs"
                v-on="on"
              ></v-text-field>
            </template>
            <v-date-picker v-model="endDate" no-title scrollable>
              <v-spacer></v-spacer>
              <v-btn text color="primary" @click="menu1 = false">Cancel</v-btn>
              <v-btn text color="primary" @click="$refs.menu1.save(endDate)">OK</v-btn>
            </v-date-picker>
          </v-menu>
        </v-flex>
      </template>
      <template
        v-if="selectedTimeScale === 'Monthly'"
      >
        <v-flex md3>
          <v-menu
            ref="menu"
            v-model="menu"
            :close-on-content-click="false"
            :return-value.sync="startMonth"
            transition="scale-transition"
            offset-y
            min-width="290px"
            open-on-hover
          >
            <template v-slot:activator="{ on, attrs }">
              <v-text-field
                v-model="startMonth"
                label="Start"
                prepend-icon="event"
                readonly
                v-bind="attrs"
                v-on="on"
              ></v-text-field>
            </template>
            <v-date-picker v-model="startMonth" no-title scrollable type="month">
              <v-spacer></v-spacer>
              <v-btn text color="primary" @click="menu = false">Cancel</v-btn>
              <v-btn text color="primary" @click="$refs.menu.save(startMonth)">OK</v-btn>
            </v-date-picker>
          </v-menu>
        </v-flex>
        <v-flex md3>
          <v-menu
            ref="menu1"
            v-model="menu1"
            :close-on-content-click="false"
            :return-value.sync="endMonth"
            transition="scale-transition"
            offset-y
            min-width="290px"
            open-on-hover
          >
            <template v-slot:activator="{ on, attrs }">
              <v-text-field
                v-model="endMonth"
                label="end"
                prepend-icon="event"
                readonly
                v-bind="attrs"
                v-on="on"
              ></v-text-field>
            </template>
            <v-date-picker v-model="endMonth" no-title scrollable type="month">
              <v-spacer></v-spacer>
              <v-btn text color="primary" @click="menu1 = false">Cancel</v-btn>
              <v-btn text color="primary" @click="$refs.menu1.save(endMonth)">OK</v-btn>
            </v-date-picker>
          </v-menu>
        </v-flex>
      </template>
    </v-toolbar>
  </div>
</template>

<script>
  import Chart from 'chart.js';
  import moment from 'moment'
  import { mapState } from "vuex";
  import 'chartjs-plugin-crosshair';
  import $ from 'jquery';

  export default {
    components: {},
    data() {
      return {
        timeScale: ['Weekly', 'Monthly'],
        selectedGroups: [],
        selectedGroupsStore:[],
        groups: [],
        selectedTimeScale: null,
        labels:["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
        weekLabels:[],
        currentYear: null,
        page: null,
        selectedYearMeeting:[],
        currentYearGraph:[],
        data:null,
        startDate: new Date().toISOString().substr(0, 10),
        endDate: new Date().toISOString().substr(0, 10),
        startMonth: new Date().toISOString().substr(0, 7),
        endMonth: new Date().toISOString().substr(0, 7),
        menu: false,
        menu1: false,
        yearSwitch: false,
        currentViewingGraphData: null,
        currentViewingWeeklyGraphData: null,
        window:{
          graph: null
        },
        graphOption: {
          tooltips: {
            cornerRadius: 0,
            caretSize: 0,
            xPadding: 16,
            yPadding: 10,
            backgroundColor: 'rgba(0, 150, 100, 0.9)',
            titleFontStyle: 'normal',
            titleMarginBottom: 15,
            mode: 'label',
            intersect: false,

          },
          plugins: {
            crosshair: {
              line: {
                color: '#253495',
                width: 6
              },
              sync: {
                enabled: false
              }
            }
          }
        }
      }
    },

    computed:{
      likesAllFruit () {
        return this.selectedGroups.length === this.groups.length
      },
      fistSelectedGroup() {
        this.reloadGraph();
        if (this.selectedTimeScale === 'Weekly'){
          this.calculateWeekGroupData();
        }
        return this.selectedGroups[0];
      },
      ...mapState(["currentAccount"]),
    },
    watch:{
      selectedGroups(newValue){
        if (newValue.length === 0) {
          if (this.selectedTimeScale === 'Monthly') {
            let ctx2 = document.getElementById("myChart2");
            let myChart2 = new Chart(ctx2, {
              type: "line",
              data: {
                labels: this.week,
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
              options: this.graphOption
            });
            myChart2.update();
          }
          if (this.selectedTimeScale === 'Weekly') {
            if (newValue.length === 0) {
              this.resetCanvas();
              let ctx2 = document.getElementById("myChart2");
              let myChart2 = new Chart(ctx2, {
                type: "line",
                data: {
                  labels: this.weekLabels,
                  datasets: [
                    {
                      label: ["No group selected"],
                      backgroundColor: "rgba(225,10,10,0.3)",
                      borderColor: "rgb(225,103,110)",
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
                options: this.graphOption
              });
              myChart2.update();
            }
          }
        }
      },

      startMonth(newValue){
        if (newValue.substr(0, 4) === this.endMonth.substr(0, 4)) {
          if (newValue.substr(5,) - this.endMonth.substr(5,) < 0) { //same year
            this.yearSwitch = true;
            this.updateStartGraph(newValue);
          }
        }
        else if (newValue.substr(0, 4) < this.endMonth.substr(0, 4)){
          //need to reload graph
          this.reloadMultipleStartYearGraph();
          this.yearSwitch = true;
        }
      },

      endMonth(newValue){
        if(newValue.substr(0, 4) === this.startMonth.substr(0, 4)){
          if (newValue.substr(5,) - this.startMonth.substr(5,) < 0){
            this.yearSwitch = true;
          }
          else if(newValue.substr(5,) - this.startMonth.substr(5,) === 0){
            this.currentYear = newValue.substr(0, 4);
            this.yearSwitch = false;
          }
          else if(newValue.substr(5,) - this.startMonth.substr(5,) > 0){
            this.yearSwitch = true;
            this.updateEndGraph(newValue);
          }
        }
        else if(newValue.substr(0, 4) > this.startMonth.substr(0, 4)){ //another year
          this.reloadMultipleEndYearGraph();
          this.yearSwitch = true;
        }
      },

      startDate(newValue){
        if(Number(newValue.substr(0, 4)) === Number(this.endDate.substr(0, 4))){ // same Year --Done
          if (newValue.substr(5,7) <= this.endDate.substr(5,7 )){
            this.updateStartWeeklyGraph(newValue);
          }
        }
        else if (Number(newValue.substr(0, 4)) <= Number(this.endDate.substr(0, 4) - 1)){ //previous coming year
          this.reloadPreComingYear(newValue);
        }
      },

      endDate(newValue){
        if(newValue.substr(0, 4) === this.startDate.substr(0, 4)){
          if (this.startDate.substr(5,7) <= newValue.substr(5,7 )){
            this.updateEndWeeklyGraph(newValue);
          }
        }
        else if(Number(newValue.substr(0, 4))-1 >= Number(this.startDate.substr(0, 4))){
          this.reloadFollowComingYear(newValue);
        }
      }
    },

    mounted() {
      this.getAllGroups();
    },

    methods: {
      updateStartWeeklyGraph(newDate){
        this.resetCanvas();
        let ctx2 = document.getElementById("myChart2");
        let filteredData = this.currentViewingWeeklyGraphData.map(a => Object.assign({}, a));
        let start = moment(newDate).isoWeek();
        let end = moment(this.endDate).isoWeek();
        for(let line of filteredData){
          line.data = line.data.slice(start-1, end);
        }
        let myChart2 = new Chart(ctx2, {
          type: "line",
          data: {
            labels: this.labels.slice(start-1, end),
            datasets: filteredData
          },
          options: this.graphOption
        });
        myChart2.update();
      },

      reloadPreComingYear(newDate){
        //one previous year
        if (Number(newDate.substr(0, 4)) === Number(this.endDate.substr(0, 4) - 1)){
          this.resetCanvas();
          let ctx2 = document.getElementById("myChart2");
          let start = moment(newDate).isoWeek();
          let end = moment(this.endDate).isoWeek();
          let numWeeksFirstYear = moment(newDate).isoWeeksInYear() - start + 1;
          let numberOfLines = this.selectedGroups.length;

          let weekLabels = [];
          for(let i =0; i < numWeeksFirstYear; i++){
            if (i === numWeeksFirstYear -1){
              weekLabels.push( "week" + (Number(start) + Number(i)).toString() + "(" + newDate.slice(0,4) + "End)");
            }
            weekLabels.push( "week" + (Number(start) + Number(i)).toString());
          }
          for(let i = 0; i < end; i++){
            weekLabels.push("week" + (i + 1));
          }
          this.graphOption['scales'] ={
            xAxes:[{
              ticks:{
                display: true,
                autoSkip: true,
                maxTicksLimit: 30
              }
            }]
          };
          let myChart2 = new Chart(ctx2, {
            type: "line",
            data: {
              labels: weekLabels,
              datasets: []
            },
            options: this.graphOption
          });
          // load data into the graph
          if (numberOfLines > 0) {
            for (let i = 0; i < numberOfLines; i++) {
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
          }
        }
        //load more than 2 years in a roll
        else if (Number(newDate.substr(0, 4)) < Number(this.endDate.substr(0, 4) - 1)){
          this.resetCanvas();
          let ctx2 = document.getElementById("myChart2");
          let numberOfLines = this.selectedGroups.length;
          let start = moment(newDate).isoWeek();
          let end = moment(this.endDate).isoWeek();
          let numWeeksFirstYear = moment(newDate).isoWeeksInYear() - start + 1;

          let weekLabels = [];
          for(let i =0; i < numWeeksFirstYear; i++){//weeks of the first select time range year
            if (i === numWeeksFirstYear -1){
              weekLabels.push( "week" + (Number(start) + Number(i)).toString() + "(" + newDate.slice(0,4) + "End)");
            }
            weekLabels.push( newDate.slice(0,4) + " week" + (Number(start) + Number(i)).toString());
          }
          //weeks of the years between start and end year
          for (let i=0; i < Number(this.endDate.substr(0, 4) - newDate.substr(0, 4)) - 1; i++){
            let currentLoopingYear = Number(newDate.substr(0, 4)) + 1 + i;
            let currentYearLoop = moment(currentLoopingYear).isoWeeksInYear();
            for (let j = 0; i < currentYearLoop; i++){
              if( j === currentYearLoop -1){
                weekLabels.push("week" + i + "("+ currentLoopingYear + "End)");
              }
              else{
                weekLabels.push(currentLoopingYear + " week" + i);
              }
            }
          }
          //weeks of the last month
          for(let i = 0; i < end; i++){
            if (i === moment(newDate).isoWeeksInYear()){
              weekLabels.push(newDate.slice(0,4) + "week" + (i + 1) + "(" + newDate.slice(0,4) + "End)");
            }
            else{
              weekLabels.push(newDate.slice(0,4) + " week" + (i + 1));
            }
          }
          // Add the number of the previous year into the labels
          //add the weeks in the last year
          this.graphOption['scales'] ={
            xAxes:[{
              ticks:{
                display: true,
                autoSkip: true,
                maxTicksLimit: 30
              }
            }]
          };
          let myChart2 = new Chart(ctx2, {
            type: "line",
            data: {
              labels: weekLabels,
              datasets: []
            },
            options: this.graphOption
          });

          if (numberOfLines > 0) {
            for (let i = 0; i < numberOfLines; i++) {
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
          }
        }
      },

      reloadFollowComingYear(newDate){
        this.resetCanvas();
        //one following year
        if (Number(newDate.substr(0, 4)) -1 === Number(this.startDate.substr(0, 4))){
          this.resetCanvas();
          let ctx2 = document.getElementById("myChart2");
          let start = moment(this.startDate).isoWeek();
          let end = moment(newDate).isoWeek();
          let numWeeksFirstYear = moment(this.startDate).isoWeeksInYear() - start + 1;
          let numberOfLines = this.selectedGroups.length;

          let weekLabels = [];
          for(let i =0; i < numWeeksFirstYear; i++){
            if (i === numWeeksFirstYear -1){
              weekLabels.push( "week" + (Number(start) + Number(i)).toString() + "(" + newDate.slice(0,4) + "End)");
            }
            weekLabels.push( "week" + (Number(start) + Number(i)).toString());
          }
          for(let i = 0; i < end; i++){
            weekLabels.push("week" + (i + 1));
          }
          this.graphOption['scales'] ={
            xAxes:[{
              ticks:{
                display: true,
                autoSkip: true,
                maxTicksLimit: 30
              }
            }]
          };
          let myChart2 = new Chart(ctx2, {
            type: "line",
            data: {
              labels: weekLabels,
              datasets: []
            },
            options: this.graphOption
          });
          // load data into the graph
          if (numberOfLines > 0) {
            for (let i = 0; i < numberOfLines; i++) {
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
          }
        }
        //load more then 2 years in a roll
        else if (Number(newDate.substr(0, 4)) -1 >= Number(this.startDate.substr(0, 4))){
          this.resetCanvas();
          let ctx2 = document.getElementById("myChart2");
          let numberOfLines = this.selectedGroups.length;
          let start = moment(newDate).isoWeek();
          let end = moment(this.endDate).isoWeek();
          let numWeeksFirstYear = moment(newDate).isoWeeksInYear() - start + 1;

          let weekLabels = [];
          for(let i =0; i < numWeeksFirstYear; i++){//weeks of the first select time range year
            if (i === numWeeksFirstYear -1){
              weekLabels.push( "week" + (Number(start) + Number(i)).toString() + "(" + newDate.slice(0,4) + "End)");
            }
            weekLabels.push( newDate.slice(0,4) + " week" + (Number(start) + Number(i)).toString());
          }
          //weeks of the years between start and end year
          for (let i=0; i < Number(this.endDate.substr(0, 4) - newDate.substr(0, 4)) - 1; i++){
            let currentLoopingYear = Number(newDate.substr(0, 4)) + 1 + i;
            let currentYearLoop = moment(currentLoopingYear).isoWeeksInYear();
            for (let j = 0; i < currentYearLoop; i++){
              if( j === currentYearLoop -1){
                weekLabels.push("week" + i + "("+ currentLoopingYear + "End)");
              }
              else{
                weekLabels.push(currentLoopingYear + " week" + i);
              }
            }
          }
          //weeks of the last month
          for(let i = 0; i < end; i++){
            if (i === moment(newDate).isoWeeksInYear()){
              weekLabels.push(newDate.slice(0,4) + "week" + (i + 1) + "(" + newDate.slice(0,4) + "End)");
            }
            else{
              weekLabels.push(newDate.slice(0,4) + " week" + (i + 1));
            }
          }
          // Add the number of the previous year into the labels
          //add the weeks in the last year
          this.graphOption['scales'] ={
            xAxes:[{
              ticks:{
                display: true,
                autoSkip: true,
                maxTicksLimit: 30
              }
            }]
          };
          let myChart2 = new Chart(ctx2, {
            type: "line",
            data: {
              labels: weekLabels,
              datasets: []
            },
            options: this.graphOption
          });

          if (numberOfLines > 0) {
            for (let i = 0; i < numberOfLines; i++) {
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
          }
        }
      },

      updateEndWeeklyGraph(newDate){
        this.resetCanvas();
        let ctx2 = document.getElementById("myChart2");
        let filteredData = this.currentViewingWeeklyGraphData.map(a => Object.assign({}, a));
        let start = moment(this.startDate).isoWeek();
        let end = moment(newDate).isoWeek();
        for(let line of filteredData){
          line.data = line.data.slice(start-1, end);
        }
        let myChart2 = new Chart(ctx2, {
          type: "line",
          data: {
            labels: this.labels.slice(start-1, end),
            datasets: filteredData
          },
          options: this.graphOption
        });
        myChart2.update();
      },

      updateStartGraph(newMonth){
        let filteredData = this.currentViewingGraphData.map(a => Object.assign({}, a));
        let start = Number(newMonth.substr(5,));
        let end = Number(this.endMonth.substr(5,))
        for(let line of filteredData){
          line.data = line.data.slice(start-1, end);
        }
        let ctx2 = document.getElementById("myChart2");
        let myChart2 = new Chart(ctx2, {
          type: "line",
          data: {
            labels: this.labels.slice(Number(newMonth.substr(5,))-1, Number(this.endMonth.substr(5,))),
            datasets: filteredData
          },
          options: this.graphOption
        });
        myChart2.update();
      },

      updateEndGraph(newMonth){
        let ctx2 = document.getElementById("myChart2");
        let filteredData = this.currentViewingGraphData.map(a => Object.assign({}, a));
        let start = Number(this.startMonth.substr(5,));
        let end = Number(newMonth.substr(5,))
        for(let line of filteredData){
          line.data = line.data.slice(start-1, end);
        }
        let myChart2 = new Chart(ctx2, {
          type: "line",
          data: {
            labels: this.labels.slice(Number(this.startMonth.substr(5,))-1, Number(newMonth.substr(5,))),
            datasets: filteredData
          },
          options: this.graphOption
        });
        myChart2.update();
      },

      calculateGraph(inputGroup){
        let template = [];
        let result = [];
        if (this.selectedTimeScale === "Monthly") {
          for (let i=0; i< inputGroup.meetings.length; i++){
              let meetingYear = this.parseYear(inputGroup.meetings[i].startTime)[0];
              let meetingMonth = this.parseYear(inputGroup.meetings[i].startTime)[1];
              if (!(meetingYear in template)){
                template[meetingYear] = [0,0,0,0,0,0,0,0,0,0,0,0];
              }
              if(meetingYear in template){
                switch(meetingMonth){
                  case '01':
                    template[meetingYear][0] = template[meetingYear][0] + inputGroup.meetings[i].attendances.length;
                    break;
                  case '02':
                    template[meetingYear][1] = template[meetingYear][1] + inputGroup.meetings[i].attendances.length;
                    break;
                  case '03':
                    template[meetingYear][2] = template[meetingYear][2] + inputGroup.meetings[i].attendances.length;
                    break;
                  case '04':
                    template[meetingYear][3] = template[meetingYear][3] + inputGroup.meetings[i].attendances.length;
                    break;
                  case '05':
                    template[meetingYear][4] = template[meetingYear][4] + inputGroup.meetings[i].attendances.length;
                    break;
                  case '06':
                    template[meetingYear][5] = template[meetingYear][5] + inputGroup.meetings[i].attendances.length;
                    break;
                  case '07':
                    template[meetingYear][6] = template[meetingYear][6] + inputGroup.meetings[i].attendances.length;
                    break;
                  case '08':
                    template[meetingYear][7] = template[meetingYear][7] + inputGroup.meetings[i].attendances.length;
                    break;
                  case '09':
                    template[meetingYear][8] = template[meetingYear][8] + inputGroup.meetings[i].attendances.length;
                    break;
                  case '10':
                    template[meetingYear][9] = template[meetingYear][9] + inputGroup.meetings[i].attendances.length;
                    break;
                  case '11':
                    template[meetingYear][10] = template[meetingYear][10] + inputGroup.meetings[i].attendances.length;
                    break;
                  case '12':
                    template[meetingYear][11] = template[meetingYear][11] + inputGroup.meetings[i].attendances.length;
                    break;
                }
              }
          }
          if (template.length === 0){       //there is no date in the group
            if(this.startMonth.substr(0,4) === this.endMonth.substr(0,4)
              && this.startMonth.substr(5,) === this.startMonth.substr(5,)){
              return [0,0,0,0,0,0,0,0,0,0,0,0];
            }
            else if (this.startMonth.substr(0,4) < this.endMonth.substr(0,4)){
              let numZero = 12 - Number(this.startMonth.substr(5,) + 1) + Number(this.endMonth.substr(5,))
                + 12 * (Number(this.endMonth.substr(0, 4) - Number(this.startMonth.substr(0, 4))));
              for (let i=0; i<numZero; i++){
                template.push(0);
              }
              return template
            }
          }
          else if (this.startMonth.substr(0,4) === this.endMonth.substr(0,4)){ //same year
            if (template[this.startMonth.substr(0,4)] === undefined){
              template[this.startMonth.substr(0,4)] = [0,0,0,0,0,0,0,0,0,0,0,0];
            }
            if (Number(this.startMonth.substr(5,)) === Number(this.endMonth.substr(5,))){
              return template[Number(this.startMonth.substr(0,4))];
            }
            else if(Number(this.startMonth.substr(5,)) < Number(this.endMonth.substr(5,))){
              return template[Number(this.startMonth.substr(0,4))].slice(Number(this.startMonth.substr(5,)), Number(this.endMonth.substr(5,)));
            }
          }
          else if(Number(this.startMonth.substr(0,4)) === Number(this.endMonth.substr(0,4)) - 1){ // the previous year(s)/ nextComing year
            if (template[this.startMonth.substr(0,4)] === undefined){
              template[this.startMonth.substr(0,4)] = [0,0,0,0,0,0,0,0,0,0,0,0];
            }
            if (template[this.endMonth.substr(0,4)] === undefined){
              template[this.endMonth.substr(0,4)] = [0,0,0,0,0,0,0,0,0,0,0,0];
            }
            let start = Number(this.startMonth.substr(5,));
            let end = Number(this.endMonth.substr(5,));
            return template[this.startMonth.substr(0, 4)].slice(start-1, 12).concat(template[this.endMonth.substr(0, 4)].slice(0,end));
          }
          else if(Number(this.startMonth.substr(0,4)) < Number(this.endMonth.substr(0,4)) - 1){// the >2 years before the current year
            let emptyData = [0,0,0,0,0,0,0,0,0,0,0,0];
            let start = Number(this.startMonth.substr(0,4));
            let end = Number(this.endMonth.substr(0, 4));
            let curYear = start;
            let numYears = end - start + 1;
            for (let i=0; i < numYears; i++){
              if (!(curYear in template) && i === 0){ //the fist year's data  is empty
                result = result.concat(emptyData.slice(Number(this.startMonth.substr(5,)) - 1, ));
                curYear++;
              }
              else if (!(curYear in template) && i === numYears-1){ //last year is empty
                result = result.concat(emptyData.slice(0, Number(this.endMonth.substr(5,))));
              }
              else{// all the data in the middle
                if (i === 0 ){ //first year of data
                  result = result.concat(template[curYear].slice(Number(this.startMonth.substr(5,)) - 1, ));
                  curYear++;
                }
                else if (i === numYears - 1){ // last year of data
                  result = result.concat(template[curYear].slice(0, Number(this.endMonth.substr(5,))));
                }
                else{ // the year in the middle of the years
                  if (curYear in template){
                    result = result.concat(template[curYear]);
                    curYear++;
                  }
                  else {
                    result = result.concat(emptyData);
                    curYear++;
                  }
                }
              }
            }
          }

          if (Number(this.startMonth.substr(0,4)) < Number(this.endMonth.substr(0,4)) - 1){
            return result;
          }
          else{
            return template;
          }
        }
        else if (this.selectedTimeScale === "Weekly"){
          let template = [];
          let start = moment(this.startDate).isoWeek();
          let end = moment(this.endDate).isoWeek();
          let numYears = Number(this.endDate.substr(0,4)) -Number(this.startDate.substr(0,4)) -1;
          let curYear = Number(this.startDate.substr(0,4)) + 1;
          for (let i=0; i< inputGroup.meetings.length; i++){
            let meetingYear = this.parseYear(inputGroup.meetings[i].startTime)[0];
            let index = moment(inputGroup.meetings[i].startTime).isoWeek();
            //make initial empty data
            if (!(meetingYear in template)){
              for (let j = Number(this.startDate.substr(0,4)); j < Number(this.endDate.substr(0,4)) + 1; j++){
                if (template[j] == undefined){
                  for (let i =0; i< moment(meetingYear).isoWeeksInYear(); i++){
                    if (i == 0 ){
                      template[j] = [];
                    }
                    template[j].push(0);
                  }
                }
              }
            }
            if(meetingYear in template){
              template[meetingYear][index - 1] = template[meetingYear][index - 1] + inputGroup.meetings[i].attendances.length;
            }
          }
          // now we have all the data, we need to filter it into a proper size
          // pre year + the current year
          if (Number(this.startDate.substr(0,4)) === Number(this.endDate.substr(0,4)) - 1){
            return (template[Number(this.startDate.substr(0,4))].slice(start,)).concat(template[Number(this.endDate.substr(0,4))].slice(0,end));
          }
          else { // more than 2 years in a roll
            result = result.concat(template[Number(this.startDate.substr(0,4))].slice(start-1,));
            for(let i=0; i < numYears; i++){
              result = result.concat(template[curYear]);
              curYear++;
            }
            result = result.concat(template[Number(this.endDate.substr(0,4))].slice(0,end));
            return result;
          }
        }
      },

      parseYear(startTime){
        let time = startTime.split('-');
        return time;
      },

      toggle () {
        this.$nextTick(() => {
          if (this.likesAllFruit) {
            this.selectedGroups = [];
            this.loadGraph();
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
        if (this.selectedTimeScale === 'Weekly'){
          this.weekLabels = [];
          this.weekGenerator();
          this.labels = this.weekLabels;
          this.loadWeekGraph();
        }
        else if(this.selectedTimeScale === 'Monthly'){
          this.labels = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
        }
      },
      weekGenerator(){
        let numberOfWeeks = this.currentYear.toString();
        for(let i=0; i<moment(numberOfWeeks).weeksInYear(); i++){
          this.weekLabels.push("Week" + (i+1));
        }
      },
      loadWeekGraph(){
      if (this.selectedTimeScale === "Weekly" && this.selectedGroups.length == 0){
          let ctx2 = document.getElementById("myChart2");
          let myChart2 = new Chart(ctx2, {
            type: "line",
            data: {
              labels: this.labels,
              datasets: [
                {
                  label: ["No week group selected"],
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
            options: this.graphOption
          });
          myChart2.update();
        }
      },

      changePageLoadGraph(){
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
          options: this.graphOption
        });
        myChart2.update();
      },

      loadGraph (){
        this.currentYear = moment().format('YYYY');
        if (this.selectedTimeScale === "Monthly" && this.selectedGroups.length == 0){
          let ctx2 = document.getElementById("myChart2");
          this.window.chart = new Chart(ctx2, {
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
            options: this.graphOption,
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
            options: this.graphOption
          });
          myChart2.update();
        }
      },

      reloadGraph() {
        if (this.selectedTimeScale === 'Monthly') {
         this.resetCanvas();
          let numberOfLines = this.selectedGroups.length;
          let ctx2 = document.getElementById("myChart2");
          if (this.startMonth === this.endMonth){
            this.labels = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
          }
          else{
            this.labels = this.labelStartGenerator(this.startMonth, this.endMonth);
          }

          let myChart2 = new Chart(ctx2, {
            type: "line",
            data: {
              labels: this.labelStartGenerator(this.startMonth, this.endMonth),
              datasets: []
            },
            options: this.graphOption
          });
          if (numberOfLines > 0) {
            for (let i = 0; i < numberOfLines; i++) {
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
            this.currentViewingGraphData = myChart2.data.datasets;
          }
          myChart2.update();
        }
        else if(this.selectedTimeScale === 'Weekly'){
          this.resetCanvas();
          let numberOfLines = this.selectedGroups.length;
          let ctx2 = document.getElementById("myChart2");
          let myChart2 = new Chart(ctx2, {
            type: "line",
            data: {
              labels: this.labels,
              datasets: []
            },
            options: this.graphOption
          });
          if (numberOfLines > 0) {
            for (let i = 0; i < numberOfLines; i++) {
              myChart2.data.datasets.push(
                {
                  label: this.selectedGroups[i].name,
                  backgroundColor: this.backgroundColorGenerator(),
                  borderColor: this.borderColorGenerator(),
                  borderWidth: 1,
                  pointStrokeColor: "#000",
                  pointStyle: "crossRot",
                  data: this.FTgenerator(),
                  cubicInterpolationMode: "monotone",
                  spanGaps: "false",
                  fill: "false"
                }
              );
            }
          }
          myChart2.update();
        }
      },

      resetCanvas(){ //working
        $('#myChart2').remove();
        $('#graph-container').append('<canvas id="myChart2" width="500" height="180"></canvas>');
      },

      reloadMultipleStartYearGraph(){
        if (this.selectedTimeScale === 'Monthly') {
          this.resetCanvas();
          let numberOfLines = this.selectedGroups.length;
          let ctx2 = document.getElementById("myChart2");
          // The labels needed to update to the version of crossing years
          if (Number(this.startMonth.substr(0,4)) < Number(this.endMonth.substr(0,4))){
            //calcualte the lables
            let myChart2 = new Chart(ctx2, {
              type: "line",
              data: {
                labels: this.labelStartGenerator(this.startMonth, this.endMonth),
                datasets: [],
              },
              options: this.graphOption
            });
            if (numberOfLines > 0) {
              for (let i = 0; i < numberOfLines; i++) {
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
              this.currentViewingGraphData = myChart2.data.datasets;
            }
            myChart2.update();
          }
        }
      },

      reloadMultipleEndYearGraph(){
        if (this.selectedTimeScale === 'Monthly') {
          this.resetCanvas();
          let numberOfLines = this.selectedGroups.length;
          let ctx2 = document.getElementById("myChart2");
          let myChart2 = new Chart(ctx2, {
            type: "line",
            data: {
              labels:this.labelStartGenerator(this.startMonth, this.endMonth),
              datasets: []
            },
            options: this.graphOption
          });
          // The labels needed to update to the version of crossing years
          if (numberOfLines > 0) {
            for (let i = 0; i < numberOfLines; i++) {
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
            this.currentViewingGraphData = myChart2.data.datasets;
          }
          myChart2.update();
        }
      },

      labelStartGenerator(startTime, endTime){
        let monthLabels = [];
        let year = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
        if (Number(endTime.substr(0,4)) === Number(startTime.substr(0,4)) && Number(endTime.substr(5,)) > Number(startTime.substr(5,))){ // the same year
          return year.slice(Number(startTime.substr(5,)) -1 , Number(endTime.substr(5,)) -1)
        }
        else if(startTime === endTime){
          return year;
        }
        //number of indexs in in one lable
        else if (Number(endTime.substr(0,4)) - Number(startTime.substr(0,4)) === 1){  //number should be <=24
          if (Number(endTime.substr(5,)) === Number(startTime.substr(5,)) - 1){ //one roll
            for(let i = 0; i < 12; i++ ){
              let index = 0
              if(i + Number(endTime.substr(5,)) >= 12){
                index = i + Number(endTime.substr(5,)) - 12;
                monthLabels.push(year[index]);
              }
              else{
                if (year[Number(endTime.substr(5,)) + i] === "December"){
                  monthLabels.push((year[Number(endTime.substr(5,)) + i] + " " + startTime.substr(0, 4) +"End").toString());
                }
                else{
                  monthLabels.push(year[Number(endTime.substr(5,)) + i])
                }
              }
            }
          }
          else if(endTime.substr(5,) > startTime.substr(5,) - 1){ //12+
            let index = 0
            for(let i = 0; i < 13 + Number(endTime.substr(5,) - startTime.substr(5,)); i++){
              if(i + Number(startTime.substr(5,)) > 12){ //second half year
                index = i + Number(startTime.substr(5,)) - 13;
                monthLabels.push(year[index]);
              }
              else{   // first half year
                if (year[Number(startTime.substr(5,)) + i -1] === "December"){
                  monthLabels.push((year[Number(startTime.substr(5,)) + i - 1] + " " + startTime.substr(0,4) +"End").toString());
                }
                else{
                  monthLabels.push(year[Number(startTime.substr(5,)) + i - 1])
                }
              }
            }
          }
          else if(endTime.substr(5,) < startTime.substr(5,) - 1){ //12-
            let index = 0
            for(let i = 0; i < 13 - Number(startTime.substr(5,)) + Number(endTime.substr(5,)); i++){
              if(i + Number(startTime.substr(5,)) > 12){ //second half year
                index = i + Number(startTime.substr(5,)) - 13;
                monthLabels.push(year[index]);
              }
              else{   // first half year
                if (year[Number(startTime.substr(5,)) + i -1] === "December"){
                  monthLabels.push((year[Number(startTime.substr(5,)) + i - 1] + " " + startTime.substr(0, 4) +"End").toString());
                }
                else{
                  monthLabels.push(year[Number(startTime.substr(5,)) + i - 1])
                }
              }
            }
          }
          return monthLabels;
        } //one year gap
        else if (Number(endTime.substr(0,4)) - Number(startTime.substr(0,4)) > 1){  //>2 years gap
          let numMonth = 12 * (Number(endTime.substr(0,4) - Number(startTime.substr(0,4))) - 1)
          + Number(endTime.substr(5,)) + (13 - Number(startTime.substr(5,)))
          let loopYear = Number(startTime.substr(0, 4));
          for (let i =0; i < numMonth; i++){
            if (year[Number(startTime.substr(5,)) + i - 1] === "December"){
              monthLabels.push(year[Number(startTime.substr(5,)) + i -1] + loopYear + "End");
              loopYear++;
            }
            else{
              if (loopYear != Number(startTime.substr(0, 4)) && loopYear != Number(endTime.substr(0, 4))){
                if (year[i - (12 -Number(startTime.substr(5,)) + (loopYear - Number(startTime.substr(0,4)) -1 ) * 12) - 1] === "December"){
                  monthLabels.push(year[i - (12 -Number(startTime.substr(5,)) + (loopYear - Number(startTime.substr(0,4)) -1 ) * 12) - 1] + loopYear + "End ");
                  loopYear++;
                }
                else{
                  monthLabels.push(year[i - (12 -Number(startTime.substr(5,)) + (loopYear - Number(startTime.substr(0,4)) -1 ) * 12) - 1]);
                }
              }
              else if(loopYear === Number(endTime.substr(0, 4))){
                monthLabels.push(year[i - (12 -Number(startTime.substr(5,)) + (loopYear - Number(startTime.substr(0,4)) -1 ) * 12) -1]);
              }
              else{
                monthLabels.push(year[Number(startTime.substr(5,)) + i - 1]);
              }
            }
          }
          return monthLabels;
        }
      },

      labelEndGenerator(startTime, endTime){
        let monthLabels = [];
        let year = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
        if (Number(endTime.substr(0,4)) - Number(startTime.substr(0,4)) === 1){  //Month number should be <=24
          if (Number(endTime.substr(5,)) === Number(startTime.substr(5,)) - 1){ //one roll year
            for(let i = 0; i < 12; i++ ){
              let index = 0
              if(i + Number(endTime.substr(5,)) >= 12){
                index = i + Number(endTime.substr(5,)) - 12;
                monthLabels.push(year[index]);
              }
              else{
                if (year[Number(endTime.substr(5,)) + i] === "December"){
                  monthLabels.push((year[Number(endTime.substr(5,)) + i] + " " + startTime.substr(0, 4) +"End").toString());
                }
                else{
                  monthLabels.push(year[Number(endTime.substr(5,)) + i])
                }
              }
            }
          }
          else if(endTime.substr(5,) > startTime.substr(5,) - 1){ //12+
            let index = 0
            for(let i = 0; i < 13 + Number(endTime.substr(5,) - startTime.substr(5,)); i++){
              if(i + Number(startTime.substr(5,)) > 12){ //second half year
                index = i + Number(startTime.substr(5,)) - 13;
                monthLabels.push(year[index]);
              }
              else{   // first half year
                if (year[Number(startTime.substr(5,)) + i -1] === "December"){
                  monthLabels.push((year[Number(startTime.substr(5,)) + i - 1] + " " + startTime.substr(5,) +"End").toString());
                }
                else{
                  monthLabels.push(year[Number(startTime.substr(5,)) + i - 1])
                }
              }
            }
          }
          else if(endTime.substr(5,) < startTime.substr(5,) - 1){ //12-
            let index = 0
            for(let i = 0; i < 13 - Number(startTime.substr(5,)) + Number(endTime.substr(5,)); i++){
              if(i + Number(startTime.substr(5,)) > 12){ //second half year
                index = i + Number(startTime.substr(5,)) - 13;
                monthLabels.push(year[index]);
              }
              else{   // first half year
                if (year[Number(startTime.substr(5,)) + i -1] === "December"){
                  monthLabels.push((year[Number(startTime.substr(5,)) + i - 1] + " " + startTime.substr(0, 4) +"End").toString());
                }
                else{
                  monthLabels.push(year[Number(startTime.substr(5,)) + i - 1])
                }
              }
            }
          }
          return monthLabels;
        }
        //more than one year gap
        else if (Number(endTime.substr(0,4)) - Number(startTime.substr(0,4)) > 1){
          let numMonth = 12 * (Number(endTime.substr(0,4) - Number(startTime.substr(0,4))) - 1)
            + Number(endTime.substr(5,)) + (13 - Number(startTime.substr(5,)))
          let loopYear = Number(startTime.substr(0, 4));
          for (let i =0; i < numMonth; i++){
            if (year[Number(startTime.substr(5,)) + i - 1] === "December"){
              monthLabels.push(year[Number(startTime.substr(5,)) + i -1] + loopYear + "End");
              loopYear++;
            }
            else{
              if (loopYear != Number(startTime.substr(0, 4)) && loopYear != Number(endTime.substr(0, 4))){
                if (year[i - (12 -Number(startTime.substr(5,)) + (loopYear - Number(startTime.substr(0,4)) -1 ) * 12) - 1] === "December"){
                  monthLabels.push(year[i - (12 -Number(startTime.substr(5,)) + (loopYear - Number(startTime.substr(0,4)) -1 ) * 12) - 1] + loopYear + "End ");
                  loopYear++;
                }
                else{
                  monthLabels.push(year[i - (12 -Number(startTime.substr(5,)) + (loopYear - Number(startTime.substr(0,4)) -1 ) * 12) - 1]);
                }
              }
              else if(loopYear === Number(endTime.substr(0, 4))){ //last section
                monthLabels.push(year[i - (12 -Number(startTime.substr(5,)) + (loopYear - Number(startTime.substr(0,4)) -1 ) * 12) -1]);
              }
              else{
                monthLabels.push(year[Number(startTime.substr(5,)) + i - 1]);
              }
            }
          }
          return monthLabels;
        }
      },

      calculateWeekGraph(group){
        let initialData = this.FTgenerator();
        for (let i = 0; i < group.meetings.length; i++){
          initialData[(moment(group.meetings[i].startTime).isoWeek())-1] = initialData[(moment(group.meetings[i].startTime).isoWeek()) -1 ] + group.meetings[i].attendances.length;
        }
        return initialData;
      },

      calculateWeekGroupData(){
        let numberOfLines = this.selectedGroups.length;
        let ctx2 = document.getElementById("myChart2");
        let myChart2 = new Chart(ctx2, {
          type: "line",
          data: {
            labels: this.labels,
            datasets: []
          },
          options: this.graphOption
        });
        if (numberOfLines > 0) {
          for(let group of this.selectedGroups){
            myChart2.data.datasets.push(
              {
                label: group.name,
                backgroundColor: this.backgroundColorGenerator(),
                borderColor: this.borderColorGenerator(),
                borderWidth: 1,
                pointStrokeColor: "#000",
                pointStyle: "crossRot",
                data: this.calculateWeekGraph(group),
                cubicInterpolationMode: "monotone",
                spanGaps: "false",
                fill: "false"
              }
            );
          }
          this.currentViewingWeeklyGraphData = myChart2.data.datasets;
        }
        myChart2.update();
      },

      FTgenerator(){
        for (var a=[],i=0;i<52;++i) a[i]=0;
        function shuffle(array) {
          let tmp, current, top = array.length;
          if(top) while(--top) {
            current = Math.floor(Math.random() * (top + 1));
            tmp = array[current];
            array[current] = array[top];
            array[top] = tmp;
          }
          return array;
        }
        return a = shuffle(a);
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
