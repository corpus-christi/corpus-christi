// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add("login", (email, password) => { ... })

// Cypress.Commands.add("login", function() {
//   cy.visit("/login");
//   cy.get("[data-cy=username]").type("Cytest");
//   cy.get("[data-cy=password]").type("password");
//   cy.get("[data-cy=login]").click();
//
//   // Wait after pressing login to not redirect back to login
//   cy.wait(250);
// });
//
// -- This is a child command --
// Cypress.Commands.add("drag", { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add("dismiss", { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This is will overwrite an existing command --
// Cypress.Commands.overwrite("visit", (originalFn, url, options) => { ... })

const getStore = () => cy.window().its("app.$store");
import Account from "../../../src/models/Account.js";

Cypress.Commands.add("login", (username = "Cytest", password = "password") => {
  cy.request({
    method: "POST",
    url: "/api/v1/auth/login",
    body: {
      username,
      password
    }
  })
    .its("body")
    .as("user");
  cy.visit("/");
  // this currently will produce a few errors in the browser console
  getStore().then(store => {
    cy.get("@user").then(user => {
      console.log(store);
      let credential = {
        // FIXME: for some reason the Account used by Cypress is not the very same
        // Account constructor used in the main application, which results in the
        // vuexpersistedstate not being able to synchronize this account object
        account: new Account(
          user.username,
          user.firstName,
          user.lastName,
          ["public"], // can add more roles later, or parameterize this
          user.email
        ),
        jwt: user.jwt
      };
      store.commit("logIn", credential);
    });
  });
});

Cypress.Commands.add("course_page", function() {
  cy.get("[data-cy=toggle-nav-drawer]").click();
  cy.get("[data-cy=courses]").click();
});

Cypress.Commands.add("deploma_page", function() {
  cy.get("[data-cy=toggle-nav-drawer]").click();
  cy.get(".v-list__group__header__append-icon").click();
  cy.get("[data-cy=diplomas-admin]").click();
});

Cypress.Commands.add("transcript_page", function() {
  cy.get("[data-cy=toggle-nav-drawer]").click();
  cy.get(".v-list__group__header__append-icon").click();
  cy.get("[data-cy=transcripts]").click();
});
