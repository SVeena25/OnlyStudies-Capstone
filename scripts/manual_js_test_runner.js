/*
Manual JavaScript test runner for browser console execution.
Usage:
1) Open OnlyStudies in a browser and log in/out as required by each scenario.
2) Open DevTools Console.
3) Paste this file content and run.
4) Execute: OnlyStudiesManualTests.runAll() or run each category method.
*/
(function () {
  function nowIso() {
    return new Date().toISOString();
  }

  function logResult(level, area, name, details) {
    var color = level === "PASS" ? "#137333" : level === "WARN" ? "#b06000" : "#c5221f";
    console.log(
      "%c[" + level + "]%c " + area + " :: " + name + "\n" + details,
      "color:" + color + ";font-weight:bold;",
      "color:inherit;"
    );
  }

  function pass(area, name, details) {
    logResult("PASS", area, name, details || "");
  }

  function warn(area, name, details) {
    logResult("WARN", area, name, details || "");
  }

  function fail(area, name, details) {
    logResult("FAIL", area, name, details || "");
  }

  function assert(area, name, condition, detailsIfFail, detailsIfPass) {
    if (condition) {
      pass(area, name, detailsIfPass || "Condition met.");
      return true;
    }
    fail(area, name, detailsIfFail || "Condition not met.");
    return false;
  }

  function sameOriginPath(path) {
    return new URL(path, window.location.origin).toString();
  }

  async function probeRoute(path) {
    var response = await fetch(sameOriginPath(path), {
      method: "GET",
      credentials: "same-origin",
      redirect: "manual"
    });
    return {
      path: path,
      status: response.status,
      redirected: response.type === "opaqueredirect" || (response.status >= 300 && response.status < 400)
    };
  }

  var OnlyStudiesManualTests = {
    meta: {
      generatedAt: nowIso(),
      version: "1.0"
    },

    functionality: async function () {
      var area = "Functionality";
      console.group("Manual JS Test :: " + area);

      assert(
        area,
        "Core nav links exist",
        !!document.querySelector('a[href="/"]') && !!document.querySelector('form[action="/search/"]'),
        "Expected home link and search form were not found.",
        "Home link and search form found."
      );

      var protectedRoutes = ["/tasks/", "/appointments/", "/notifications/", "/blog/create/"];
      for (var i = 0; i < protectedRoutes.length; i += 1) {
        try {
          var probe = await probeRoute(protectedRoutes[i]);
          if (probe.status === 200) {
            warn(area, "Protected route check " + probe.path, "Returned 200 in current session. Run while logged out to verify redirect-to-login behavior.");
          } else if (probe.status >= 300 && probe.status < 400) {
            pass(area, "Protected route check " + probe.path, "Returned redirect status (expected for unauthenticated access).");
          } else {
            warn(area, "Protected route check " + probe.path, "Returned status " + probe.status + ". Validate behavior manually.");
          }
        } catch (error) {
          fail(area, "Protected route check " + protectedRoutes[i], "Request failed: " + error.message);
        }
      }

      var firstForm = document.querySelector("form");
      if (firstForm) {
        var requiredControls = firstForm.querySelectorAll("[required]");
        if (requiredControls.length > 0) {
          var invalidCount = 0;
          requiredControls.forEach(function (el) {
            if (typeof el.checkValidity === "function" && !el.checkValidity()) {
              invalidCount += 1;
            }
          });
          pass(area, "HTML required-field validation presence", "Detected " + requiredControls.length + " required control(s), " + invalidCount + " currently invalid in default state.");
        } else {
          warn(area, "HTML required-field validation presence", "No required controls in current page form.");
        }
      } else {
        warn(area, "Form validation probe", "No form found on current page.");
      }

      console.groupEnd();
    },

    usability: function () {
      var area = "Usability";
      console.group("Manual JS Test :: " + area);

      assert(
        area,
        "Skip link exists",
        !!document.querySelector(".skip-link"),
        "Expected .skip-link was not found.",
        "Skip link detected."
      );

      var focusables = document.querySelectorAll("a, button, input, select, textarea, [tabindex]");
      assert(
        area,
        "Focusable controls present",
        focusables.length > 10,
        "Too few focusable controls detected (" + focusables.length + ").",
        "Focusable controls detected: " + focusables.length
      );

      var unlabeledInputs = Array.prototype.filter.call(
        document.querySelectorAll("input, select, textarea"),
        function (el) {
          var hasLabel = !!document.querySelector('label[for="' + el.id + '"]');
          var hasAria = !!(el.getAttribute("aria-label") || el.getAttribute("aria-labelledby"));
          return !hasLabel && !hasAria && el.type !== "hidden";
        }
      );

      if (unlabeledInputs.length === 0) {
        pass(area, "Form labels/ARIA", "All visible form controls appear labeled.");
      } else {
        warn(area, "Form labels/ARIA", "Found potentially unlabeled controls: " + unlabeledInputs.length);
      }

      console.groupEnd();
    },

    responsiveness: function () {
      var area = "Responsiveness";
      console.group("Manual JS Test :: " + area);

      var hasHorizontalOverflow = document.documentElement.scrollWidth > window.innerWidth;
      assert(
        area,
        "No horizontal overflow at current viewport",
        !hasHorizontalOverflow,
        "scrollWidth=" + document.documentElement.scrollWidth + ", innerWidth=" + window.innerWidth,
        "Current viewport width check passed."
      );

      var navbarToggler = document.querySelector(".navbar-toggler");
      assert(
        area,
        "Navbar toggler exists",
        !!navbarToggler,
        "Navbar toggler missing; mobile navigation may fail.",
        "Navbar toggler found."
      );

      var tinyTargets = Array.prototype.filter.call(
        document.querySelectorAll("button, a.btn, input[type='submit']"),
        function (el) {
          var rect = el.getBoundingClientRect();
          return rect.width > 0 && rect.height > 0 && (rect.width < 32 || rect.height < 32);
        }
      );

      if (tinyTargets.length === 0) {
        pass(area, "Tap target sizing", "No visible button targets under 32x32px detected.");
      } else {
        warn(area, "Tap target sizing", "Found small tap targets: " + tinyTargets.length + ". Verify at 375px viewport.");
      }

      console.groupEnd();
    },

    dataManagement: async function () {
      var area = "Data Management";
      console.group("Manual JS Test :: " + area);

      try {
        var res = await fetch(sameOriginPath("/api/notifications/"), {
          method: "GET",
          credentials: "same-origin"
        });
        if (!res.ok) {
          warn(area, "Notifications API access", "Status " + res.status + ". Ensure you are logged in and endpoint is enabled.");
        } else {
          var payload = await res.json();
          var hasNotificationsKey = Object.prototype.hasOwnProperty.call(payload, "notifications");
          assert(area, "Notifications API payload shape", hasNotificationsKey, "Expected `notifications` key missing.");

          var hasPotentialPIILeak = JSON.stringify(payload).toLowerCase().indexOf("password") !== -1;
          assert(area, "No obvious sensitive fields", !hasPotentialPIILeak, "Payload appears to contain sensitive terms.", "No obvious sensitive fields detected in payload.");

          pass(area, "Notification count", "Items returned: " + (payload.notifications ? payload.notifications.length : 0));
        }
      } catch (error) {
        fail(area, "Notifications API probe", "Request failed: " + error.message);
      }

      warn(
        area,
        "Cross-user isolation",
        "Manual step required: repeat this API probe in a second browser profile with another user and verify datasets do not overlap."
      );

      console.groupEnd();
    },

    runAll: async function () {
      console.group("OnlyStudies Manual JS Test Run");
      console.log("Version:", this.meta.version, "Generated:", this.meta.generatedAt);
      await this.functionality();
      this.usability();
      this.responsiveness();
      await this.dataManagement();
      console.groupEnd();
      console.log("Manual JavaScript test run completed.");
    }
  };

  window.OnlyStudiesManualTests = OnlyStudiesManualTests;
  console.log("OnlyStudiesManualTests loaded. Run: OnlyStudiesManualTests.runAll()");
})();
