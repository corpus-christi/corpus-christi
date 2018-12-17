describe('The Home Page', function () {
    it('successfully loads', function () {
        cy.visit('/');
    })
});

describe('Locale Selector', function () {
    it('contains test locales', function () {
        cy.visit('/locale');
        cy.contains('Locales');
    })
});