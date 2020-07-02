<template>
  <!-- component to split a group. emits 'success', 'cancel', 'error' event. -->
  <div>
    <v-card>
      <v-layout align-center justify-center row fill-height>
        <v-card-title class="headline">
          {{ $t("groups.split.title") }}
        </v-card-title>
      </v-layout>
    </v-card>
    <v-stepper non-linear v-model="currentStep">
      <v-stepper-header>
        <v-stepper-step editable step="1">{{
          $t("groups.split.group-information")
        }}</v-stepper-step>
        <v-stepper-step editable step="2">{{
          $t("groups.split.choose-members")
        }}</v-stepper-step>
        <v-stepper-step editable step="3">{{
          $t("groups.split.choose-managers")
        }}</v-stepper-step>
      </v-stepper-header>
      <v-stepper-items>
        <v-stepper-content step="1">
          <v-layout row justify-space-around>
            <v-flex md5>
              <span class="headline">{{
                $t("groups.split.parent-group")
              }}</span>
              <v-text-field
                v-bind:label="$t('groups.name')"
                name="parent-title"
                v-validate="'required'"
                :data-vv-as="$t('groups.name')"
                v-bind:error-messages="errors.first('parent-title')"
                v-model="parentGroup.name"
              />
              <v-textarea
                rows="3"
                v-bind:label="$t('groups.group-description')"
                name="parent-description"
                v-validate="'required'"
                :data-vv-as="$t('groups.description')"
                v-bind:error-messages="errors.collect('parent-description')"
                v-model="parentGroup.description"
              />
              <entity-type-form
                name="parent-grouptype"
                entity-type-name="groupType"
                v-validate="'required'"
                :data-vv-as="$t('groups.group-type')"
                v-bind:error-messages="errors.first('parent-grouptype')"
                v-model="parentGroup.groupType"
              />
            </v-flex>
            <v-divider vertical></v-divider>
            <v-flex md5>
              <span class="headline">{{ $t("groups.split.child-group") }}</span>
              <v-text-field
                v-bind:label="$t('groups.name')"
                name="child-title"
                v-validate="'required'"
                :data-vv-as="$t('groups.name')"
                v-bind:error-messages="errors.first('child-title')"
                v-model="childGroup.name"
              />
              <v-textarea
                rows="3"
                v-bind:label="$t('groups.group-description')"
                name="child-description"
                v-validate="'required'"
                :data-vv-as="$t('groups.description')"
                v-bind:error-messages="errors.collect('child-description')"
                v-model="childGroup.description"
              />
              <entity-type-form
                name="child-grouptype"
                entity-type-name="groupType"
                v-validate="'required'"
                :data-vv-as="$t('groups.group-type')"
                v-bind:error-messages="errors.first('child-grouptype')"
                v-model="childGroup.groupType"
              />
            </v-flex>
          </v-layout>
          <v-layout>
            <v-btn flat @click="cancel">{{ $t("actions.cancel") }}</v-btn>
            <v-spacer></v-spacer>
            <v-btn color="primary" @click="currentStep = 2">{{
              $t("actions.next")
            }}</v-btn>
          </v-layout>
        </v-stepper-content>
        <v-stepper-content step="2">
          <v-container v-if="hasMembers">
            <v-layout
              align-center
              v-for="member in members"
              :key="member.person.id"
            >
              <v-flex md5>
                <span class="text-center-xs"
                  ><v-icon>person</v-icon
                  >{{ getPersonFullName(member.person) }}</span
                >
              </v-flex>
              <v-flex md7>
                <v-radio-group row v-model="member.destination">
                  <v-radio
                    :label="$t('groups.split.parent-group')"
                    value="parent"
                  ></v-radio>
                  <v-radio
                    :label="$t('groups.split.child-group')"
                    value="child"
                  ></v-radio>
                </v-radio-group>
              </v-flex>
            </v-layout>
          </v-container>
          <v-layout justify-center v-else>
            <span class="headline my-5"
              >{{ $t("groups.split.no-members") }}
            </span>
          </v-layout>
          <v-layout>
            <v-btn flat @click="currentStep = 1">{{
              $t("actions.previous")
            }}</v-btn>
            <v-spacer></v-spacer>
            <v-btn color="primary" @click="currentStep = 3">{{
              $t("actions.next")
            }}</v-btn>
          </v-layout>
        </v-stepper-content>
        <v-stepper-content step="3">
          <v-container v-if="hasManagers">
            <v-layout
              align-center
              v-for="manager in managers"
              :key="manager.person.id"
            >
              <v-flex md5>
                <span class="text-center-xs"
                  ><v-icon>account_circle</v-icon
                  >{{ getPersonFullName(manager.person) }}</span
                >
              </v-flex>
              <v-flex md7>
                <v-radio-group row v-model="manager.destination">
                  <v-radio
                    :label="$t('groups.split.parent-group')"
                    value="parent"
                  ></v-radio>
                  <v-radio
                    :label="$t('groups.split.child-group')"
                    value="child"
                  ></v-radio>
                </v-radio-group>
              </v-flex>
            </v-layout>
          </v-container>
          <v-layout justify-center v-else>
            <span class="headline my-5"
              >{{ $t("groups.split.no-managers") }}
            </span>
          </v-layout>
          <v-layout>
            <v-btn flat @click="currentStep = 2">{{
              $t("actions.previous")
            }}</v-btn>
            <v-spacer></v-spacer>
            <v-btn color="primary" :loading="loading" @click="split">{{
              $t("actions.confirm")
            }}</v-btn>
          </v-layout>
        </v-stepper-content>
      </v-stepper-items>
    </v-stepper>
  </div>
</template>
<script>
import EntityTypeForm from "./EntityTypeForm";
import { eventBus } from "../../plugins/event-bus.js";
import { pick, isEmpty } from "lodash";
export default {
  name: "SplitGroupForm",
  components: { EntityTypeForm },
  props: {
    initialData: {
      type: Object,
      required: true
    }
  },
  watch: {
    initialData(parentGroup) {
      if (isEmpty(parentGroup)) {
        this.resetForm();
      } else {
        this.parentGroup = pick(parentGroup, [
          "id",
          "name",
          "description",
          "groupType"
        ]);
        this.members = parentGroup.members
          .filter(m => m.active)
          .map(m => ({ destination: "parent", ...m }));
        this.managers = parentGroup.managers
          .filter(m => m.active)
          .map(m => ({ destination: "parent", ...m }));
      }
    }
  },
  computed: {
    hasMembers() {
      return this.members.length != 0;
    },
    hasManagers() {
      return this.managers.length != 0;
    },
    parentGroupPayload() {
      return {
        name: this.parentGroup.name,
        description: this.parentGroup.description,
        groupTypeId: this.parentGroup.groupType.id
      };
    },
    childGroupPayload() {
      return {
        name: this.childGroup.name,
        description: this.childGroup.description,
        groupTypeId: this.childGroup.groupType.id
      };
    }
  },
  methods: {
    getPersonFullName(person) {
      return `${person.firstName} ${person.lastName}`;
    },
    resetForm() {
      this.currentStep = 1;
      this.parentGroup = {};
      this.childGroup = {};
      this.members = [];
      this.managers = [];
      this.$validator.reset();
    },
    cancel() {
      this.resetForm();
      this.$emit("cancel");
    },
    split() {
      this.loading = true;
      this.$validator.validateAll().then(() => {
        if (this.errors.any()) {
          this.loading = false;
          this.redirectToErrors();
        } else {
          Promise.all([
            // create the child group, and modify the parent group
            this.$http.post("api/v1/groups/groups", this.childGroupPayload),
            this.$http.patch(
              `api/v1/groups/groups/${this.parentGroup.id}`,
              this.parentGroupPayload
            )
          ])
            .then(([{ data: { id: childGroupId } }]) => {
              let promises = [];
              for (let member of this.members) {
                if (member.destination === "child") {
                  promises.push(
                    this.$http.patch(
                      `api/v1/groups/groups/${this.parentGroup.id}/members/${
                        member.person.id
                      }`,
                      { groupId: childGroupId }
                    )
                  );
                }
              }
              for (let manager of this.managers) {
                if (manager.destination === "child") {
                  promises.push(
                    this.$http.patch(
                      `api/v1/groups/groups/${this.parentGroup.id}/managers/${
                        manager.person.id
                      }`,
                      { groupId: childGroupId }
                    )
                  );
                }
              }
              return Promise.all(promises).then(() => {
                eventBus.$emit("message", {
                  content: "groups.split.success"
                });
                this.$emit("success");
              });
            })
            .catch(err => {
              console.log(err);
              eventBus.$emit("error", { content: "groups.split.error" });
            })
            .finally(() => {
              this.loading = false;
            });
        }
      });
    },
    redirectToErrors() {
      this.currentStep = 1;
    }
  },
  data() {
    return {
      currentStep: 1,
      parentGroup: {},
      childGroup: {},
      members: [],
      managers: [],
      loading: false
    };
  }
};
</script>
