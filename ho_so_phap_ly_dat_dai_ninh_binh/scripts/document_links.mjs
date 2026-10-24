// Keep report navigation in place; open sources and document files separately.
export function openDocumentsInNewTab(html) {
  return html.replace(/<a\b[^>]*>/g, tag => {
    const href = tag.match(/\bhref="([^"]*)"/)?.[1] || '';
    const documentLink = /^(?:https?:\/\/|(?:\.\.\/)*(?:documents|reports|data)\/)/i.test(href)
      || /\.(?:pdf|docx?|xlsx?|csv|json|md|txt)(?:[?#]|$)/i.test(href);
    if (!documentLink) return tag;
    return tag.replace(/\s(?:target|rel)="[^"]*"/g, '').replace(/>$/, ' target="_blank" rel="noopener noreferrer">');
  });
}
