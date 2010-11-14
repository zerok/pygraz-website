function(doc) {
  if (typeof doc.next_version !== 'undefined' && doc.next_version !== null)
  emit(doc.root_id, doc);
}
