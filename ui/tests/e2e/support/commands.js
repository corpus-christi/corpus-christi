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


Cypress.Commands.add('login', function() {
    cy.visit('/login');
    cy.get('[data-cy=username]').type('Cytest');
    cy.get('[data-cy=password]').type('password');
    cy.get('[data-cy=login]').click();
})



// Cypress.Commands.add('login', () => {
//     cy.request({
//         method: 'POST',
//         url: 'http://localhost:8080/api/v1/auth/login',
//         body: {
//             password: 'Qwerty1234',
//             username: 'lpratico'
//         }
//     })
//     .then((resp) => {
//         window.localStorage.setItem('jwt', Response.body.user.token)
//     })
// })


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

Cypress.Commands.add("login", function() {
  cy.visit("/login");
  cy.get("[data-cy=username]").type("Cytest");
  cy.get("[data-cy=password]").type("password");
  cy.get("[data-cy=login]").click();
});

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
