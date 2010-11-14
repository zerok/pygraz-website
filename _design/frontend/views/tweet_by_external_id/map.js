function(doc) {
  if (doc.doc_type === 'tweet')
  emit(doc.external_id, doc);
}
