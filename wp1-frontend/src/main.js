import 'bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';

import Vue from 'vue';
import VueRouter from 'vue-router';

import App from './App.vue';
import ArticlePage from './components/ArticlePage.vue';
import IndexPage from './components/IndexPage.vue';
import ProjectPage from './components/ProjectPage.vue';

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
