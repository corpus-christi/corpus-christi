<template>
  <form ref="form">
    <v-stepper v-model="currentStep" non-linear>
      <v-stepper-header>
        <v-stepper-step editable step="1">
          <span v-bind:class="{ 'text-red': stepOneErrors }">
            {{ t("people.personal-information") }}
          </span>
        </v-stepper-step>

        <v-divider />

        <v-stepper-step editable step="2" v-if="showAccountInfo">
          <span v-bind:class="{ 'text-red': stepTwoErrors }">
            {{ t("people.account-information") }}
          </span>
          <small
            v-if="!isAccountRequired"
            v-bind:class="{ 'text-red': stepTwoErrors }"
            >{{ t("people.optional") }}</small
          >
        </v-stepper-step>

        <v-divider />

        <v-stepper-step editable v-bind:step="showAccountInfo ? 3 : 2">
          <span v-bind:class="{ 'text-red': stepThreeErrors }">
            {{ t("people.additional-information") }}
          </span>
          <small v-bind:class="{ 'text-red': stepThreeErrors }">
            {{ t("people.optional") }}
          </small>
        </v-stepper-step>
      </v-stepper-header>
      <v-stepper-window>
        <v-stepper-window-item value="1">
          <v-text-field
            v-model="person.firstName"
            v-bind:label="t('person.name.first') + ' *'"
            name="firstName"
            :rules="[rules.required, rules.counter]"
            counter
            maxlength="64"
            :readonly="formDisabled"
            data-cy="first-name"
          />

          <v-text-field
            v-model="person.lastName"
            v-bind:label="t('person.name.last') + ' *'"
            name="lastName"
            :rules="[rules.required, rules.counter]"
            counter
            maxlength="64"
            :readonly="formDisabled"
            data-cy="last-name"
          />

          <v-text-field
            v-model="person.secondLastName"
            v-bind:label="t('person.name.second-last')"
            name="secondLastName"
            :rules="[rules.counter]"
            counter
            maxlength="64"
            :readonly="formDisabled"
            data-cy="second-last-name"
          />

          <v-radio-group
            v-model="person.gender"
            :readonly="formDisabled"
            inline
            data-cy="radio-gender"
          >
            <v-radio v-bind:label="t('person.male')" value="M" />
            <v-radio v-bind:label="t('person.female')" value="F" />
          </v-radio-group>

          <v-menu
            :close-on-content-click="false"
            v-model="showBirthdayPicker"
            :nudge-right="40"
            transition="scale-transition"
            offset-y
            min-width="290px"
            :disabled="formDisabled"
            data-cy="show-birthday-picker"
          >
            <template #activator="{ props: menuProps }">
              <v-text-field
                v-bind="menuProps"
                v-model="person.birthday"
                name="birthday"
                v-bind:label="t('person.date.birthday')"
                prepend-icon="event"
                readonly
                data-cy="birthday"
              />
            </template>
            <v-date-picker
              v-bind:locale="authStore.currentLanguageCode"
              :max="getTodayString"
              v-model="person.birthday"
              @update:model-value="showBirthdayPicker = false"
              data-cy="birthday-picker"
            />
          </v-menu>

          <v-text-field
            v-model="person.email"
            v-bind:label="t('person.email')"
            name="email"
            prepend-icon="email"
            data-cy="email"
            :readonly="formDisabled"
          />
          <v-text-field
            v-model="person.phone"
            v-bind:label="t('person.phone')"
            prepend-icon="phone"
            data-cy="phone"
            :readonly="formDisabled"
          />
        </v-stepper-window-item>
        <v-stepper-window-item value="2" v-if="showAccountInfo">
          <!-- User name (for creating new account) -->
          <v-text-field
            v-if="showAccountInfo"
            v-model="person.username"
            v-bind:label="t('person.username') + (isAccountRequired ? ' *' : '')"
            name="username"
            prepend-icon="person"
            data-cy="username"
          />

          <!-- Password (new or update) -->
          <v-text-field
            v-if="showAccountInfo"
            v-model="person.password"
            type="password"
            ref="pwdField"
            v-bind:label="t('person.password') + (isAccountRequired ? ' *' : '')"
            name="password"
            prepend-icon="lock"
            data-cy="password"
          />
          <!-- Password confirmation (new or update) -->
          <v-text-field
            v-if="showAccountInfo"
            v-model="repeatPassword"
            type="password"
            v-bind:label="t('person.repeat-password')"
            name="repeat-password"
            prepend-icon="lock"
            data-cy="confirm-password"
          />
        </v-stepper-window-item>
        <v-stepper-window-item :value="showAccountInfo ? 3 : 2">
          <attribute-form
            :personId="person.id"
            :existingAttributes="person.attributesInfo"
            v-model="attributeFormData"
            ref="attributeForm"
          />
          <v-row justify="center" align="space-around">
            <v-col shrink>
              <v-btn
                size="small"
                color="primary"
                variant="text"
                :disabled="addressWasSaved"
                @click="changeAddressView(true)"
              >
                {{ t("actions.add-address") }}
              </v-btn>
              <v-btn
                class="text-xs-center"
                color="primary"
                variant="text"
                size="small"
                @click="showImageChooser = true"
                :disabled="showImageChooser"
              >
                {{ t("images.actions.add-image") }}
              </v-btn>
            </v-col>
          </v-row>
          <v-col v-show="addressSaved">
            <span>{{ t("places.messages.saved") }}</span>
          </v-col>
          <v-expand-transition>
            <address-form
              v-if="showAddressForm"
              @cancel="changeAddressView"
              @saved="saveAddress"
            >
            </address-form>
          </v-expand-transition>
          <v-expand-transition>
            <image-chooser
              v-if="showImageChooser"
              :imageId="getImageId"
              v-on:saved="chooseImage"
              v-on:deleted="deleteImage"
              v-on:cancel="cancelImageChooser"
              v-on:missing="missingImage"
            />
          </v-expand-transition>
        </v-stepper-window-item>
      </v-stepper-window>
    </v-stepper>
    <v-stepper v-model="currentStep">
      <v-stepper-window>
        <v-stepper-window-item value="1">
          <v-row>
            <v-btn
              color="secondary"
              variant="text"
              v-on:click="cancel"
              :disabled="formDisabled"
              data-cy="cancel"
              >{{ t("actions.cancel") }}</v-btn
            >
            <v-spacer />
            <v-btn color="primary" variant="elevated" v-on:click="next" data-cy="next">
              {{ t("people.next") }}
            </v-btn>
          </v-row>
        </v-stepper-window-item>
        <v-stepper-window-item value="2" v-if="showAccountInfo">
          <v-row>
            <v-btn
              color="secondary"
              variant="text"
              v-on:click="cancel"
              :disabled="formDisabled"
              data-cy="cancel"
              >{{ t("actions.cancel") }}</v-btn
            >
            <v-spacer />
            <v-btn
              color="primary"
              variant="elevated"
              v-on:click="previous"
              data-cy="previous"
              >{{ t("people.previous") }}</v-btn
            >
            <v-btn color="primary" variant="elevated" v-on:click="next" data-cy="next">
              {{ t("people.next") }}
            </v-btn>
          </v-row>
        </v-stepper-window-item>

        <v-stepper-window-item :value="showAccountInfo ? 3 : 2">
          <v-row>
            <v-btn
              color="secondary"
              variant="text"
              v-on:click="cancel"
              :disabled="formDisabled"
              data-cy="cancel"
              >{{ t("actions.cancel") }}</v-btn
            >
            <v-spacer />
            <v-btn
              color="primary"
              variant="outlined"
              v-on:click="addMore"
              v-if="addAnotherEnabled"
              :loading="addMoreIsLoading"
              :disabled="formDisabled"
              data-cy="add-another"
              >{{ t("actions.add-another") }}</v-btn
            >
            <v-btn
              color="primary"
              variant="elevated"
              v-on:click="previous"
              :disabled="showAddressForm"
              data-cy="previous"
              >{{ t("people.previous") }}</v-btn
            >
            <v-btn
              color="primary"
              variant="elevated"
              v-on:click="save"
              :loading="saveIsLoading"
              :disabled="formDisabled"
              data-cy="save"
              >{{ t(saveButtonText) }}</v-btn
            >
          </v-row>
        </v-stepper-window-item>
      </v-stepper-window>
    </v-stepper>
  </form>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useI18n } from "vue-i18n";
import { inject } from "vue";
import type { AxiosInstance } from "axios";
import { useAuthStore } from "@/stores/auth";
import { isEmpty } from "lodash";
import AttributeForm from "./input_fields/AttributeForm.vue";
import AddressForm from "../AddressForm.vue";
import ImageChooser from "../images/ImageChooser.vue";

const { t } = useI18n();
const http = inject<AxiosInstance>("$http")!;
const authStore = useAuthStore();

const props = defineProps<{
  initialData: any;
  addAnotherEnabled?: boolean;
  saveButtonText?: string;
  showAccountInfo?: boolean;
  isAccountRequired?: boolean;
}>();

const emit = defineEmits(["cancel", "saved", "added-another"]);

const attributeForm = ref<any>(null);
const showBirthdayPicker = ref(false);
const showAddressForm = ref(false);
const showImageChooser = ref(false);
const imageSaved = ref(false);
const saveIsLoading = ref(false);
const addMoreIsLoading = ref(false);
const addressWasSaved = ref(false);

const rules = {
  required: (value: string) => !!value || "Required.",
  counter: (value: string) => (value || "").length <= 64 || "Max 64 characters"
};

const person = ref<any>({
  id: 0,
  active: true,
  firstName: "",
  lastName: "",
  secondLastName: "",
  gender: "",
  birthday: "",
  email: "",
  username: "",
  password: "",
  phone: "",
  addressId: 0,
  attributesInfo: []
});

const repeatPassword = ref("");
const attributeFormData = ref<any>({});
const currentStep = ref(1);
const stepOneErrors = ref(false);
const stepTwoErrors = ref(false);
const stepThreeErrors = ref(false);

const personKeys = computed(() => Object.keys(person.value));

const formDisabled = computed(() =>
  saveIsLoading.value ||
  addMoreIsLoading.value ||
  showAddressForm.value ||
  (showImageChooser.value && !imageSaved.value)
);

const hasUsername = computed(() =>
  person.value.username && person.value.username.length ? "required" : ""
);

const getTodayString = computed(() => {
  let today = new Date();
  return `${today.getFullYear()}-${(today.getMonth() + 1).toLocaleString("en-US", {
    minimumIntegerDigits: 2,
    useGrouping: false
  })}-${today.getDate().toLocaleString("en-US", {
    minimumIntegerDigits: 2,
    useGrouping: false
  })}`;
});

const addressSaved = computed(() => addressWasSaved.value);

const getImageId = computed(() => {
  if (person.value.images) {
    return person.value.images.length > 0 ? person.value.images[0].image_id : -1;
  } else {
    return -1;
  }
});

watch(
  () => props.initialData,
  (personProp) => {
    if (isEmpty(personProp)) {
      clear();
    } else {
      person.value = personProp;
      if (person.value.images && person.value.images.length > 0) {
        showImageChooser.value = true;
        imageSaved.value = true;
      } else {
        showImageChooser.value = false;
        imageSaved.value = false;
      }
    }
  }
);

function cancel() {
  clear();
  stepOneErrors.value = false;
  stepTwoErrors.value = false;
  stepThreeErrors.value = false;
  resetForm();
  emit("cancel");
}

function clear() {
  for (let key of personKeys.value) {
    person.value[key] = "";
  }
  if (attributeForm.value) {
    attributeForm.value.clear();
  }
  showAddressForm.value = false;
  showImageChooser.value = false;
  addressWasSaved.value = false;
}

function next() {
  currentStep.value++;
}

function previous() {
  currentStep.value--;
}

function resetForm() {
  saveIsLoading.value = false;
  addMoreIsLoading.value = false;
  currentStep.value = 1;
}

function addMore() {
  addMoreIsLoading.value = true;
  savePerson("added-another");
}

function save() {
  saveIsLoading.value = true;
  savePerson("saved");
}

function saveAddress(resp: any) {
  person.value.addressId = resp.id;
  addressWasSaved.value = true;
  showAddressForm.value = false;
}

function changeAddressView(show: boolean) {
  showAddressForm.value = show;
}

function savePerson(emitMessage: string) {
  let attributes: any[] = [];
  let personId = person.value.id;
  for (let key in attributeFormData.value) {
    attributes.push(attributeFormData.value[key]);
  }
  delete person.value["attributesInfo"];
  delete person.value["accountInfo"];
  delete person.value["id"];
  let data = {
    person: person.value,
    attributesInfo: attributes
  };
  if (personId) {
    updatePerson(data, personId, emitMessage);
  } else {
    addPerson(data, emitMessage);
  }
}

async function updatePerson(data: any, personId: number, emitMessage: string) {
  let newImageId: any = null;
  if (person.value.newImageId) {
    newImageId = person.value.newImageId;
  }
  delete person.value.newImageId;
  delete person.value.images;

  let oldImageId = await getOldImageId(personId);

  console.log(newImageId, oldImageId);
  if (newImageId) {
    if (oldImageId) {
      http
        .put(`/api/v1/people/${personId}/images/${newImageId}?old=${oldImageId}`)
        .then(resp => {
          console.log("PUT IMAGE ON PERSON", resp);
          http
            .put(`/api/v1/people/persons/${personId}`, data)
            .then(response => {
              emit(emitMessage, response.data);
              resetForm();
              saveIsLoading.value = false;
            })
            .catch(err => {
              saveIsLoading.value = false;
              console.error("FALURE", err.response);
            });
        })
        .catch(err => {
          console.error("ERROR PUTTING IMAGE", err.response);
        });
    } else {
      http
        .post(`/api/v1/people/${personId}/images/${newImageId}`)
        .then(resp => {
          console.log("POST IMAGE ON PERSON", resp);
          http
            .put(`/api/v1/people/persons/${personId}`, data)
            .then(response => {
              emit(emitMessage, response.data);
              resetForm();
              saveIsLoading.value = false;
            })
            .catch(err => {
              saveIsLoading.value = false;
              console.error("FALURE", err.response);
            });
        })
        .catch(err => {
          console.error("ERROR POSTING IMAGE", err.response);
        });
    }
  } else {
    if (oldImageId) {
      http
        .delete(`/api/v1/people/${personId}/images/${oldImageId}`)
        .then(resp => {
          console.log("DELETED IMAGE ON PERSON", resp);
          http
            .put(`/api/v1/people/persons/${personId}`, data)
            .then(response => {
              emit(emitMessage, response.data);
              resetForm();
              saveIsLoading.value = false;
            })
            .catch(err => {
              saveIsLoading.value = false;
              console.error("FALURE", err.response);
            });
        })
        .catch(err => {
          console.error("ERROR DELETING IMAGE", err.response);
        });
    } else {
      http
        .put(`/api/v1/people/persons/${personId}`, data)
        .then(response => {
          emit(emitMessage, response.data);
          resetForm();
          saveIsLoading.value = false;
        })
        .catch(err => {
          saveIsLoading.value = false;
          console.error("FALURE", err.response);
        });
    }
  }
}

function addPerson(data: any, emitMessage: string) {
  let imageId = -1;
  if (person.value.newImageId) {
    imageId = person.value.newImageId;
  }
  delete person.value.newImageId;
  http
    .post("/api/v1/people/persons", data)
    .then(async response => {
      if (imageId > -1) {
        await addImage(response.data.id, imageId);
      }
      emit(emitMessage, response.data);
      resetForm();
    })
    .catch(err => {
      resetForm();
      console.error("FAILURE", err.response);
    });
}

function addImage(personId: number, imageId: number) {
  return http
    .post(`/api/v1/people/${personId}/images/${imageId}`)
    .then(resp => {
      console.log("IMAGE ADDED TO PERSON", resp);
    })
    .catch(err => {
      console.error("FAILURE TO ADD IMAGE", err.response);
    });
}

function getOldImageId(id: number) {
  if (!id) {
    return null;
  }
  return http
    .get(`/api/v1/people/persons/${id}?include_images=1`)
    .then(resp => {
      console.log(resp);
      if (resp.data.images && resp.data.images.length > 0) {
        return resp.data.images[0].image_id;
      } else {
        return null;
      }
    })
    .catch(err => {
      console.error("ERROR FETCHING IMAGE", err);
      return null;
    });
}

function chooseImage(id: number) {
  person.value.newImageId = id;
  imageSaved.value = true;
}

function deleteImage() {
  showImageChooser.value = false;
  delete person.value.newImageId;
  person.value.images = [];
  imageSaved.value = false;
}

function cancelImageChooser() {
  showImageChooser.value = false;
}

function missingImage() {
  imageSaved.value = false;
}
</script>
