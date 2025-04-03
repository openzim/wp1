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
import ExpiredZim from './components/ExpiredZim.vue';

Vue.config.productionTip = false;

Vue.use(VueRouter);

const BASE_TITLE = 'Wikipedia 1.0 Server';

const routes = [
  { path: '/', component: IndexPage, meta: { title: () => BASE_TITLE } },
  { path: '/update/', component: UpdatePage, meta: { title: () => BASE_TITLE + ' - Manual Update' } },
  { path: '/project/:projectName', component: ProjectPage, meta: { title: (route) => BASE_TITLE + ' - ' + route.params.projectName } },
  { path: '/compare/', component: ComparePage, meta: { title: () => BASE_TITLE + ' - Comparing projects' } },
  { path: '/selections/user', component: MyLists, meta: { title: () => BASE_TITLE + ' - My Selections' } },
  { path: '/selections/simple', component: SimpleBuilder, meta: { title: () => BASE_TITLE + ' - Create Simple Selection' } },
  { path: '/selections/sparql', component: SparqlBuilder, meta: { title: () => BASE_TITLE + ' - Create SPARQL Selection' } },
  { path: '/selections/petscan', component: PetscanBuilder, meta: { title: () => BASE_TITLE + ' - Create Petscan Selection' } },
  { path: '/selections/book', component: BookBuilder, meta: { title: () => BASE_TITLE + ' - Create Book Selection' } },
  { path: '/selections/wikiproject', component: WikiProjectBuilder, meta: { title: () => BASE_TITLE + ' - Edit WikiProject Selection' } },
  { path: '/selections/:builder_id/zim', component: ZimFile, meta: { title: () => BASE_TITLE + ' - ZIM file' } },
  { path: '/expired-zim', component: ExpiredZim, meta: { title: () => BASE_TITLE + ' - ZIM Expired' } },
];

const router = new VueRouter({
  mode: 'history',
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition;
    return { x: 0, y: 0 };
  },
});


async function checkZimFileExpiration() {
  const zimUrl = 'https://s3.wasabisys.com/zim-storage/latest.zim'; 
  try {
    const response = await fetch(zimUrl, { method: 'HEAD' });
    if (!response.ok) {
      console.warn('ZIM file not found, redirecting to /expired-zim'); 
      router.push('/expired-zim');
    } else {
      console.log('ZIM file is available'); 
    }
  } catch (error) {
    console.error('Error checking ZIM file:', error);
    router.push('/expired-zim');
  }
}


router.beforeEach(async (to, from, next) => {
  console.log(`Navigating to: ${to.path}`); 
  document.title = to.meta.title(to);
  
  if (to.path !== '/expired-zim') {
    await checkZimFileExpiration(); 
  }
  
  next();
});

new Vue({
  el: '#app',
  router,
  render: (h) => h(App),
  components: { App },
});
