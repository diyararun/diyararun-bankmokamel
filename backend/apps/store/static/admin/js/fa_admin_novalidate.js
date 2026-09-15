/**
 * Suppresses the browser's own native HTML5 validation UI ("Please fill
 * out this field", "Please match the requested format", ...) on every
 * admin add/change form.
 *
 * Why this exists: Django's admin panel and all of its own error
 * messages already render in Persian/RTL correctly (LANGUAGE_CODE is
 * set to "fa-ir" project-wide). But a browser's *native* validation
 * tooltip — the little bubble that pops up when you try to submit a
 * form with an empty "required" field — is drawn by the browser itself,
 * in the browser's own UI language, completely independent of the
 * page's language/dir. There is no HTML/CSS/JS way to translate that
 * bubble's text; the only way to stop it from appearing in English (or
 * whatever language the seller's browser happens to be in) is to turn
 * off native validation entirely and let the (already correctly
 * localized) server-side validation in Django handle it, exactly like
 * every other error already shown in this admin.
 *
 * This only removes the *instant, before-submit* browser check — it
 * does not touch Django's own validation, which still runs on submit
 * and still displays its Persian error messages under each field as
 * normal.
 */
(function () {
  "use strict";

  function disableNativeValidation() {
    document.querySelectorAll("#content-main form").forEach(function (form) {
      form.noValidate = true;
    });
  }

  document.addEventListener("DOMContentLoaded", disableNativeValidation);
})();
