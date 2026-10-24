export default class {
  data() { return { permalink: '/assets/search-index.json', eleventyExcludeFromCollections: true }; }
  render(data) { return JSON.stringify(data.research.search); }
}
