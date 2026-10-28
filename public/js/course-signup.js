/**
 * Sign-up form handler for the Innovation & Entrepreneurship course page
 * (src/innovation-course.template.html).
 *
 * Submissions are recorded in a Google Form. Because Google Forms does not
 * allow cross-origin fetch() submissions, this follows the classic pattern:
 *
 *   1. Intercept the visible form's submit event.
 *   2. Drop the submission if the off-screen honeypot field (`website`) was
 *      filled in. People never see that field; spam bots that fill every input
 *      do. The bot still sees the normal thank-you message so it learns nothing.
 *   3. Build a hidden <form> whose inputs use the Google Form's `entry.*` field
 *      IDs, POST it to the form's /formResponse endpoint with the hidden
 *      <iframe name="gform-iframe"> as the target, and treat the iframe's
 *      `load` event as confirmation.
 *   4. Show "Thank you for your submission!" beneath the form and disable the
 *      fields to prevent duplicate submissions.
 *
 * The entry IDs below come from the form's pre-filled link:
 *   https://docs.google.com/forms/d/e/<GOOGLE_FORM_ID>/viewform?usp=pp_url
 *     &entry.1836183358=John+Smith
 *     &entry.324405984=smithj@pennmedicine.upenn.edu
 *     &entry.747874515=Yes
 *     &entry.1253580093=MS1
 * If the Google Form is rebuilt, regenerate a pre-filled link and update them.
 *
 * Licensed under the MIT License. Copyright PennHealthX 2026.
 */
(function () {
  "use strict";

  var GOOGLE_FORM_ID = "1FAIpQLScVGgam_ANSB8lPOgO71kCjBZamHcuoxyNr9s0AGwjRnXTJ9g";
  var GOOGLE_FORM_ACTION =
    "https://docs.google.com/forms/d/e/" + GOOGLE_FORM_ID + "/formResponse";

  // Visible input name -> Google Form entry ID.
  var ENTRY_IDS = {
    name: "entry.1836183358",
    email: "entry.324405984",
    attending: "entry.747874515",
    training_year: "entry.1253580093"
  };

  var IFRAME_NAME = "gform-iframe";
  var HONEYPOT_NAME = "website";

  // Google normally answers within a second. If the iframe never fires `load`
  // (e.g. the response is blocked from rendering in a frame), assume the POST
  // went through rather than leaving the user stuck on "Sending".
  var FALLBACK_MS = 8000;

  var THANK_YOU_MESSAGE = "Thank you for your submission!";

  var form = document.getElementById("course-signup-form");
  var iframe = document.getElementById(IFRAME_NAME);
  if (!form || !iframe) return;

  var fields = form.querySelector(".signup-fields");
  var submitButton = form.querySelector('button[type="submit"]');
  var status = document.getElementById("signup-status");
  var honeypot = form.querySelector('input[name="' + HONEYPOT_NAME + '"]');
  var submitLabel = submitButton ? submitButton.textContent : "Sign up";
  var pending = false;

  function showStatus(message, kind) {
    if (!status) return;
    status.textContent = message;
    status.className = "signup-status " + kind;
    status.hidden = false;
  }

  function markSubmitted() {
    if (fields) fields.disabled = true;
    showStatus(THANK_YOU_MESSAGE, "success");
  }

  function setSending(isSending) {
    if (!submitButton) return;
    submitButton.disabled = isSending;
    submitButton.textContent = isSending ? "Sending…" : submitLabel;
  }

  function buildHiddenForm(data) {
    var hiddenForm = document.createElement("form");
    hiddenForm.style.display = "none";
    hiddenForm.action = GOOGLE_FORM_ACTION;
    hiddenForm.method = "POST";
    hiddenForm.target = IFRAME_NAME;

    Object.keys(ENTRY_IDS).forEach(function (field) {
      var input = document.createElement("input");
      input.type = "hidden";
      input.name = ENTRY_IDS[field];
      input.value = data.get(field) || "";
      hiddenForm.appendChild(input);
    });

    return hiddenForm;
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();

    // Honeypot check comes first so bots never trigger validation UI.
    if (honeypot && honeypot.value.trim() !== "") {
      markSubmitted();
      return;
    }

    if (typeof form.checkValidity === "function" && !form.checkValidity()) {
      if (typeof form.reportValidity === "function") form.reportValidity();
      return;
    }

    if (pending) return;
    pending = true;
    setSending(true);

    var hiddenForm = buildHiddenForm(new FormData(form));
    document.body.appendChild(hiddenForm);

    var fallbackTimer = null;

    function finish() {
      if (!pending) return;
      pending = false;
      clearTimeout(fallbackTimer);
      iframe.onload = null;
      hiddenForm.remove();
      setSending(false);
      markSubmitted();
    }

    iframe.onload = finish;
    fallbackTimer = setTimeout(finish, FALLBACK_MS);
    hiddenForm.submit();
  });
})();
