# Architecture Notes

Here are some random notes
about how CC is built.

## UI Top Level

For Vuetify 1.5, the component hierarchy was as follows
(Vuetify components start with `v-`,
CC components capitalized):
* `v-app`
    * `Toolbar`
        * `nav` contains one of these:
            * `ArcoToolbar`
                * `v-toolbar`
                    * `LocaleMenu`
            * `StandardToolbar`
                * `v-toolbar`
                    * `v-toolbar-side-icon`
                    * `AccountMenu`
                    * `LocaleMenu`
                * `NavDrawer`
    * `v-content`
        * `MessageSnackBar`
        * `ErrorReportDialog`
        * `router-view`
    * `Footer`
        * `v-footer`

For Vuetify 2:
* `v-app`
    * `NavDrawer`
        * `v-navigation-drawer app`
    * `AppBar`
        * `v-app-bar app`
    * `v-content`
        `router-view`
