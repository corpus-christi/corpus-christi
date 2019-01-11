<template>
  <v-layout>
    <v-flex xs12 sm12>
      <v-card>
        <v-container fill-height fluid>
            <v-flex xs12 sm12 align-end flexbox>
              <span class="headline">Youth Spaghetti Dinner</span>
            </v-flex>
        </v-container>
        <v-card-text>
          <div>
            <span><b>Location: </b>Coffee Dei</span><br>
            <span><b>Date: </b>1/24/2019</span><br>
            <span><b>Time: </b>6:00 PM - 7:30 PM</span><br><br>  
            <span>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer suscipit id turpis sed hendrerit. 
              In hac habitasse platea dictumst. Aenean ut scelerisque purus. Phasellus a pretium tortor. 
              Nunc et risus eu risus tempus placerat. Pellentesque habitant morbi tristique senectus et netus et 
              malesuada fames ac turpis egestas. Sed pretium imperdiet aliquam. In cursus aliquet mi at gravida. 
              Integer mollis, odio in viverra imperdiet, libero tortor bibendum dui, sit amet congue odio nisl a tortor. 
              Sed suscipit rutrum elit et tincidunt. In egestas sem a sapien pharetra ullamcorper. Maecenas ut sagittis dui. 
              Phasellus vitae tincidunt neque, eu convallis ante. </span><br>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-btn flat color="primary" v-on:click="$router.push({path: '/events/' + $route.params.event + '/participants'})">
            <v-icon>person</v-icon>&nbsp;{{ $t('events.participants') }}
          </v-btn>
          <v-btn flat color="primary" v-on:click="$router.push({path: '/events/' + $route.params.event + '/teams'})">
            <v-icon>group</v-icon>&nbsp;{{ $t('events.teams') }}
          </v-btn>
          <v-btn flat color="primary" v-on:click="$router.push({path: '/events/' + $route.params.event + '/assets'})">
            <v-icon>devices_other</v-icon>&nbsp;{{ $t('events.assets') }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-flex>
  </v-layout>
</template>

<script>
export default {
    name: "EventDetails"
}
</script>