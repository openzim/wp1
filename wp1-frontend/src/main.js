import 'bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';

import 'jquery';
import 'datatables.net';
import 'datatables.net-dt/css/jquery.dataTables.min.css';

import Vue from 'vue';
import VueRouter from 'vue-router';

import App from './App.vue';
import ArticlePage from './components/ArticlePage.vue';
import BookBuilder from './components/BookBuilder.vue';
import PetscanBuilder from './components/PetscanBuilder.vue';
import SimpleBuilder from './components/SimpleBuilder.vue';
import SparqlBuilder from './components/SparqlBuilder.vue';
import ComparePage from './components/ComparePage.vue';
import IndexPage from './components/IndexPage.vue';
import MyLists from './components/MyLists.vue';
import ProjectPage from './components/ProjectPage.vue';
import UpdatePage from './components/UpdatePage.vue';
import ZimFile from './components/ZimFile.vue';
import WikiProjectBuilder from './components/WikiProjectBuilder.vue';


Vue.config.productionTip = false;

Vue.use(VueRouter);

const BASE_TITLE = 'Wikipedia 1.0 Server';

import VueI18n from 'vue-i18n';


// Import translations
import en from './locales/en.json';
import fr from './locales/fr.json';
import es from './locales/es.json';
import ar from './locales/ar.json';

Vue.use(VueI18n);

const userLang = navigator.language.split('-')[0]; // Detect browser language
const availableLanguages = ['en', 'fr', 'es', 'ar'];
const defaultLanguage = availableLanguages.includes(userLang) ? userLang : 'en';

const i18n = new VueI18n({
  locale: defaultLanguage,
  fallbackLocale: 'en',
  messages: { en, fr, es, ar }
});




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
    component: SimpleBuilder,
    meta: {
      title: () => BASE_TITLE + ' - Create Simple Selection',
    },
  },
  {
    path: '/selections/sparql',
    component: SparqlBuilder,
    meta: {
      title: () => BASE_TITLE + ' - Create SPARQL Selection',
    },
  },
  {
    path: '/selections/petscan',
    component: PetscanBuilder,
    meta: {
      title: () => BASE_TITLE + ' - Create Petscan Selection',
    },
  },
  {
    path: '/selections/book',
    component: BookBuilder,
    meta: {
      title: () => BASE_TITLE + ' - Create Book Selection',
    },
  },
  {
    path: '/selections/wikiproject',
    component: WikiProjectBuilder,
    meta: {
      title: () => BASE_TITLE + ' - Edit WikiProject Selection',
    },
  },
  {
    path: '/selections/simple/:builder_id',
    component: SimpleBuilder,
    meta: {
      title: () => BASE_TITLE + ' - Edit Simple Selection',
    },
  },
  {
    path: '/selections/sparql/:builder_id',
    component: SparqlBuilder,
    meta: {
      title: () => BASE_TITLE + ' - Edit SPARQL Selection',
    },
  },
  {
    path: '/selections/petscan/:builder_id',
    component: PetscanBuilder,
    meta: {
      title: () => BASE_TITLE + ' - Edit Petscan Selection',
    },
  },
  {
    path: '/selections/book/:builder_id',
    component: BookBuilder,
    meta: {
      title: () => BASE_TITLE + ' - Edit Book Selection',
    },
  },
  {
    path: '/selections/wikiproject/:builder_id',
    component: WikiProjectBuilder,
    meta: {
      title: () => BASE_TITLE + ' - Edit WikiProject Selection',
    },
  },
  {
    path: '/selections/:builder_id/zim',
    component: ZimFile,
    meta: {
      title: () => BASE_TITLE + ' - ZIM file',
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
  el: '#app',
  router,
  i18n,
  data: {
    isLoggedIn: false,
  },
  render: h => h(App),
});
