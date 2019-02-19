// Vue Router configuration

import Vue from "vue";
import VueRouter from "vue-router";
import store from "./store";

Vue.use(VueRouter);

const router = new VueRouter({
  mode: "history",
  routes: [
    {
      name: "public",
      path: "/",
      meta: { layout: "arco" },
      component: () => import("@/pages/Public")
    },
    {
      name: "public-events",
      path: "/public/events",
      meta: { authRequired: false },
      component: () => import("@/pages/public/Events")
    },
    {
      name: "public-courses",
      path: "/public/courses",
      meta: { authRequired: false },
      component: () => import("@/pages/public/Courses")
    },
    {
      name: "login",
      path: "/login",
      meta: { layout: "arco" },
      component: () => import("@/pages/Login")
    },
    {
      name: "signup",
      path: "/signup",
      meta: { layout: "arco" },
      component: () => import("@/pages/Signup")
    },
    {
      name: "admin",
      path: "/admin",
      meta: { authRequired: true },
      // component: () => import("@/pages/Admin")
      component: () => import("@/components/events/Dashboard")
    },
    {
      name: "people",
      path: "/people",
      meta: { authRequired: true },
      component: () => import("@/pages/People")
    },
    {
      name: "groups",
      path: "/groups",
      meta: { authRequired: true },
      component: () => import("@/pages/Groups"),
      redirect: { name: "all-groups" },
      children: [
        {
          name: "all-groups",
          path: "all",
          meta: { authRequired: true },
          component: () => import("@/components/groups/GroupTable")
        },
        {
          name: "group",
          path: ":group",
          meta: { authRequired: true },
          redirect: { name: "group-details" },
          component: () => import("@/components/groups/Group"),
          children: [
            {
              name: "group-details",
              path: "details",
              meta: { authRequired: true },
              component: () => import("@/components/groups/GroupDetails")
            },
            {
              name: "group-members",
              path: "members",
              meta: { authRequired: true },
              component: () =>
                import("@/components/groups/members/GroupMembers")
            },
            {
              name: "group-meetings",
              path: "meetings",
              meta: { authRequired: true },
              component: () =>
                import("@/components/groups/meetings/GroupMeetings")
            }
          ]
        }
      ]
    },
    {
      name: "events",
      path: "/events",
      meta: { authRequired: true },
      component: () => import("@/pages/Events"),
      redirect: { name: "all-events" },
      children: [
        {
          name: "all-events",
          path: "all",
          meta: { authRequired: true },
          component: () => import("@/components/events/EventTable")
        },
        {
          name: "events-dashboard",
          path: "dashboard",
          meta: { authRequired: true },
          component: () => import("@/components/events/Dashboard")
        },
        {
          name: "events-calendar",
          path: "calendar",
          meta: { authRequired: true },
          component: () => import("@/components/events/Calendar")
        }
      ]
    },
    {
      name: "event",
      path: "/event/:event",
      meta: { authRequired: true },
      redirect: { name: "event-details" },
      component: () => import("@/components/events/Event"),
      children: [
        {
          name: "event-details",
          path: "details",
          meta: { authRequired: true },
          component: () => import("@/components/events/EventDetails")
        },
        {
          name: "event-participants",
          path: "participants",
          meta: { authRequired: true },
          component: () => import("@/components/events/EventParticipants")
        }
      ]
    },
    {
      name: "teams",
      path: "/teams",
      meta: { authRequired: true },
      component: () => import("@/pages/Teams"),
      redirect: { name: "all-teams" },
      children: [
        {
          name: "all-teams",
          path: "all",
          meta: { authRequired: true },
          component: () => import("@/components/teams/TeamTable")
        },
        {
          name: "team",
          path: ":team",
          meta: { authRequired: true },
          component: () => import("@/components/teams/Team")
        }
      ]
    },
    {
      name: "assets",
      path: "/assets",
      meta: { authRequired: true },
      component: () => import("@/pages/Assets")
    },
    {
      name: "locale",
      path: "/locale",
      meta: { authRequired: true },
      component: () => import("@/pages/Locale")
    },
    {
      name: "diplomas-admin",
      path: "/diplomas",
      meta: { authRequired: true },
      component: () => import("@/pages/Diplomas"),
      redirect: { name: "all-diplomas" },
      children: [
        {
          name: "all-diplomas",
          path: "all",
          meta: { authRequired: true },
          component: () => import("@/components/diplomas/DiplomasTable")
        },
        {
          name: "diploma-details",
          path: ":diplomaId",
          meta: { authRequired: true },
          props: true,
          component: () => import("@/components/diplomas/DiplomaDetails")
        }
      ]
    },
    {
      name: "transcripts",
      path: "/transcripts",
      meta: { authRequired: true },
      component: () => import("@/pages/Transcripts"),
      redirect: { name: "all-transcripts" },
      children: [
        {
          name: "all-transcripts",
          path: "all",
          meta: { authRequired: true },
          component: () => import("@/components/transcripts/TranscriptsTable")
        },
        {
          name: "transcript-details",
          path: ":studentId",
          meta: { authRequired: true },
          props: true,
          component: () => import("@/components/transcripts/TranscriptDetails")
        }
      ]
    },
    {
      name: "courses",
      path: "/courses",
      meta: { authRequired: true },
      component: () => import("@/pages/Courses"),
      redirect: { name: "all-courses" },
      children: [
        {
          name: "courses-dashboard",
          path: "dashboard",
          meta: { authRequired: true },
          component: () => import("@/components/courses/Dashboard")
        },
        {
          name: "all-courses",
          path: "all",
          meta: { authRequired: true },
          component: () => import("@/components/courses/CoursesTable")
        },
        {
          name: "course-details",
          path: ":courseId",
          meta: { authRequired: true },
          props: true,
          component: () => import("@/components/courses/CourseDetails")
        },
        {
          name: "course-offering",
          path: ":courseId/offering/:offeringId",
          meta: { authRequired: true },
          props: true,
          redirect: { name: "course-offering-details" },
          component: () => import("@/components/courses/CourseOffering"),
          children: [
            {
              name: "course-offering-details",
              path: "details",
              meta: { authRequired: true },
              props: true,
              component: () =>
                import("@/components/courses/CourseOfferingDetails")
            },
            {
              name: "course-offering-students",
              path: "students",
              meta: { authRequired: true },
              props: true,
              component: () =>
                import("@/components/courses/CourseOfferingStudents")
            },
            {
              name: "course-offering-meetings",
              path: "meetings",
              meta: { authRequired: true },
              props: true,
              component: () =>
                import("@/components/courses/CourseOfferingMeetings")
            }
          ]
        }
      ]
    }
  ]
});

router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.authRequired)) {
    // The destination requires authentication.
    if (store.getters.isLoggedIn) {
      // But we're already logged in.
      next();
    } else {
      // So redirect to the login page; retain
      // the desired page for a later redirect.
      next({
        name: "login",
        query: { redirect: to.name }
      });
    }
  } else {
    // The destination doesn't require authentication.
    next();
  }
});

export default router;
