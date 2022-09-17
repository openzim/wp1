import 'bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';

import 'jquery';
import 'datatables.net';
import 'datatables.net-dt/css/jquery.dataTables.min.css';

import Vue from 'vue';
import VueRouter from 'vue-router';

import App from './App.vue';
import ArticlePage from './components/ArticlePage.vue';
import SimpleList from './components/SimpleList.vue';
import SparqlList from './components/SparqlList.vue';
import ComparePage from './components/ComparePage.vue';
import IndexPage from './components/IndexPage.vue';
import MyLists from './components/MyLists.vue';
import ProjectPage from './components/ProjectPage.vue';
import UpdatePage from './components/UpdatePage.vue';

Vue.config.productionTip = false;

Vue.use(VueRouter);

const BASE_TITLE = 'Wikipedia 1.0 Server';

const routes = [
  {
    path: '/',
    component: IndexPage,
    meta: { title: () => BASE_TITLE },
  },
  {
    path: '/update/',
    component: UpdatePage,
    meta: { title: () => BASE_TITLE + ' - Manual Update' },
  },
  {
    path: '/update/:projectName',
    component: UpdatePage,
    props: (route) => ({
      incomingSearch: route.params.projectName,
    }),
    meta: {
      title: (route) =>
        BASE_TITLE + ' - Manual Update - ' + route.params.projectName,
    },
  },
  {
    path: '/project/:projectName',
    component: ProjectPage,
    meta: {
      title: (route) => BASE_TITLE + ' - ' + route.params.projectName,
    },
  },
  {
    path: '/project/:projectName/articles',
    component: ArticlePage,
    props: (route) => ({
      currentProject: route.params.projectName,
    }),
    meta: {
      title: (route) =>
        BASE_TITLE + ' - ' + route.params.projectName + ' articles',
    },
  },
  {
    path: '/compare/',
    component: ComparePage,
    meta: {
      title: () => BASE_TITLE + ' - Comparing projects',
    },
  },
  {
    path: '/compare/:projectNameA/:projectNameB',
    component: ComparePage,
    props: (route) => ({
      incomingSearchA: route.params.projectNameA,
      incomingSearchB: route.params.projectNameB,
    }),
    meta: {
      title: (route) =>
        BASE_TITLE +
        ' - Comparing ' +
        route.params.projectNameA +
        ' and ' +
        route.params.projectNameB,
    },
  },
  {
    path: '/selections/user',
    component: MyLists,
    meta: {
      title: () => BASE_TITLE + ' - My Selections',
    },
  },
  {
    path: '/selections/simple',
    component: SimpleList,
    meta: {
      title: () => BASE_TITLE + ' - Create Simple Selection',
    },
  },
  {
    path: '/selections/sparql',
    component: SparqlList,
    meta: {
      title: () => BASE_TITLE + ' - Create SPARQL Selection',
    },
  },
  {
    path: '/selections/simple/:builder_id',
    component: SimpleList,
    meta: {
      title: () => BASE_TITLE + ' - Edit Simple Selection',
    },
  },
  {
    path: '/selections/sparql/:builder_id',
    component: SparqlList,
    meta: {
      title: () => BASE_TITLE + ' - Edit SPARQL Selection',
    },
  },
];

const router = new VueRouter({
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { x: 0, y: 0 };
    }
  },
});

router.beforeEach((to, from, next) => {
  document.title = to.meta.title(to);
  next();
});

new Vue({
  data: {
    isLoggedIn: false,
  },
  el: '#app',
  render: (h) => h(App),
  router,
  template: '<App/>',
  components: { App },
});
