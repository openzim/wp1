<!-- The featured-star / GA / A-class icons that Wikipedia renders next to
     assessment-class labels. Renders nothing for classes without an icon. -->
<template>
  <img
    v-if="icon"
    :alt="icon.alt"
    :title="icon.title"
    :src="icon.src"
    :srcset="icon.srcset"
    decoding="async"
    :width="size"
    :height="size"
    class="mr-1 inline-block align-[-2px]"
  />
</template>

<script>
const STAR = {
  alt: 'Star icon',
  src: '//upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Featured_article_star.svg/20px-Featured_article_star.svg.png',
  srcset:
    '//upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Featured_article_star.svg/40px-Featured_article_star.svg.png 2.5x, //upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Featured_article_star.svg/60px-Featured_article_star.svg.png 3.75x',
};

const ICONS = {
  FA: { ...STAR, title: 'Featured article' },
  FL: { ...STAR, title: 'Featured list' },
  FM: { ...STAR, title: 'Featured media' },
  GA: {
    alt: 'Green plus icon on white circle with green border',
    title: 'Good article',
    src: '//upload.wikimedia.org/wikipedia/commons/thumb/9/94/Symbol_support_vote.svg/20px-Symbol_support_vote.svg.png',
    srcset:
      '//upload.wikimedia.org/wikipedia/commons/thumb/9/94/Symbol_support_vote.svg/40px-Symbol_support_vote.svg.png 2.5x, //upload.wikimedia.org/wikipedia/commons/thumb/9/94/Symbol_support_vote.svg/60px-Symbol_support_vote.svg.png 3.75x',
  },
  A: {
    alt: 'Light blue capital letter A over pale yellow star icon in white circle with light blue border',
    title: 'A-Class',
    src: '//upload.wikimedia.org/wikipedia/commons/thumb/2/25/Symbol_a_class.svg/20px-Symbol_a_class.svg.png',
    srcset:
      '//upload.wikimedia.org/wikipedia/commons/thumb/2/25/Symbol_a_class.svg/40px-Symbol_a_class.svg.png 2.5x, //upload.wikimedia.org/wikipedia/commons/thumb/2/25/Symbol_a_class.svg/60px-Symbol_a_class.svg.png 3.75x',
  },
};

export default {
  name: 'class-icon',
  props: {
    // Class label text, e.g. 'FA', 'GA'.
    label: String,
    size: { type: Number, default: 14 },
  },
  computed: {
    icon: function () {
      return ICONS[this.label] || null;
    },
  },
};
</script>
