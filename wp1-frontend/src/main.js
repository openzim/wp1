import 'bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';

import Vue from 'vue';
import VueRouter from 'vue-router';

import App from './App.vue';
import ArticlePage from './components/ArticlePage.vue';
import IndexPage from './components/IndexPage.vue';
import ProjectPage from './components/ProjectPage.vue';
import UpdatePage from './components/UpdatePage.vue';

Vue.config.productionTip = false;

Vue.use(VueRouter);

const BASE_TITLE = 'Wikipedia 1.0 Server';

const routes = [
  {
    path: '/',
    component: IndexPage,
    meta: { title: () => BASE_TITLE }
  },
  {
    path: '/update/',
    component: UpdatePage,
    meta: { title: () => BASE_TITLE + ' - Manual Update' }
  },
  {
    path: '/update/:projectName',
    component: UpdatePage,
    props: route => ({
      incomingSearch: route.params.projectName,
      updateTime: route.query.updateTime,
      showSuccessMessage: route.query.success == 1,
      showFailureMessage: route.query.failure == 1
    }),
    meta: {
      title: route =>
        BASE_TITLE + ' - Manual Update - ' + route.params.projectName
    }
  },
  {
    path: '/project/:projectName',
    component: ProjectPage,
    meta: {
      title: route => BASE_TITLE + ' - ' + route.params.projectName
    }
  },
  {
    path: '/project/:projectName/articles',
    component: ArticlePage,
    meta: {
      title: route =>
        BASE_TITLE + ' - ' + route.params.projectName + ' articles'
    }
  }
];

const router = new VueRouter({
  routes
});

router.beforeEach((to, from, next) => {
  document.title = to.meta.title(to);
  next();
});

new Vue({
  el: '#app',
  render: h => h(App),
  router,
  template: '<App/>',
  components: { App }
});
