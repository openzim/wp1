<template>
  <div>
    <pulse-loader
      class="loader"
      :loading="loading"
      :color="loaderColor"
      :size="loaderSize"
    ></pulse-loader>
    <table v-if="tableData">
      <th :colspan="tableData.total_cols">
        <a :href="'#/project/' + currentProject + '/articles'">{{
          tableData.title
        }}</a>
      </th>
      <tr>
        <th class="quality" rowspan="2">Quality</th>
        <th
          v-if="!tableData.is_single_col"
          class="importance"
          :colspan="tableData.total_cols - 1"
        >
          Importance
        </th>
      </tr>
      <tr>
        <th
          v-for="col in tableData.ordered_cols"
          :class="getClass(tableData.col_labels[col])"
          :key="col"
        >
          <WikiLink
            v-if="tableData.col_labels[col].href"
            :href="tableData.col_labels[col].href"
            :text="tableData.col_labels[col].text"
          ></WikiLink>
          <span v-if="!tableData.col_labels[col].href">{{
            tableData.col_labels[col]
          }}</span>
        </th>
        <th class="total">Total</th>
      </tr>

      <tr />
      <tr v-for="row in tableData.ordered_rows" :key="row">
        <th :class="getClass(tableData.row_labels[row])">
          <span v-if="tableData.row_labels[row].text == 'FA'">
            <img
              alt="Featured list"
              src="//upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Featured_article_star.svg/16px-Featured_article_star.svg.png"
              decoding="async"
              width="16"
              height="16"
              srcset="
                //upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Featured_article_star.svg/24px-Featured_article_star.svg.png 1.5x,
                //upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Featured_article_star.svg/32px-Featured_article_star.svg.png 2x
              "
              data-file-width="180"
              data-file-height="180"
              style="position: relative; top: -2px"
            />
          </span>
          <span v-if="tableData.row_labels[row].text == 'GA'">
            <img
              alt=""
              src="//upload.wikimedia.org/wikipedia/en/thumb/9/94/Symbol_support_vote.svg/16px-Symbol_support_vote.svg.png"
              decoding="async"
              title="Good article"
              width="16"
              height="16"
              srcset="
                //upload.wikimedia.org/wikipedia/en/thumb/9/94/Symbol_support_vote.svg/24px-Symbol_support_vote.svg.png 1.5x,
                //upload.wikimedia.org/wikipedia/en/thumb/9/94/Symbol_support_vote.svg/32px-Symbol_support_vote.svg.png 2x
              "
              data-file-width="180"
              data-file-height="185"
              style="position: relative; top: -2px"
            />
          </span>
          <WikiLink
            v-if="tableData.row_labels[row].href"
            :href="tableData.row_labels[row].href"
            :text="tableData.row_labels[row].text"
          ></WikiLink>
          <span v-if="!tableData.row_labels[row].href">
            {{ tableData.row_labels[row] }}
          </span>
        </th>
        <td v-for="col in tableData.ordered_cols" :key="col">
          <span v-if="tableData.data[row][col]">
            <router-link
              :to="{
                path: `/project/${currentProject}/articles`,
                query: { quality: row, importance: col },
              }"
              >{{ tableData.data[row][col] }}</router-link
            >
          </span>
        </td>
        <td>
          <router-link
            :to="{
              path: `/project/${currentProject}/articles`,
              query: { quality: row },
            }"
            >{{ tableData.row_totals[row] }}</router-link
          >
        </td>
      </tr>

      <tr />
      <tr>
        <td>Total</td>
        <td v-for="col in tableData.ordered_cols" :key="col">
          <router-link
            :to="{
              path: `/project/${currentProject}/articles`,
              query: { importance: col },
            }"
            >{{ tableData.col_totals[col] }}</router-link
          >
        </td>
        <td>
          {{ tableData.total }}
        </td>
      </tr>
    </table>
  </div>
</template>

<script>
import WikiLink from './WikiLink.vue';
import PulseLoader from 'vue-spinner/src/PulseLoader.vue';

export default {
  name: 'project-table',
  components: {
    WikiLink,
    PulseLoader,
  },
  props: {
    projectId: String,
  },
  data: function () {
    return {
      tableData: null,
      loading: false,
      loaderColor: '#007bff',
      loaderSize: '1rem',
    };
  },
  computed: {
    currentProject: function () {
      if (!this.projectId) {
        return null;
      }
      return this.projectId.replace(/_/g, ' ');
    },
  },
  watch: {
    projectId: async function (projectId) {
      this.tableData = null;
      if (!projectId) {
        return;
      }

      this.loading = true;
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/projects/${projectId}/table`
      );
      const json = await response.json();
      this.loading = false;

      this.tableData = json.table_data;
    },
  },
  methods: {
    getClass: function (cls) {
      if (cls.text) {
        return cls.text;
      }
      return cls;
    },
  },
};
</script>

<style scoped>
@import '../labels.scss';

.loader {
  margin: auto;
  text-align: center;
}

table {
  border-collapse: collapse;
  border: 1px solid #aaa;
  margin: auto;
  text-align: right;
}

th {
  border: 1px solid #aaa;
  padding-left: 0.5rem;
  padding-right: 0.5rem;
  text-align: center;
}

th a {
  color: #000;
}

td {
  border: 1px solid #aaa;
  padding-left: 0.5rem;
  padding-right: 0.5rem;
}

.table-link {
  color: #006fe6;
  cursor: pointer;
}

.quality {
  vertical-align: bottom;
}
</style>
