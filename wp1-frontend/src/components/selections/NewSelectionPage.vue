<template>
  <div class="wp1r flex flex-1 flex-col bg-page">
    <div
      class="mx-auto flex w-full max-w-[1200px] flex-1 flex-col border-x border-border bg-surface"
    >
      <div v-if="!isLoggedIn" class="mx-auto w-full max-w-[760px]">
        <SelectionsNullState mode="signed-out" />
      </div>
      <div v-else class="grid flex-1 md:grid-cols-[264px_minmax(0,1fr)]">
        <!-- ============ Source picker ============ -->
        <div
          class="flex flex-col gap-1 border-b border-border-strong px-3.5 pb-3.5 pt-6 md:border-b-0 md:border-r"
        >
          <div class="wp1r-microlabel mb-1">Source</div>
          <button
            v-for="option in sources"
            :key="option.key"
            :id="'source-' + option.key"
            type="button"
            class="flex w-full cursor-pointer flex-col items-start gap-0.5 rounded border border-solid px-2.5 py-2 text-left"
            :class="
              source === option.key
                ? 'border-accent-border bg-accent-tint'
                : 'border-transparent bg-transparent hover:bg-surface-muted'
            "
            @click="pickSource(option.key)"
          >
            <span
              class="text-[13.5px]"
              :class="
                source === option.key
                  ? 'font-semibold text-accent-hover'
                  : 'font-medium text-ink'
              "
              >{{ option.label }}</span
            >
            <span
              class="text-xs leading-[1.4]"
              :class="source === option.key ? 'text-ink-2' : 'text-ink-3'"
              >{{ option.blurb }}</span
            >
          </button>
        </div>

        <!-- ============ Form ============ -->
        <form
          class="flex min-w-0 max-w-[780px] flex-col gap-4 px-5 pb-[18px] pt-6"
          @submit.prevent="onSubmit"
        >
          <div>
            <h1 class="m-0 text-[19px] font-semibold tracking-[-0.015em]">
              {{ title }}
            </h1>
            <p class="mb-0 mt-1.5 text-[13.5px] leading-[1.5] text-ink-2">
              {{ currentSource.description }}
              <a
                href="https://wp1.readthedocs.io/en/latest/user/selections/"
                target="_blank"
                rel="noopener noreferrer"
                >Documentation</a
              >
            </p>
          </div>

          <div class="grid gap-3.5 sm:grid-cols-2">
            <div id="project">
              <label
                for="project-select"
                class="mb-1 block text-xs font-medium text-ink-2"
                >Project</label
              >
              <select
                id="project-select"
                v-model="project"
                class="wp1r-select h-8 w-full"
              >
                <option v-for="site in projectOptions" :key="site">
                  {{ site }}
                </option>
              </select>
            </div>
            <div id="listName">
              <label
                for="name-input"
                class="mb-1 block text-xs font-medium text-ink-2"
                >Selection name</label
              >
              <input
                id="name-input"
                v-model="name"
                type="text"
                class="wp1r-input h-8 w-full"
                placeholder="My selection"
              />
            </div>
          </div>

          <!-- Source-specific field -->
          <div v-if="source === 'simple'" id="items">
            <label
              for="articles"
              class="mb-1 block text-xs font-medium text-ink-2"
              >Articles
              <span class="ml-1 font-mono text-[11px] font-normal text-ink-4"
                >one title per line</span
              ></label
            >
            <textarea
              id="articles"
              v-model="articles"
              rows="9"
              class="wp1r-input w-full py-2 font-mono text-[12.5px] leading-[1.6]"
              style="resize: vertical"
              :placeholder="simplePlaceholder"
            ></textarea>
          </div>

          <div v-else-if="source === 'sparql'" id="items">
            <label for="query" class="mb-1 block text-xs font-medium text-ink-2"
              >Query
              <span class="ml-1 font-mono text-[11px] font-normal text-ink-4"
                >must return ?article</span
              ></label
            >
            <textarea
              id="query"
              v-model="query"
              rows="9"
              class="wp1r-input w-full py-2 font-mono text-[12.5px] leading-[1.6]"
              style="resize: vertical"
              :placeholder="sparqlPlaceholder"
            ></textarea>
            <div class="mt-2">
              <button
                id="toggleUpdateQuery"
                type="button"
                class="cursor-pointer border-0 bg-transparent p-0 text-[12.5px] text-accent"
                @click="showSparqlImport = !showSparqlImport"
              >
                {{ showSparqlImport ? '▾' : '▸' }} Import from a Wikidata Query
                URL
              </button>
              <div v-if="showSparqlImport" class="mt-2 flex gap-2">
                <input
                  id="updateQueryInput"
                  v-model="sparqlImportUrl"
                  type="text"
                  class="wp1r-input h-8 flex-1 font-mono text-xs"
                  placeholder="https://query.wikidata.org/#%23Goats%0ASELECT…"
                />
                <button
                  id="updateQuery"
                  type="button"
                  class="wp1r-btn-secondary h-8 px-3"
                  @click="importSparqlUrl"
                >
                  Update
                </button>
              </div>
              <p
                v-if="sparqlImportError"
                class="mb-0 mt-1.5 text-[12.5px] text-danger"
              >
                Could not extract a SPARQL query from that URL. Make sure it is
                a URL from query.wikidata.org.
              </p>
            </div>
          </div>

          <div v-else-if="source === 'petscan'" id="items">
            <label
              for="petscan-url"
              class="mb-1 block text-xs font-medium text-ink-2"
              >Petscan URL
              <span class="ml-1 font-mono text-[11px] font-normal text-ink-4"
                >psid or full URL</span
              ></label
            >
            <input
              id="petscan-url"
              v-model="url"
              type="text"
              class="wp1r-input h-8 w-full font-mono text-[12.5px]"
              placeholder="https://petscan.wmcloud.org/?psid=28104512"
            />
          </div>

          <div v-else-if="source === 'book'" id="items">
            <label
              for="book-url"
              class="mb-1 block text-xs font-medium text-ink-2"
              >Book page
              <span class="ml-1 font-mono text-[11px] font-normal text-ink-4"
                >Book: namespace URL</span
              ></label
            >
            <input
              id="book-url"
              v-model="url"
              type="text"
              class="wp1r-input h-8 w-full font-mono text-[12.5px]"
              placeholder="https://en.wikipedia.org/wiki/Book:Trees_of_the_World"
            />
          </div>

          <div
            v-else-if="source === 'wikiproject'"
            class="flex flex-col gap-3.5"
          >
            <div id="include-items">
              <label class="mb-1 block text-xs font-medium text-ink-2"
                >WikiProjects to include
                <span class="ml-1 font-mono text-[11px] font-normal text-ink-4"
                  >at least one</span
                ></label
              >
              <ProjectAutocomplete @select="addProject(wpInclude, $event)" />
              <div
                v-if="wpInclude.length"
                id="include-projects"
                class="mt-2 flex flex-wrap gap-1.5"
              >
                <span
                  v-for="(wikiproject, i) in wpInclude"
                  :key="'include-' + i"
                  class="inline-flex items-center gap-1.5 rounded-[3px] border border-ok-border bg-ok-tint px-2 py-1 text-[12.5px]"
                >
                  {{ wikiproject }}
                  <button
                    type="button"
                    class="cursor-pointer border-0 bg-transparent p-0 leading-none text-ink-4 hover:text-danger"
                    :aria-label="'Remove ' + wikiproject"
                    @click="wpInclude.splice(i, 1)"
                  >
                    ×
                  </button>
                </span>
              </div>
            </div>
            <div id="exclude-items">
              <label class="mb-1 block text-xs font-medium text-ink-2"
                >WikiProjects to exclude
                <span class="ml-1 font-mono text-[11px] font-normal text-ink-4"
                  >optional</span
                ></label
              >
              <ProjectAutocomplete @select="addProject(wpExclude, $event)" />
              <div
                v-if="wpExclude.length"
                id="exclude-projects"
                class="mt-2 flex flex-wrap gap-1.5"
              >
                <span
                  v-for="(wikiproject, i) in wpExclude"
                  :key="'exclude-' + i"
                  class="inline-flex items-center gap-1.5 rounded-[3px] border border-danger-border bg-danger-tint px-2 py-1 text-[12.5px]"
                >
                  {{ wikiproject }}
                  <button
                    type="button"
                    class="cursor-pointer border-0 bg-transparent p-0 leading-none text-ink-4 hover:text-danger"
                    :aria-label="'Remove ' + wikiproject"
                    @click="wpExclude.splice(i, 1)"
                  >
                    ×
                  </button>
                </span>
              </div>
            </div>
          </div>

          <!-- Validation errors -->
          <div v-if="errors" id="invalid_articles">
            <div class="text-[13px] text-danger">{{ errors }}</div>
            <textarea
              v-if="invalidItems"
              class="wp1r-input mt-2 w-full !border-danger-border bg-danger-tint py-2 font-mono text-[12.5px]"
              rows="5"
              readonly
              :value="invalidItems"
            ></textarea>
          </div>

          <!-- Action row -->
          <div class="mt-auto flex items-center gap-2.5">
            <button
              id="saveListButton"
              type="submit"
              class="wp1r-btn-primary h-8 px-3.5"
              :disabled="processing"
            >
              {{ processing ? 'Saving…' : 'Save selection' }}
            </button>
            <span v-if="liveNote" class="text-[12.5px] text-ink-3">{{
              liveNote
            }}</span>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import ProjectAutocomplete from './ProjectAutocomplete.vue';
import SelectionsNullState from './SelectionsNullState.vue';
import { loginStore } from '../../store.js';
import { SOURCES } from '../../lib/selections.js';

const SOURCE_CONFIG = {
  simple: {
    titleNoun: 'simple',
    model: 'wp1.selection.models.simple',
    description:
      'Paste the exact titles of the articles you want, one per line. Blank ' +
      'lines and comments starting with # are ignored.',
  },
  sparql: {
    titleNoun: 'SPARQL',
    model: 'wp1.selection.models.sparql',
    description:
      'A SPARQL query run against Wikidata that returns Wikipedia articles. ' +
      'Enter it directly or import it from a query service URL.',
  },
  petscan: {
    titleNoun: 'Petscan',
    model: 'wp1.selection.models.petscan',
    description:
      'A saved Petscan query, referenced by its PSID or full URL. The query ' +
      'is re-run every time the selection rebuilds.',
  },
  book: {
    titleNoun: 'book',
    model: 'wp1.selection.models.book',
    description: 'Every article listed in a Wikipedia book page.',
  },
  wikiproject: {
    titleNoun: 'WikiProject',
    model: 'wp1.selection.models.wikiproject',
    description:
      'Every article assessed by the WikiProjects you choose. English ' +
      'Wikipedia only.',
  },
};

export default {
  name: 'NewSelectionPage',
  components: { ProjectAutocomplete, SelectionsNullState },
  data: function () {
    return {
      source: this.initialSource(),
      name: '',
      project: 'en.wikipedia.org',
      sites: [],
      articles: '',
      query: '',
      url: '',
      wpInclude: [],
      wpExclude: [],
      showSparqlImport: false,
      sparqlImportUrl: '',
      sparqlImportError: false,
      processing: false,
      errors: '',
      invalidItems: '',
      simplePlaceholder:
        'Eiffel_Tower\nStatue_of_Liberty\nFreedom_Monument_(Baghdad)\n\n' +
        '# comments and blank lines are ignored\n',
      sparqlPlaceholder:
        '#Rock bands that start with "M"\n' +
        'SELECT ?band ?bandLabel ?article\n' +
        'WHERE\n' +
        '{\n' +
        '  ?band wdt:P31 wd:Q5741069 .\n' +
        '  ?band rdfs:label ?bandLabel .\n' +
        '  { ?article schema:about ?band. ' +
        '?article schema:isPartOf <https://en.wikipedia.org/>. }\n' +
        '  FILTER(LANG(?bandLabel) = "en") .\n' +
        "  FILTER(STRSTARTS(?bandLabel, 'M')) .\n}",
    };
  },
  computed: {
    isLoggedIn: function () {
      return loginStore.isLoggedIn;
    },
    sources: function () {
      return SOURCES;
    },
    currentSource: function () {
      return SOURCE_CONFIG[this.source] || SOURCE_CONFIG.simple;
    },
    title: function () {
      return `New ${this.currentSource.titleNoun} selection`;
    },
    projectOptions: function () {
      if (this.source === 'wikiproject') {
        return ['en.wikipedia.org'];
      }
      return this.sites.length ? this.sites : ['en.wikipedia.org'];
    },
    liveNote: function () {
      if (this.source === 'simple') {
        const n = this.articles
          .split('\n')
          .filter((line) => line.trim() && !line.trim().startsWith('#')).length;
        return `${n} title${n === 1 ? '' : 's'} detected`;
      }
      if (this.source === 'petscan') {
        return 'Re-run on every build';
      }
      if (this.source === 'wikiproject') {
        const n = this.wpInclude.length;
        return `${n} WikiProject${n === 1 ? '' : 's'} included`;
      }
      return '';
    },
  },
  watch: {
    '$route.query.source': function () {
      const source = this.initialSource();
      if (source !== this.source) {
        this.source = source;
      }
    },
    source: function () {
      if (this.source === 'wikiproject') {
        this.project = 'en.wikipedia.org';
      }
      this.errors = '';
      this.invalidItems = '';
    },
  },
  created: async function () {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/sites/`);
    if (response.ok) {
      const data = await response.json();
      this.sites = data.sites;
    }
  },
  methods: {
    initialSource: function () {
      const requested = this.$route.query.source;
      if (
        requested &&
        (SOURCE_CONFIG[requested] || requested === 'combinator')
      ) {
        return requested === 'combinator' ? 'simple' : requested;
      }
      return 'simple';
    },
    pickSource: function (key) {
      if (key === 'combinator') {
        // The combinator has its own full-width builder.
        this.$router.push('/selections/combinator');
        return;
      }
      this.source = key;
      if (this.$route.query.source !== key) {
        this.$router.replace({
          path: '/selections/new',
          query: { source: key },
        });
      }
    },
    addProject: function (list, project) {
      if (!list.includes(project)) {
        list.push(project);
      }
    },
    importSparqlUrl: function () {
      this.sparqlImportError = false;
      const url = this.sparqlImportUrl;
      if (url.indexOf('wikidata.org') === -1) {
        this.sparqlImportError = true;
        return;
      }
      const parts = url.split('#');
      if (parts.length < 2) {
        this.sparqlImportError = true;
        return;
      }
      this.query = unescape(parts[1]);
    },
    validate: function () {
      if (!this.name.trim()) {
        return 'Please provide a selection name.';
      }
      switch (this.source) {
        case 'simple':
          if (!this.articles.trim()) {
            return 'Please provide at least one article title.';
          }
          break;
        case 'sparql':
          if (!this.query.trim()) {
            return 'Please provide a query.';
          }
          break;
        case 'petscan':
          if (!this.url.trim()) {
            return 'Please provide a Petscan URL.';
          }
          break;
        case 'book':
          if (!this.url.trim()) {
            return 'Please provide a book page URL.';
          }
          break;
        case 'wikiproject':
          if (this.wpInclude.length === 0) {
            return 'Please provide at least one WikiProject to include.';
          }
          break;
      }
      return null;
    },
    buildParams: function () {
      switch (this.source) {
        case 'simple':
          return { list: this.articles.split('\n') };
        case 'sparql':
          return { query: this.query };
        case 'petscan':
        case 'book':
          return { url: this.url };
        case 'wikiproject':
          return { include: [...this.wpInclude], exclude: [...this.wpExclude] };
      }
      return {};
    },
    onSubmit: async function () {
      this.errors = '';
      this.invalidItems = '';
      const problem = this.validate();
      if (problem) {
        this.errors = problem;
        return;
      }

      this.processing = true;
      let response = null;
      try {
        response = await fetch(`${import.meta.env.VITE_API_URL}/builders/`, {
          headers: { 'Content-Type': 'application/json' },
          method: 'post',
          credentials: 'include',
          body: JSON.stringify({
            name: this.name,
            project: this.project,
            model: this.currentSource.model,
            params: this.buildParams(),
          }),
        });
      } catch (e) {
        this.processing = false;
        this.errors = 'A network error has occurred.';
        return;
      }
      this.processing = false;

      if (!response.ok) {
        this.errors = 'An unknown server error has occurred.';
        return;
      }

      const data = await response.json();
      if (data.success) {
        this.$router.push(`/selections/user/${data.id}`);
        return;
      }
      this.errors = data.items.errors.join(', ');
      this.invalidItems = (data.items.invalid || []).join('\n');
    },
  },
};
</script>
