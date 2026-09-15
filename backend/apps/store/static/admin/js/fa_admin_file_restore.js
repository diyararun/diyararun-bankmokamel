/**
 * Restores a seller's already-chosen file(s) in <input type="file">
 * fields after the admin redisplays the same add/change form because
 * of a validation error elsewhere on the page.
 *
 * The problem: a browser always resets a file input to empty on any
 * full-page reload/redisplay — including the reload Django admin does
 * when a form fails validation. So today, if a seller fills in a
 * product's images (main form, or several rows of the "تصویرهای
 * محصول" inline) and one *other*, unrelated field has an error, they
 * come back to find every "choose file" input empty again — the error
 * has to be fixed *and* every image re-selected from scratch. The more
 * images they'd picked, the worse this is.
 *
 * The fix: on submit, remember each file input's chosen File object(s)
 * in IndexedDB (the one browser storage API that can actually hold File
 * objects, unlike localStorage), keyed by this page's URL + the input's
 * form field name. On the next page load, if the page is in fact an
 * error-redisplay (a Django "errorlist"/"errornote" is present), put
 * those same File object(s) back into the matching input via the
 * DataTransfer API. A fresh, error-free page (a brand new "add" visit,
 * or after a successful save) never restores anything, so there is no
 * risk of old files leaking into an unrelated later visit.
 *
 * Deliberately does NOT intercept the form submit into an AJAX request
 * — the normal Django admin POST + full page reload happens completely
 * unmodified; this script only "replays" the selection afterwards, so
 * Django admin's own error rendering never has to be reimplemented here.
 */
(function () {
  "use strict";

  var DB_NAME = "fa_admin_file_restore";
  var STORE_NAME = "files";

  function openDb() {
    return new Promise(function (resolve, reject) {
      var request = indexedDB.open(DB_NAME, 1);
      request.onupgradeneeded = function () {
        request.result.createObjectStore(STORE_NAME);
      };
      request.onsuccess = function () {
        resolve(request.result);
      };
      request.onerror = function () {
        reject(request.error);
      };
    });
  }

  function storageKey(inputName) {
    // Scoped to this exact admin page (e.g. .../catalog/product/add/)
    // *and* this exact form field name (e.g. "productimage_set-0-image"),
    // so different inline rows, and different pages, never collide.
    return window.location.pathname + "::" + inputName;
  }

  function isErrorRedisplay() {
    return !!document.querySelector(".errorlist, .errornote");
  }

  function saveFileInputsOnSubmit() {
    document.querySelectorAll('input[type="file"]').forEach(function (input) {
      if (!input.name || !input.files || input.files.length === 0) {
        return;
      }
      var files = Array.prototype.slice.call(input.files);
      openDb()
        .then(function (db) {
          db.transaction(STORE_NAME, "readwrite").objectStore(STORE_NAME).put(files, storageKey(input.name));
        })
        .catch(function () {
          // This is purely a UX convenience — if IndexedDB isn't
          // available for some reason, the form must still submit
          // normally, with no error shown for this.
        });
    });
  }

  function restoreFileInputsOnLoad() {
    var fileInputs = document.querySelectorAll('input[type="file"]');
    if (fileInputs.length === 0) {
      return;
    }
    var errorRedisplay = isErrorRedisplay();
    openDb()
      .then(function (db) {
        fileInputs.forEach(function (input) {
          if (!input.name) {
            return;
          }
          var key = storageKey(input.name);
          var tx = db.transaction(STORE_NAME, "readwrite");
          var getRequest = tx.objectStore(STORE_NAME).get(key);
          getRequest.onsuccess = function () {
            var files = getRequest.result;
            if (files && files.length && errorRedisplay) {
              var transfer = new DataTransfer();
              files.forEach(function (file) {
                transfer.items.add(file);
              });
              input.files = transfer.files;
            }
            if (files) {
              // One-time use either way: a restored selection, or a
              // stale entry from an abandoned earlier attempt, is
              // equally done being useful once we've looked at it.
              tx.objectStore(STORE_NAME).delete(key);
            }
          };
        });
      })
      .catch(function () {
        // No IndexedDB available — nothing to restore, page loads as normal.
      });
  }

  document.addEventListener("DOMContentLoaded", function () {
    restoreFileInputsOnLoad();
    document.querySelectorAll("#content-main form").forEach(function (form) {
      form.addEventListener("submit", saveFileInputsOnSubmit);
    });
  });
})();
