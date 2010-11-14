function(doc) {
  if (doc.doc_type === 'user' && typeof doc.openids !== 'undefined'){
    doc.openids.forEach(function(oid){emit(oid, doc)});
  }
}
