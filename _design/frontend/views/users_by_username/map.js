function(doc) {
  if (doc.doc_type === 'user' && typeof doc.openids !== 'undefined'){
    emit(doc.username, doc);
  }
}
