<template>
    <v-card
        class="mr-2"
        outlined
        elevation="2"
        v-if="true"
    >
        <v-row
            class="subrow"
            align="center"
        >
            <v-col 
                cols="8"
            >
                <v-select
                    prepend-icon="filter_alt"
                    multiple
                    chips
                    :items="filters"
                >
                </v-select>
            </v-col>
            <v-col
                cols="4"
            >
                <v-btn
                    dark
                >
                    <v-icon>keyboard_arrow_down</v-icon>
                </v-btn>
            </v-col>
        </v-row>
        <v-row
            class="subrow"
        >
            <v-col>
                <v-btn
                    class="ml-4"
                    dark
                    width="70%"
                >
                    Add New Locale
                </v-btn>
            </v-col>
        </v-row>
        <v-row
            class="subrow"
        >
            <v-col>
                <v-card
                    width="50%"
                >
                    0/0
                </v-card>
            </v-col>
        </v-row>
        <v-row
            class="subrow"
        >
            <v-col>
                <v-card
                    width="50%"
                >
                    0/0
                </v-card>
            </v-col>
        </v-row>
        <v-row
            class="subrow"
        >
            <v-col>
                <v-btn
                    dark
                >
                    Cancel
                </v-btn>
            </v-col>
            <v-col>
                <v-btn
                    dark
                >
                    Sumbit
                </v-btn>
            </v-col>
            <v-col>
                <v-btn
                    dark
                >
                    <v-icon>keyboard_arrow_up</v-icon>
                </v-btn>
            </v-col>
        </v-row>
    </v-card>
</template>

<script>
export default {
    name: "ToolBox",
    props: {

    },
    data() {
        return {
            filters: [
                'Yes',
                'No',
                'Maybe',
                'So',
            ],
        };
    },
    methods: {

    },
};
</script>

<style scoped>
    
    .subrow {
        height:24%;
        align-content:center;
    }
</style>