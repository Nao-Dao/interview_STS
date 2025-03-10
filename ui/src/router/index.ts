import { createRouter, createWebHashHistory } from 'vue-router'

import view from '../view/index.vue';

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "experment",
      component: view
    },
    {
      path: "/manual/:cid",
      name: "manual",
      component: () => import("../view/manual.vue")
    },
    {
      path: "/auto/:cid",
      name: "auto",
      component: () => import("../view/auto.vue")
    }
  ]
});

export default router;
