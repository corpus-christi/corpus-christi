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

Cypress.Commands.add("login", function() {
  cy.visit("/login");
  cy.get("[data-cy=username]").type("Cytest");
  cy.get("[data-cy=password]").type("password");
  cy.get("[data-cy=login]").click();

  // Wait after pressing login to not redirect back to login
  cy.wait(250);
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

// TODO: Eventually bypass logging in before each test
// import store from "../../../src/store"
// const getStore = () => cy.window().its('app.$store');

// Cypress.Commands.add('login', () => {
//   cy.request({
//     method: 'POST',
//     url: '/api/v1/auth/login',
//     body: {
//       username: 'Cytest',
//       password: 'password'
//     }
//   }).then(function() {
//     console.log(getStore());
//     getStore().mutations.logIn({});
//   })
// })
