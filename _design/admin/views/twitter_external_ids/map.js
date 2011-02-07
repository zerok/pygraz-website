function(doc) {
  if (doc.doc_type === 'tweet') {
    emit(null, doc.external_id);
  }
}
