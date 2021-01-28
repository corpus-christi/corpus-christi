<template>
  <v-sheet rounded>
    <v-container>
      <v-row>
        <v-col>
          <p class="headline">{{ title }}</p>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-stepper v-model="currentStep" non-linear>
            <v-stepper-header>
              <v-stepper-step editable step="1">
                <span v-bind:class="{ 'red--text': stepOneErrors }">
                  {{ $t("people.personal-information") }}
                </span>
              </v-stepper-step>

              <v-divider />

              <v-stepper-step editable step="2">
                <span v-bind:class="{ 'red--text': stepTwoErrors }">
                  {{ $t("people.account-information") }}
                </span>
              </v-stepper-step>

              <v-divider />

              <v-stepper-step editable step="3">
                <span v-bind:class="{ 'red--text': stepThreeErrors }">
                  {{ $t("people.additional-information") }}
                </span>
                <small v-bind:class="{ 'red--text': stepThreeErrors }">
                  {{ $t("people.optional") }}
                </small>
              </v-stepper-step>
            </v-stepper-header>

            <v-stepper-items>
              <v-stepper-content step="1">
                <PersonalInfoForm />
                <PersonStepperNavButtons
                  :is-disabled="formDisabled"
                  @cancel="cancel"
                  :show-previous-button="false"
                  @next="next"
                />
              </v-stepper-content>

              <v-stepper-content step="2">
                <AccountInfoForm />
                <PersonStepperNavButtons
                  :is-disabled="formDisabled"
                  @cancel="cancel"
                  @previous="previous"
                  @next="next"
                />
              </v-stepper-content>

              <v-stepper-content step="3">
                <attribute-form
                  :personId="person.id"
                  :existingAttributes="person.attributesInfo"
                  v-model="attributeFormData"
                  ref="attributeForm"
                />

                <v-row>
                  <v-col>
                    <v-btn
                      class="mx-1"
                      :disabled="addressWasSaved"
                      @click="changeAddressView(true)"
                    >
                      <v-icon left>add_location</v-icon>
                      {{ $t("actions.add-address") }}
                    </v-btn>
                    <v-btn
                      class="mx-1"
                      @click="showImageChooser = true"
                      :disabled="showImageChooser"
                    >
                      <v-icon left>add_a_photo</v-icon>
                      {{ $t("images.actions.add-image") }}
                    </v-btn>
                  </v-col>
                </v-row>
                <v-col v-show="addressSaved">
                  <span>{{ $t("places.messages.saved") }}</span>
                </v-col>

                <v-expand-transition>
                  <address-form
                    v-if="showAddressForm"
                    @cancel="changeAddressView"
                    @saved="saveAddress"
                  />
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

                <PersonStepperNavButtons
                  :is-disabled="formDisabled"
                  @cancel="cancel"
                  @previous="previous"
                  :show-next-button="false"
                  :show-save-button="true"
                  @save="save"
                  :is-saving-active="saveIsLoading"
                />
              </v-stepper-content>
            </v-stepper-items>
          </v-stepper>
        </v-col>
      </v-row>
    </v-container>
  </v-sheet>
</template>

<script>
import { mapGetters } from "vuex";
import AttributeForm from "../input_fields/AttributeForm.vue";
import { isEmpty } from "lodash";
import AddressForm from "../../AddressForm.vue";
import ImageChooser from "../../images/ImageChooser";
import PersonalInfoForm from "./PersonalInfoForm";
import AccountInfoForm from "./AccountInfoForm";
import PersonStepperNavButtons from "./PersonStepperNavButtons";

export default {
  name: "PersonStepper",
  components: {
    PersonStepperNavButtons,
    PersonalInfoForm,
    AccountInfoForm,
    "attribute-form": AttributeForm,
    "address-form": AddressForm,
    "image-chooser": ImageChooser,
  },
  props: {
    title: {
      type: String,
      required: true,
    },
    initialData: {
      type: Object,
      required: true,
    },
  },
  data: function () {
    return {
      showAddressForm: false,
      showImageChooser: false,
      imageSaved: false,
      saveIsLoading: false,
      addMoreIsLoading: false,
      addressWasSaved: false,

      rules: {
        required: (value) => !!value || "Required.",
        counter: (value) => value.length <= 64 || "Max 64 characters",
      },

      person: {
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
        attributesInfo: [],
      },

      repeatPassword: "",

      attributeFormData: {},

      currentStep: 1,
      stepOneErrors: false,
      stepTwoErrors: false,
      stepThreeErrors: false,
    };
  },

  computed: {
    // List the keys in a Person record.
    personKeys() {
      return Object.keys(this.person);
    },

    ...mapGetters(["currentLanguageCode"]),

    formDisabled() {
      return (
        this.saveIsLoading ||
        this.addMoreIsLoading ||
        this.showAddressForm ||
        (this.showImageChooser && !this.imageSaved)
      );
    },

    addressSaved() {
      return this.addressWasSaved;
    },

    getImageId() {
      if (this.person.images) {
        return this.person.images.length > 0
          ? this.person.images[0].image_id
          : -1;
      } else {
        return -1;
      }
    },
  },

  watch: {
    // Make sure data stays in sync with any changes to `initialData` from parent.
    initialData(personProp) {
      if (isEmpty(personProp)) {
        this.clear();
      } else {
        this.person = personProp;
        if (this.person.images && this.person.images.length > 0) {
          this.showImageChooser = true;
          this.imageSaved = true;
        } else {
          this.showImageChooser = false;
          this.imageSaved = false;
        }
      }
    },
  },

  methods: {
    // Abandon ship.
    cancel() {
      this.clear();
      this.stepOneErrors = false;
      this.stepTwoErrors = false;
      this.stepThreeErrors = false;
      this.resetForm();
      this.removeLocationFromDatabase();
      this.$emit("cancel");
    },

    // Clear the form and the validators.
    clear() {
      for (let key of this.personKeys) {
        this.person[key] = "";
      }

      this.$refs.attributeForm.clear();
      this.showAddressForm = false;
      this.showImageChooser = false;
      this.addressWasSaved = false;
      this.$validator.reset();
    },

    next() {
      this.setErrors();
      this.currentStep++;
    },

    previous() {
      this.setErrors();
      this.currentStep--;
    },

    redirectToErrors() {
      if (this.stepOneErrors) {
        this.currentStep = 1;
      } else if (this.stepTwoErrors) {
        this.currentStep = 2;
      } else if (this.stepThreeErrors) {
        this.currentStep = 3;
      }
    },

    resetForm() {
      this.saveIsLoading = false;
      this.addMoreIsLoading = false;
      this.currentStep = 1;
      this.addressWasSaved = false;
    },

    addMore() {
      this.addMoreIsLoading = true;
      this.savePerson("added-another");
    },

    save() {
      this.saveIsLoading = true;
      this.savePerson("saved");
    },

    saveAddress(resp) {
      this.person.addressId = resp.id;
      this.addressWasSaved = true;
      this.showAddressForm = false;
    },

    setErrors() {
      this.stepOneErrors =
        this.errors.items.findIndex((element) => {
          return (
            element.field === "firstName" ||
            element.field === "lastName" ||
            element.field === "secondLastName" ||
            element.field === "email" ||
            element.field === "birthday"
          );
        }) !== -1;
      this.stepTwoErrors =
        this.errors.items.findIndex((element) => {
          return (
            element.field === "username" ||
            element.field === "password" ||
            element.field === "confirm-password"
          );
        }) !== -1;
      this.stepThreeErrors =
        this.errors.items.findIndex((element) => {
          return (
            element.field !== "username" &&
            element.field !== "password" &&
            element.field !== "confirm-password" &&
            element.field !== "firstName" &&
            element.field !== "lastName" &&
            element.field !== "secondLastName" &&
            element.field !== "email" &&
            element.field !== "birthday"
          );
        }) !== -1;
    },

    changeAddressView(show) {
      this.showAddressForm = show;
    },

    savePerson(emitMessage) {
      this.$validator.validateAll().then(() => {
        if (!this.errors.any()) {
          let attributes = [];
          let personId = this.person.id;
          for (let key in this.attributeFormData) {
            attributes.push(this.attributeFormData[key]);
          }
          delete this.person["attributesInfo"];
          delete this.person["accountInfo"];
          delete this.person["id"];
          let id = this.person.id;
          let active = this.person.active;
          let firstName = this.person.firstName;
          let lastName = this.person.lastName;
          let secondLastName = this.person.secondLastName;
          let gender = this.person.gender;
          let birthday = this.person.birthday;
          let email = this.person.email;
          let username = this.person.username;
          let password = this.person.password;
          let phone = this.person.phone;
          let addressId = this.person.addressId;
          let personObject = {
            id,
            active,
            firstName,
            lastName,
            secondLastName,
            gender,
            birthday,
            email,
            username,
            password,
            phone,
            addressId,
          };
          let data = {
            person: personObject,
            attributesInfo: attributes,
          };
          if (personId) {
            this.updatePerson(data, personId, emitMessage);
          } else {
            this.addPerson(data, emitMessage);
          }
        } else {
          this.setErrors();
          this.resetForm();
          this.redirectToErrors();
        }
      });
    },

    async updatePerson(data, personId, emitMessage) {
      console.log("What I'm Saying", emitMessage);
      let newImageId = null;
      if (this.person.newImageId) {
        newImageId = this.person.newImageId;
      }
      delete this.person.newImageId;
      delete this.person.images;

      let oldImageId = await this.getOldImageId(personId);

      console.log(newImageId, oldImageId);
      if (newImageId) {
        // a new image was added to the form
        if (oldImageId) {
          // an image was edited (PUT)
          this.$http
            .put(
              `/api/v1/people/${personId}/images/${newImageId}?old=${oldImageId}`
            )
            .then((resp) => {
              console.log("PUT IMAGE ON PERSON", resp);
              this.$http
                .put(`/api/v1/people/persons/${personId}`, data)
                .then((response) => {
                  this.$emit(emitMessage, response.data);
                  this.resetForm();
                  this.saveIsLoading = false;
                })
                .catch((err) => {
                  this.saveIsLoading = false;
                  console.error("FALURE", err.response);
                });
            })
            .catch((err) => {
              console.error("ERROR PUTTING IMAGE", err.response);
            });
        } else {
          // an image was added (POST)
          this.$http
            .post(`/api/v1/people/${personId}/images/${newImageId}`)
            .then((resp) => {
              console.log("POST IMAGE ON PERSON", resp);
              this.$http
                .put(`/api/v1/people/persons/${personId}`, data)
                .then((response) => {
                  this.$emit(emitMessage, response.data);
                  this.resetForm();
                  this.saveIsLoading = false;
                })
                .catch((err) => {
                  this.saveIsLoading = false;
                  console.error("FALURE", err.response);
                });
            })
            .catch((err) => {
              console.error("ERROR POSTING IMAGE", err.response);
            });
        }
      } else {
        if (oldImageId) {
          // an image was removed (DELETE)
          this.$http
            .delete(`/api/v1/people/${personId}/images/${oldImageId}`)
            .then((resp) => {
              console.log("DELETED IMAGE ON PERSON", resp);
              this.$http
                .put(`/api/v1/people/persons/${personId}`, data)
                .then((response) => {
                  this.$emit(emitMessage, response.data);
                  this.resetForm();
                  this.saveIsLoading = false;
                })
                .catch((err) => {
                  this.saveIsLoading = false;
                  console.error("FALURE", err.response);
                });
            })
            .catch((err) => {
              console.error("ERROR DELETING IMAGE", err.response);
            });
        } else {
          console.log("editing", data);
          // an image didn't happen (NOTHING)
          this.$http
            .put(`/api/v1/people/persons/${personId}`, data)
            .then((response) => {
              this.$emit(emitMessage, response.data);
              this.resetForm();
              this.saveIsLoading = false;
            })
            .catch((err) => {
              this.saveIsLoading = false;
              console.error("FALURE", err.response);
            });
        }
      }
    },

    addPerson(data, emitMessage) {
      let imageId = -1;
      if (this.person.newImageId) {
        imageId = this.person.newImageId;
      }
      delete this.person.newImageId;
      this.$http
        .post("/api/v1/people/persons", data)
        .then(async (response) => {
          if (imageId > -1) {
            await this.addImage(response.data.id, imageId);
          }
          // if (this.account.username && this.account.password) {
          //   this.addAccount(response.data.id).then(() => {
          //     this.$emit(emitMessage, response.data);
          //     this.resetForm();
          //   });          }
          else {
            this.$emit(emitMessage, response.data);
            this.resetForm();
          }
          console.log("response");
          console.log(response.data);
          this.$emit("attachPerson", response.data);
        })
        .catch((err) => {
          this.resetForm();
          console.error("FAILURE", err.response);
        });
    },

    // addAccount(personId) {
    //   return this.$http
    //     .post("/api/v1/people/accounts", {
    //       username: this.account.username,
    //       password: this.account.password,
    //       active: true,
    //       personId: personId
    //     })
    //     .then(resp => {
    //       console.log("ADDED", resp);
    //     })
    //     .catch(err => {
    //       this.resetForm();
    //       console.error("FAILURE", err.response);
    //     });
    //},

    addImage(personId, imageId) {
      return this.$http
        .post(`/api/v1/people/${personId}/images/${imageId}`)
        .then((resp) => {
          console.log("IMAGE ADDED TO PERSON", resp);
        })
        .catch((err) => {
          console.error("FAILURE TO ADD IMAGE", err.response);
        });
    },

    getOldImageId(id) {
      if (!id) {
        return null;
      }
      return this.$http
        .get(`/api/v1/people/persons/${id}?include_images=1`)
        .then((resp) => {
          console.log(resp);
          if (resp.data.images && resp.data.images.length > 0) {
            return resp.data.images[0].image_id;
          } else {
            return null;
          }
        })
        .catch((err) => {
          console.error("ERROR FETCHING IMAGE", err);
          return null;
        });
    },

    removeLocationFromDatabase() {
      if (this.person.addressId !== 0 || this.person.addressId !== "") {
        this.$http.post;
      }
    },

    chooseImage(id) {
      this.person.newImageId = id;
      this.imageSaved = true;
    },

    deleteImage() {
      this.showImageChooser = false;
      delete this.person.newImageId;
      this.person.images = [];
      this.imageSaved = false;
    },

    cancelImageChooser() {
      this.showImageChooser = false;
    },

    missingImage() {
      this.imageSaved = false;
    },
  },
};
</script>
