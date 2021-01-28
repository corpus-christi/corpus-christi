# Communication

Information about how the UI and the API interact.

## UI Request

Here's a snippet of code that makes a `patch` request to the API.

```js
updateEntityType(id, newName);
{
  this.entityTypeDialog.loading = true;
  this.$http
    .patch(
      `${this.endpoint}/${id}`,
      { name: newName },
      { noErrorSnackBar: true }
    )
    .then(() => {
      this.entityTypeFormKey = `update_${id}_${newName}`; // refresh entity-type-form
      this.fetchEntityTypes();
      eventBus.$emit("message", {
        content: this.getTranslation("success-update"),
      });
    })
    .catch((err) => {
      console.error("PATCH ERROR", err);
      eventBus.$emit("error", {
        content: this.getTranslation("fail-update"),
      });
    })
    .finally(() => {
      this.entityTypeDialog.loading = false;
      this.hideEntityTypeDialog();
    });
}
```

Think of each of these "dotted blocks"
(i.e., `.patch`, `.then`, `.catch` and `.finally`) as one step in the process.

- `.patch` (of course) sends the initial request to the indicated endpoint
  and passes the ID of the entity to be patched in the URL.
  The second argument is the payload that will be sent with the request,
  in this case to tell the endpoint to update the entity `name` to `newName`.
- `.then` is the regular method run when a `Promise` completes successfully.
  In this case, it’s the promise returned by the `patch` request itself.
  Here, we are re-fetching the list of entities in order to update the UI
  to reflect the changed name.
  (This is actually a bad smell — we shouldn't re-fetch the entire list
  just to update one name — we should just updated that name directly in the UI.
  But don’t worry about that for now.)
- `.catch` is the regular method run when the `Promise` fails.
  Here, we're issuing an error.
- `.finally` is an extension to the standard `Promise` model
  that provides a method that will be invoked
  regardless of how the `Promise` resolved
  (i.e., whether it invoked `.then` or `.catch`).
  Here, we’re just cleaning up by hiding the dialog shown.

The `eventBus` thing that appears throughout might be new to you.
The goal is to be have a consistent way to provide feedback to the user
in a fairly general way. The `eventBus` is an ordinary `Vue` component
that has no visual representation.
It's just being used to have access to Vue's event mechanism.

Consider the `.then` method,
which emits a `message` event via the event bus.
There is a dialog attached to the top-level page layout component
(`ui/src/components/MessageSnackBar.vue`)
that listens for this event.
Upon receipt, it pops open the message "snack bar"
(the little box that slides into view)
with the message content passed as part of the `$emit` call above.

To see where the `MessageSnackBar` is set up,
see `ui/src/layouts/DefaultLayout.vue`.
You’ll also see there the similar `ErrorReportDialog` being created.

That last weird thing here is the `noErrorSnackBar` setting in the `patch` method.
The `$http` object we use is an instance of Axios.
It lets you hook into various parts of the lifecycle of each request.
If you look in `ui/src/plugins/axios.js`,
you can see that we've customized Axios to take action
in the event of a failed request to the API.
By putting this error reporting code here,
we don’t have to litter it all around the app
wherever we make a network request.
This code uses the `ErrorReportDialog` just mentioned.

## API Endpoint

You pass any properties to the server
in the object that’s the second argument to the `patch` method.
Axios will encode it as JSON and send it over the wire.
In the code on, this line pulls in the data:

```js
valid_attributes = i18n_value_schema.load(request.json, (partial = True));
```

The `request` object is populated by the contents of ... well ... the request.
Its `json` method treats the payload of the request as a JSON string
and converts it into an ordinary Python dictionary.

The `...schema` here is an instance of a Marshmallow schema object,
which is used to validate the content of the request
(an attempt to keep the bad guys at bay
and one we use when processing any inbound or outbound data in the API).
Its `load` method takes the ordinary Python dictionary (from `request.json`)
and makes sure it conforms to the proper "shape"
(expressed by the Marshmallow schema class).
If so, processing continues, and if not, error.

The `partial=True` tells Marshmallow that not all the fields
defined in the schema object need to be present.
This setting makes sense for an "update" operation
in which you want to be able to pass only those fields you want to update.
For a "create" operation (in a `POST` request),
that flag should be `False` (the default, so it's usually just omitted)
so that Marshmallow validates _all_ the expected fields.
