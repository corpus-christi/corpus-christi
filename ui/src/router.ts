// Vue Router configuration

import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "./stores/auth";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      name: "public",
      path: "/",
      meta: { layout: "arco" },
      component: () => import("@/pages/Public.vue")
    },
    {
      name: "public-events",
      path: "/public/events",
      meta: { authRequired: false },
      component: () => import("@/pages/public/Events.vue")
    },
    {
      name: "public-courses",
      path: "/public/courses",
      meta: { authRequired: false },
      component: () => import("@/pages/public/Courses.vue")
    },
    {
      name: "login",
      path: "/login",
      meta: { layout: "arco" },
      component: () => import("@/pages/Login.vue")
    },
    {
      name: "signup",
      path: "/signup",
      meta: { layout: "arco" },
      component: () => import("@/pages/Signup.vue")
    },
    {
      name: "admin",
      path: "/admin",
      meta: { authRequired: true },
      component: () => import("@/components/events/Dashboard.vue")
    },
    {
      name: "people",
      path: "/people",
      meta: { authRequired: true },
      component: () => import("@/pages/People.vue")
    },
    {
      name: "groups",
      path: "/groups",
      meta: { authRequired: true },
      component: () => import("@/pages/Groups.vue"),
      redirect: { name: "all-groups" },
      children: [
        {
          name: "all-groups",
          path: "all",
          meta: { authRequired: true },
          component: () => import("@/components/groups/GroupTable.vue")
        },
        {
          name: "group",
          path: ":group",
          meta: { authRequired: true },
          redirect: { name: "group-details" },
          component: () => import("@/components/groups/Group.vue"),
          children: [
            {
              name: "group-details",
              path: "details",
              meta: { authRequired: true },
              component: () => import("@/components/groups/GroupDetails.vue")
            },
            {
              name: "group-members",
              path: "members",
              meta: { authRequired: true },
              component: () =>
                import("@/components/groups/members/GroupMembers.vue")
            },
            {
              name: "group-meetings",
              path: "meetings",
              meta: { authRequired: true },
              component: () =>
                import("@/components/groups/meetings/GroupMeetings.vue")
            }
          ]
        }
      ]
    },
    {
      name: "events",
      path: "/events",
      meta: { authRequired: true },
      component: () => import("@/pages/Events.vue"),
      redirect: { name: "all-events" },
      children: [
        {
          name: "all-events",
          path: "all",
          meta: { authRequired: true },
          component: () => import("@/components/events/EventTable.vue")
        },
        {
          name: "events-dashboard",
          path: "dashboard",
          meta: { authRequired: true },
          component: () => import("@/components/events/Dashboard.vue")
        },
        {
          name: "events-calendar",
          path: "calendar",
          meta: { authRequired: true },
          component: () => import("@/components/events/Calendar.vue")
        }
      ]
    },
    {
      name: "event",
      path: "/event/:event",
      meta: { authRequired: true },
      redirect: { name: "event-details" },
      component: () => import("@/components/events/Event.vue"),
      children: [
        {
          name: "event-details",
          path: "details",
          meta: { authRequired: true },
          component: () => import("@/components/events/EventDetails.vue")
        },
        {
          name: "event-participants",
          path: "participants",
          meta: { authRequired: true },
          component: () => import("@/components/events/EventParticipants.vue")
        }
      ]
    },
    {
      name: "teams",
      path: "/teams",
      meta: { authRequired: true },
      component: () => import("@/pages/Teams.vue"),
      redirect: { name: "all-teams" },
      children: [
        {
          name: "all-teams",
          path: "all",
          meta: { authRequired: true },
          component: () => import("@/components/teams/TeamTable.vue")
        },
        {
          name: "team",
          path: ":team",
          meta: { authRequired: true },
          component: () => import("@/components/teams/Team.vue")
        }
      ]
    },
    {
      name: "assets",
      path: "/assets",
      meta: { authRequired: true },
      component: () => import("@/pages/Assets.vue")
    },
    {
      name: "places",
      path: "/places",
      meta: { authRequired: true },
      component: () => import("@/pages/Places.vue")
    },
    {
      name: "diplomas-admin",
      path: "/diplomas",
      meta: { authRequired: true },
      component: () => import("@/pages/Diplomas.vue"),
      redirect: { name: "all-diplomas" },
      children: [
        {
          name: "all-diplomas",
          path: "all",
          meta: { authRequired: true },
          component: () => import("@/components/diplomas/DiplomasTable.vue")
        },
        {
          name: "diploma-details",
          path: ":diplomaId",
          meta: { authRequired: true },
          props: true,
          component: () => import("@/components/diplomas/DiplomaDetails.vue")
        }
      ]
    },
    {
      name: "transcripts",
      path: "/transcripts",
      meta: { authRequired: true },
      component: () => import("@/pages/Transcripts.vue"),
      redirect: { name: "all-transcripts" },
      children: [
        {
          name: "all-transcripts",
          path: "all",
          meta: { authRequired: true },
          component: () =>
            import("@/components/transcripts/TranscriptsTable.vue")
        },
        {
          name: "transcript-details",
          path: ":studentId",
          meta: { authRequired: true },
          props: true,
          component: () =>
            import("@/components/transcripts/TranscriptDetails.vue")
        }
      ]
    },
    {
      name: "courses",
      path: "/courses",
      meta: { authRequired: true },
      component: () => import("@/pages/Courses.vue"),
      redirect: { name: "all-courses" },
      children: [
        {
          name: "courses-dashboard",
          path: "dashboard",
          meta: { authRequired: true },
          component: () => import("@/components/courses/Dashboard.vue")
        },
        {
          name: "all-courses",
          path: "all",
          meta: { authRequired: true },
          component: () => import("@/components/courses/CoursesTable.vue")
        },
        {
          name: "course-details",
          path: ":courseId",
          meta: { authRequired: true },
          props: true,
          component: () => import("@/components/courses/CourseDetails.vue")
        },
        {
          name: "course-offering",
          path: ":courseId/offering/:offeringId",
          meta: { authRequired: true },
          props: true,
          redirect: { name: "course-offering-details" },
          component: () => import("@/components/courses/CourseOffering.vue"),
          children: [
            {
              name: "course-offering-details",
              path: "details",
              meta: { authRequired: true },
              props: true,
              component: () =>
                import("@/components/courses/CourseOfferingDetails.vue")
            },
            {
              name: "course-offering-students",
              path: "students",
              meta: { authRequired: true },
              props: true,
              component: () =>
                import("@/components/courses/CourseOfferingStudents.vue")
            },
            {
              name: "course-offering-meetings",
              path: "meetings",
              meta: { authRequired: true },
              props: true,
              component: () =>
                import("@/components/courses/CourseOfferingMeetings.vue")
            }
          ]
        }
      ]
    }
  ]
});

router.beforeEach((to, _from, next) => {
  if (to.matched.some(record => record.meta.authRequired)) {
    const authStore = useAuthStore();
    if (authStore.isLoggedIn) {
      next();
    } else {
      next({
        name: "login",
        query: { redirect: to.name as string }
      });
    }
  } else {
    next();
  }
});

export default router;
