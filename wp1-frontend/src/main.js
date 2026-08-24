import '@fontsource/ibm-plex-sans/400.css';
import '@fontsource/ibm-plex-sans/500.css';
import '@fontsource/ibm-plex-sans/600.css';
import '@fontsource/ibm-plex-sans/700.css';
import '@fontsource/ibm-plex-mono/400.css';
import '@fontsource/ibm-plex-mono/500.css';
import '@fontsource/ibm-plex-mono/600.css';
import './tailwind.css';

import { createApp } from 'vue';
import { createRouter, createWebHashHistory } from 'vue-router';

import App from './App.vue';
import ArticlePage from './components/ArticlePage.vue';
import ComparePage from './components/ComparePage.vue';
import AssessmentsByProject from './components/AssessmentsByProject.vue';
import IndexPage from './components/IndexPage.vue';
import UpdatePage from './components/UpdatePage.vue';
import CombinatorPage from './components/selections/CombinatorPage.vue';
import NewSelectionPage from './components/selections/NewSelectionPage.vue';
import SelectionsPage from './components/selections/SelectionsPage.vue';
import ZimPage from './components/selections/ZimPage.vue';

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
    // Same component as /: the index shows the selected project's table
    // in place, below the search hero.
    path: '/project/:projectName',
    component: IndexPage,
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
    path: '/assessments/',
    component: AssessmentsByProject,
    meta: {
      title: () => BASE_TITLE + ' - Assessments by Project',
    },
  },
  {
    // One route record for list, detail and edit, so that selecting a row
    // swaps the pane without remounting the whole page.
    path: '/selections/user/:builder_id?/:mode(edit)?',
    component: SelectionsPage,
    meta: {
      title: (route) =>
        BASE_TITLE +
        (route.params.mode === 'edit'
          ? ' - Edit Selection'
          : ' - My Selections'),
    },
  },
  {
    path: '/selections/new',
    component: NewSelectionPage,
    meta: {
      title: () => BASE_TITLE + ' - New Selection',
    },
  },
  {
    path: '/selections/combinator',
    component: CombinatorPage,
    meta: {
      title: () => BASE_TITLE + ' - New Combinator Selection',
    },
  },
  {
    path: '/selections/combinator/:builder_id',
    component: CombinatorPage,
    meta: {
      title: () => BASE_TITLE + ' - Edit Combinator Selection',
    },
  },
  // The per-type create pages were unified into /selections/new; old URLs
  // redirect with the source preselected.
  ...['simple', 'sparql', 'petscan', 'wikiproject'].map((source) => ({
    path: `/selections/${source}`,
    redirect: { path: '/selections/new', query: { source } },
  })),
  // The per-type edit pages are superseded by the detail pane editor.
  ...['simple', 'sparql', 'petscan', 'wikiproject'].map((source) => ({
    path: `/selections/${source}/:builder_id`,
    redirect: (to) => `/selections/user/${to.params.builder_id}/edit`,
  })),
  {
    path: '/selections/:builder_id/zim',
    component: ZimPage,
    meta: {
      title: () => BASE_TITLE + ' - ZIM file',
    },
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { left: 0, top: 0 };
    }
  },
});

router.beforeEach((to, from, next) => {
  document.title = to.meta.title(to);
  next();
});

createApp(App).use(router).mount('#root');
