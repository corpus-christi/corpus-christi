<template>
  <v-row>
    <v-col cols="12" sm="4">
      <v-card>
        <v-card-title>
          <div>
            <h3 class="headline mb-0">
              {{ t("groups.details.class-title") }}: {{ group.name }}
            </h3>
            <div>{{ group.description }}</div>
          </div>
          Group
        </v-card-title>
      </v-card>

      <v-card class="mt-2" v-if="pageLoaded">
        <v-card-title>
          <div>
            <h3 class="headline mb-0">{{ t("groups.details.title") }}</h3>
            <div>{{ t("groups.manager") }}: {{ getManagerName() }}</div>
            <div>
              {{ t("groups.details.member-count") }}:
              {{ group.memberList.length }}
            </div>
          </div>
        </v-card-title>
      </v-card>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";
import { inject } from "vue";
import type { AxiosInstance } from "axios";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;
const route = useRoute();
const router = useRouter();

const group = ref<Record<string, any>>({});
const pageLoaded = ref(false);

function getManagerName() {
  if (group.value.managerInfo) {
    var man = group.value.managerInfo.person;
    return (
      man.firstName +
      " " +
      man.lastName +
      " " +
      (man.secondLastName ? man.secondLastName : "")
    );
  }
  return true;
}

function getGroup() {
  const id = route.params.group;
  return http.get(`/api/v1/groups/groups/${id}`).then(resp => {
    group.value = resp.data;
    console.log(group.value);
  });
}

onMounted(() => {
  pageLoaded.value = false;
  getGroup().then(() => {
    pageLoaded.value = true;
  });
});
</script>
