function(doc) {
  if (doc.doc_type === 'session')
  emit(doc.topic, doc);
}
